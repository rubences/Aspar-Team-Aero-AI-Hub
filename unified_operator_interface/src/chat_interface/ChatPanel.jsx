import React, { useState } from 'react';

const ChatPanel = ({ token }) => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hola, soy el Supervisor de Aspar Aero Hub. ¿En qué puedo ayudarte hoy?' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await fetch('http://localhost:8000/genai/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ message: input, bike_id: 'ASPAR-AERO-01' })
      });
      
      const data = await response.json();
      if (data.response) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.response 
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "Error: No se pudo contactar con el centro de mando." 
      }]);
    }
  };

  return (
    <div className="chat-container">
      <h3>Consola del Agente</h3>
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <strong>{m.role === 'user' ? 'Tú' : 'IA'}:</strong> {m.content}
          </div>
        ))}
      </div>
      <div className="chat-input-area">
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          placeholder="Consulta a los ingenieros..."
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Enviar</button>
      </div>
    </div>
  );
};

export default ChatPanel;
