import { useState } from "react";
import reactLogo from "./assets/react.svg";
import axolote from "./assets/axolote.png";
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./Login";
import Register from "./Register";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="w-screen h-full">
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
