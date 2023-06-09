"""
Views for the user API.
"""
from django.utils import timezone
from django.contrib.auth import login
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

from rest_framework.serializers import DateTimeField
from rest_framework import (
    generics,
    permissions,
    status,
    response,
    viewsets,
    permissions,
)


from knox.settings import knox_settings
from knox.auth import TokenAuthentication
from knox.views import (
    LoginView as KnoxLoginView,
    LogoutView as KnoxLogoutView,
    LogoutAllView as KnoxLogoutAllView
)

from drf_spectacular.utils import extend_schema

from core.schemes import KnoxTokenScheme
from core.models import (
    ResetPasswordToken,
    VerificationToken,
)

from user.serializers import (
    UserSerializer,
    UserMinimalSerializer,
    UserLoginSerializer,
    ResetPasswordSerializer,
)

from core.tasks import send_reset_password_email

class UserViewSet(viewsets.ModelViewSet):
    """Viewset for users."""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def list(self, request, *args, **kwargs):
        """List all users filtered by is_active, email, and is_superuser."""
        try:
            is_active = request.query_params.get('is_active', None)
            email = request.query_params.get('email', None)
            is_superuser = request.query_params.get('is_superuser', None)

            queryset = self.queryset

            if is_active is not None:
                is_active = False if is_active.lower().strip() != 'true' else True
                queryset = queryset.filter(is_active=is_active)

            if email is not None:
                queryset = queryset.filter(email=email)

            if is_superuser is not None:
                is_superuser = False if is_superuser.lower().strip() != 'true' else True
                queryset = queryset.filter(is_superuser=is_superuser)

            serializer = UserMinimalSerializer(queryset, many=True)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, Http404):
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a user by id."""
        try:
            instance = self.get_object()
            serializer = UserMinimalSerializer(instance)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, Http404):
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Set a user as active/inactive."""
        try:
            instance = self.get_object()

            # Remove superuser status if user is being deactivated
            if instance.is_active and instance.is_superuser:
                instance.is_superuser = False

            instance.is_active = not instance.is_active
            instance.save()
            return response.Response(status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, Http404):
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class LoginView(KnoxLoginView):
    """Authenticate a user and return a token."""
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserLoginSerializer

    def get_user_serializer_class(self):
        return UserMinimalSerializer

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        user.last_login = timezone.now()
        user.save()
        return super(LoginView, self).post(request, format=None)


@extend_schema(request=None, responses=None)
class LogoutView(KnoxLogoutView):
    """Logout a user."""
    pass


@extend_schema(request=None, responses=None)
class LogoutAllView(KnoxLogoutAllView):
    """Logout user from all devices."""
    pass


class ResetPasswordView(generics.GenericAPIView):
    """Reset password for a user."""
    permission_classes = (permissions.AllowAny,)
    serializer_class = ResetPasswordSerializer

    def get_context(self):
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def get_token_limit_per_user(self):
        return knox_settings.TOKEN_LIMIT_PER_USER

    def get_expiry_datetime_format(self):
        return knox_settings.EXPIRY_DATETIME_FORMAT

    def format_expiry_datetime(self, expiry):
        datetime_format = self.get_expiry_datetime_format()
        return DateTimeField(format=datetime_format).to_representation(expiry)

    def create_token(self, user):
        instance, token = ResetPasswordToken.objects.create(
            user=user,
        )

        return instance, token

    def post(self, request, format=None):
        email = request.data.get('email')
        if email is None:
            return response.Response({'email': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()

        try:
            user = User.objects.get(email=email)

            if not user.is_active or not user.is_verified:
                raise ObjectDoesNotExist

            instance, token = self.create_token(user)

            if instance and token:
                send_reset_password_email.delay(instance.user.name, instance.user.last_name, instance.user.email, token)


            data = {'msg': 'Password reset email sent.',}
            return response.Response(data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return response.Response({'email': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


