/**
 * ChatInterface — Conversational console in natural language.
 * Allows race and aero engineers to interact with AI agents via text.
 */

import React, { useState, useRef, useEffect, useCallback } from "react";

const MessageBubble = ({ message }) => {
  const isUser = message.role === "user";
  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: 12,
      }}
    >
      <div
        style={{
          maxWidth: "72%",
          background: isUser ? "#2563eb" : "#1e2433",
          color: "#f9fafb",
          borderRadius: 12,
          padding: "10px 14px",
          fontSize: 14,
          lineHeight: 1.5,
        }}
      >
        {!isUser && (
          <div style={{ color: "#60a5fa", fontSize: 11, marginBottom: 4, fontWeight: 700 }}>
            {message.agent || "AI Agent"}
          </div>
        )}
        <span>{message.content}</span>
        <div style={{ color: "#6b7280", fontSize: 10, marginTop: 4, textAlign: "right" }}>
          {message.timestamp}
        </div>
      </div>
    </div>
  );
};

const ChatInterface = ({ vehicleId = "ASPAR_44", sessionId }) => {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "¡Hola! Soy el asistente IA del equipo Aspar. Puedo ayudarte con análisis aerodinámicos, " +
        "diagnóstico de fallos, estrategia de carrera y configuración del vehículo. ¿En qué puedo ayudarte?",
      agent: "SupervisorAgent",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: "user",
      content: input.trim(),
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          vehicle_id: vehicleId,
          session_id: sessionId,
        }),
      });

      const data = await res.json();
      const agentMessage = {
        role: "assistant",
        content: data.response || "No response from agent.",
        agent: data.agent || "AI Agent",
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, agentMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error connecting to AI backend. Please try again.",
          agent: "System",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading, vehicleId, sessionId]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        background: "#111827",
        fontFamily: "monospace",
      }}
    >
      {/* Header */}
      <div
        style={{
          background: "#1e2433",
          padding: "12px 20px",
          borderBottom: "1px solid #374151",
          color: "#f9fafb",
          fontWeight: 700,
          fontSize: 15,
        }}
      >
        🤖 Aspar AI — Consola Conversacional
        <span style={{ fontSize: 12, fontWeight: 400, color: "#6b7280", marginLeft: 12 }}>
          {vehicleId}
        </span>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "16px 20px" }}>
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && (
          <div style={{ color: "#6b7280", fontSize: 13, marginBottom: 8 }}>
            Agent is thinking...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        style={{
          padding: "12px 20px",
          background: "#1e2433",
          borderTop: "1px solid #374151",
          display: "flex",
          gap: 10,
        }}
      >
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu consulta (aero, fallo, estrategia...)"
          rows={2}
          style={{
            flex: 1,
            background: "#111827",
            color: "#f9fafb",
            border: "1px solid #374151",
            borderRadius: 8,
            padding: "8px 12px",
            fontSize: 14,
            resize: "none",
            fontFamily: "inherit",
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{
            background: loading || !input.trim() ? "#374151" : "#2563eb",
            color: "#f9fafb",
            border: "none",
            borderRadius: 8,
            padding: "0 20px",
            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            fontSize: 14,
            fontWeight: 700,
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
