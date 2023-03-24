import { useState } from 'react'
import scum from './assets/esCUM.png'
import pendejolote from './assets/axolote.png'
import ipene from './assets/ipn.png'

import './App.css'
import { Link } from 'react-router-dom'


function Login() {
  const [count, setCount] = useState(0)

  return (
    <div className="w-screen h-screen">
      <div className='flex flex-row h-screen'>
      <div className='w-full m-4 border-t-4 border-b-4 border-sky-500'>
        <div className='w-full p-4 flex flex-row justify-between items-center bg-sky-500'>
          <img className='w-20 h-full' src={scum} alt="" />
    <h1 className='w-full text-center font-sans text-md font-light pb-5 text-white'>Bienvenido al sistema OMET</h1>
          <img className='w-14 h-full' src={ipene} alt="" />
        </div>
    <img className='m-auto h-36 mt-6' src={pendejolote} alt="" />
      <div className='flex flex-col items-center m-auto w-2/3'>
    <form className='w-auto flex flex-col m-4 justify-center'>
      <input className='w-64 my-2 text-gray-400 py-2 px-4 rounded-full bg-white border' placeholder='Usuario:'  type="text" id="username" name="username"/><br/><br/>
      <input className='w-64 my-2 text-gray-400 py-2 px-4 rounded-full bg-white border' placeholder='Contraseña:' type="password" id="password" name="password"/><br/><br/>
      <p className='text-xs m-2'>¿Olvidaste tu contraseña? <a className='text-cyan-700' href="#">Restaurar contraseña</a></p>
      <input className='my-5 text-white  py-2 px-4 rounded-full bg-cyan-700 mx-auto hover:bg-cyan-400 hover:cursor-pointer' type="submit" value="Iniciar sesión"/><br/><br/>
    </form>
    <p className='text-sm pb-8'>¿Aún no tienes cuenta? <Link className='text-cyan-700' to={'/register'}>Registrarse</Link></p>
      </div>
    
      </div>
      </div>
      
    </div>
  )
}

export default Login
