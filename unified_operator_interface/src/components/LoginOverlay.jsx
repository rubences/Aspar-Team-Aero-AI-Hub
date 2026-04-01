import React, { useState } from 'react';

const LoginOverlay = ({ onLogin }) => {
  const [username, setUsername] = useState('aspar_engineer');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/auth/token', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('aspar_token', data.access_token);
        onLogin(data.access_token);
      } else {
        setError('Credenciales de Pit Lane Invlidas');
      }
    } catch (err) {
      setError('Error de conexión con el Hub');
    }
  };

  return (
    <div className="login-overlay">
      <div className="login-card">
        <div className="login-logo">ASPAR TEAM | HUB</div>
        <h2>Acceso Restringido - Operaciones Aero</h2>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>USUARIO</label>
            <input 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              placeholder="Nombre del Ingeniero"
            />
          </div>
          <div className="input-group">
            <label>PASSWORD</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="********"
            />
          </div>
          {error && <div className="login-error">{error}</div>}
          <button type="submit">INICIAR SESIN DE PISTA</button>
        </form>
        <p className="login-footer">v1.0.0 Enterprise AI Edition</p>
      </div>
    </div>
  );
};

export default LoginOverlay;
