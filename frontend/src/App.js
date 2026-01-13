import React from "react";
import ChatBot from "./components/ChatBot";
import "./App.css";

function App() {
  return (
    <div className="App">
      <nav className="navbar">
        <div className="navbar-container">
          <h1 className="navbar-title">Chatbot Diabetes - Predictor de Insulina</h1>
        </div>
      </nav>

      <div className="content">
        <ChatBot />
      </div>

      <footer className="app-footer">
        <p>Recuerda siempre consultar con tu medico antes de tomar cualquier decision sobre tu medicacion.</p>
      </footer>
    </div>
  );
}

export default App;
