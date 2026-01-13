import React, { useState, useRef, useEffect } from "react";
import "../styles/ChatBot.css";

function ChatBot() {
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      text: "¡Hola! Bienvenido al asistente de diabetes.\n\nAntes de comenzar, ¿cual es tu nombre?", 
      sender: "bot" 
    }
  ]);
  const [input, setInput] = useState("");
  const [patientName, setPatientName] = useState("");
  const [patientAge, setPatientAge] = useState(null);
  const [userDetails, setUserDetails] = useState({
    name: "",
    exercise_minutes: 0,
    carbohydrates: 0,
    protein: 0,
    fats: 0,
    glucose: 0,
  });
  const [step, setStep] = useState(0); // 0: pidiendo nombre, 1: pidiendo edad, 2: esperando input, 8: resultado
  const [predictedDose, setPredictedDose] = useState(null);
  const [interactionMode, setInteractionMode] = useState("combined");
  const messagesEnd = useRef(null);

  const scrollToBottom = () => {
    messagesEnd.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { id: messages.length + 1, text: input, sender: "user" };
    setMessages([...messages, userMessage]);
    let botResponse = "";
    let newStep = step;

    // Paso 0: Capturar nombre del paciente
    if (step === 0) {
      setPatientName(input);
      // Verificar si el paciente ya existe
      try {
        const response = await fetch(`http://localhost:5000/patients/${input}`);
        const data = await response.json();
        
        if (data.success && data.patient) {
          // Paciente existe, usar su edad guardada
          setPatientAge(data.patient.age);
          botResponse = `¡Bienvenido de vuelta, ${input}! Cuéntame sobre tu día de hoy.\n\nEjemplo: 'Hice 20 min de ejercicio, comí pan y mi glucosa es 95'`;
          newStep = 2; // Saltar directamente a paso 2 (predicción)
        } else {
          // Paciente nuevo, pedir edad
          botResponse = `Mucho gusto, ${input}! Ahora, ¿cuantos anos tienes?`;
          newStep = 1;
        }
      } catch (error) {
        // Error de conexión, pedir edad de todas formas
        console.error(error);
        botResponse = `Mucho gusto, ${input}! Ahora, ¿cuantos anos tienes?`;
        newStep = 1;
      }
    }
    // Paso 1: Capturar edad
    else if (step === 1) {
      const age = parseInt(input);
      if (isNaN(age) || age < 1 || age > 150) {
        botResponse = "Por favor, ingresa una edad valida (entre 1 y 150 anos).";
        newStep = 1;
      } else {
        setPatientAge(age);
        botResponse = `Perfecto! Tienes ${age} anos. Ahora cuéntame sobre tu día.\n\nEjemplo: 'Hice 20 min de ejercicio, comí pan y mi glucosa es 95'\n\nTambién puedo responder preguntas: '¿Qué alimentos puedo comer?' o '¿Cuáles son los síntomas?'`;
        newStep = 2;
      }
    }
    // Paso 2: Detecta si es predicción o pregunta general
    else if (step === 2) {
      // Detectar tipo de entrada
      const lowerInput = input.toLowerCase();
      const isQuestion = lowerInput.includes('?') || 
                        lowerInput.match(/^(qué|cuál|cuáles|cuándo|cuánto|cómo|dónde|por qué|puedo|debo|es)/i);
      
      if (isQuestion) {
        // Es una pregunta general sobre diabetes
        await askQuestion(input);
      } else {
        // Es información sobre ejercicio, comida, glucosa
        await processCombinedInput(input);
      }
      newStep = 8;
    } else if (step === 8) {
      // Después de obtener resultado
      if (input.toLowerCase() === "otro" || input.toLowerCase() === "mas") {
        botResponse = `Perfecto ${patientName}, ¿cuéntame sobre tu nuevo día!`;
        newStep = 2;
      } else if (input.toLowerCase() === "salir") {
        botResponse = "¡Gracias por usar el chatbot! Recuerda siempre consultar con tu medico.";
        newStep = 8;
      } else {
        botResponse = "¿Deseas otro calculo? Escribe 'otro', 'mas' o 'salir'.";
      }
    }

    setStep(newStep);
    if (botResponse) {
      const botMessage = { id: messages.length + 2, text: botResponse, sender: "bot" };
      setMessages(prev => [...prev, botMessage]);
    }
    setInput("");
  };

  const askQuestion = async (userInput) => {
    try {
      const response = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          description: userInput,
          patient_name: patientName,
          patient_age: patientAge
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        let responseText = `<div style="font-family: Arial, sans-serif; color: #333;">
          <div style="background: #f1f8e9; border-left: 4px solid #8BC34A; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
            <strong style="color: #558b2f; font-size: 16px;">📚 Información sobre Diabetes:</strong>
            <div style="margin-top: 10px; line-height: 1.8; font-size: 14px;">
              <div style="white-space: pre-wrap; color: #333;">
                ${data.answer}
              </div>
            </div>
          </div>

          <div style="background: #fff3e0; border-left: 4px solid #FF9800; padding: 10px 15px; margin-bottom: 15px; border-radius: 4px; font-size: 12px;">
            <strong>📊 Tipo:</strong> ${data.question_type} | 
            <strong>Confianza:</strong> ${(data.confidence * 100).toFixed(0)}% | 
            <strong>Fuente:</strong> Base de datos médica
          </div>

          <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
            <strong style="color: #c62828; font-size: 14px;">⚠️ IMPORTANTE:</strong>
            <div style="margin-top: 8px; font-size: 13px; color: #555; line-height: 1.6;">
              Esta información es de carácter educativo. Siempre consulta con tu médico para diagnóstico y tratamiento.
            </div>
          </div>
        </div>`;

        const botMessage = { 
          id: messages.length + 2, 
          text: responseText, 
          sender: "bot",
          isHTML: true 
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const botMessage = { 
          id: messages.length + 2, 
          text: `No pude encontrar respuesta a tu pregunta. Intenta ser más específico.`, 
          sender: "bot" 
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error(error);
      const botMessage = { 
        id: messages.length + 2, 
        text: "Error al procesar tu pregunta. Intenta de nuevo.", 
        sender: "bot" 
      };
      setMessages(prev => [...prev, botMessage]);
    }
  };

  const processCombinedInput = async (userInput) => {
    try {
      const response = await fetch("http://localhost:5000/parse-combined", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          description: userInput,
          patient_name: patientName,
          patient_age: patientAge
        }),
      });

      const data = await response.json();
      if (data.success) {
        setPredictedDose(data.predicted_dose);
        
        let responseText = `<div style="font-family: Arial, sans-serif; color: #333;">
          <div style="background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
            <strong style="color: #2e7d32; font-size: 16px;">He interpretado tu informacion:</strong>
            <div style="margin-top: 10px; line-height: 1.8;">
              ${data.interpretations.map(line => `<div>• ${line}</div>`).join('')}
            </div>
          </div>

          <div style="background: #fff3e0; border-left: 4px solid #FF9800; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
            <strong style="color: #e65100; font-size: 18px;">PREDICCION DE DOSIS DE INSULINA</strong>
            <div style="margin-top: 10px; text-align: center;">
              <div style="font-size: 32px; color: #4CAF50; font-weight: bold; margin: 10px 0;">${data.predicted_dose} unidades</div>
              <div style="font-size: 14px; color: #666;">Rango estimado: ${data.range} unidades</div>
            </div>
          </div>

          <div style="background: #f3e5f5; border-left: 4px solid #9C27B0; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
            <strong style="color: #6a1b9a; font-size: 16px;">Analisis de tu situacion:</strong>
            <div style="margin-top: 10px; line-height: 1.8;">
              ${data.analysis.split('\n').map(line => line.trim() ? `<div>• ${line}</div>` : '').join('')}
            </div>
          </div>

          ${data.medical_context ? `
            <div style="background: #e3f2fd; border-left: 4px solid #2196F3; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
              <strong style="color: #1565c0; font-size: 16px;">Recomendaciones Medicas (RAG):</strong>
              <div style="margin-top: 10px; line-height: 1.8; font-size: 14px;">
                ${data.medical_context.split('\n').map(line => line.trim() ? `<div>• ${line}</div>` : '').join('')}
              </div>
            </div>
          ` : ''}

          <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
            <strong style="color: #c62828; font-size: 14px;">IMPORTANTE - Disclaimer:</strong>
            <div style="margin-top: 8px; font-size: 13px; color: #555; line-height: 1.6;">
              Esta prediccion se basa en los datos que proporcionaste. Siempre consulta con tu medico antes de tomar decisiones sobre tu medicacion.
            </div>
          </div>

          <div style="text-align: center; margin-top: 20px; font-size: 14px; color: #666;">
            Deseas otro calculo? Escribe <strong>"otro"</strong>, <strong>"mas"</strong> o <strong>"salir"</strong>.
          </div>
        </div>`;
        
        const botMessage = { id: messages.length + 1, text: responseText, sender: "bot" };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const botMessage = { 
          id: messages.length + 1, 
          text: `No pude procesar tu informacion: ${data.message}. Intenta de nuevo con datos mas claros.`, 
          sender: "bot" 
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error(error);
      const botMessage = { 
        id: messages.length + 1, 
        text: "Error de conexion. Intenta de nuevo.", 
        sender: "bot" 
      };
      setMessages(prev => [...prev, botMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chat-header">
        <h2>Asistente de Dosis de Insulina v2.0</h2>
        <p>Con soporte para lenguaje natural combinado</p>
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            <div className="message-text">
              {msg.text.includes('<div') ? (
                <div dangerouslySetInnerHTML={{ __html: msg.text }} />
              ) : msg.text.includes("**") ? (
                <div dangerouslySetInnerHTML={{ __html: msg.text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>").replace(/\n/g, "<br/>") }} />
              ) : (
                msg.text.split("\n").map((line, idx) => <div key={idx}>{line}</div>)
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEnd} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Escribe tu respuesta..."
        />
        <button onClick={sendMessage}>Enviar</button>
      </div>
    </div>
  );
}

export default ChatBot;
