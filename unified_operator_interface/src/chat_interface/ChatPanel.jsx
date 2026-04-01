import React, { useState } from 'react';

const ChatPanel = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hola, soy el Supervisor de Aspar Aero Hub. ¿En qué puedo ayudarte hoy?' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    
    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');

    // Simulate Agent Response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Analizando: "${input}"... Consultando a los especialistas en el box.` 
      }]);
    }, 1000);
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
