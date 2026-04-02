import React, { useState, useEffect } from 'react';
import HITLValidation from './components/HITLValidation';
import ChatPanel from './chat_interface/ChatPanel';
import Viewport3D from './Viewport3D';
import LoginOverlay from './components/LoginOverlay';
import TelemetryBoard from './components/TelemetryBoard';
import RaceEngineeringReport from './components/RaceEngineeringReport';

function App() {
  const [token, setToken] = useState(localStorage.getItem('aspar_token'));
  const [activeTab, setActiveTab] = useState('dashboard');
  const [health, setHealth] = useState('OFFLINE');

  // Service Health Monitor (PoC Readiness)
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('http://localhost:8000/health');
        if (res.ok) setHealth('ONLINE');
        else setHealth('ERROR');
      } catch (err) {
        setHealth('OFFLINE');
      }
    };
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!token) {
    return <LoginOverlay onLogin={(newToken) => setToken(newToken)} />;
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <h1>ASPAR TEAM | HUB</h1>
          <div className={`health-dot ${health}`} title={`System Status: ${health}`} />
        </div>
        <nav>
          <button className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>Muro de Boxes</button>
          <button className={activeTab === 'aero' ? 'active' : ''} onClick={() => setActiveTab('aero')}>Análisis Aero</button>
          <button className={activeTab === 'race-report' ? 'active' : ''} onClick={() => setActiveTab('race-report')}>Informe Goiânia</button>
          <button className="logout-btn" onClick={() => { localStorage.removeItem('aspar_token'); setToken(null); }}>SALIR</button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' ? (
          <div className="dashboard-grid">
            <section className="telemetry-panel">
              <h2>Telemetría en Vivo (Lattice Decoded)</h2>
              <TelemetryBoard token={token} />
            </section>
            
            <section className="chat-panel-section">
              <ChatPanel token={token} />
            </section>

            <section className="hitl-panel">
              <HITLValidation token={token} />
            </section>
          </div>
        ) : (
          <div className="aero-viewport-container">
            <h2>Viewport 3D Aerodinámico (PINN Flow)</h2>
            <Viewport3D token={token} />
          </div>
        ) : (
          <div className="report-panel-container">
            <h2>Informe Técnico de Ingeniería de Pista (PoC)</h2>
            <RaceEngineeringReport token={token} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 Aspar Team - POC v9.0.0 Enterprise AI Edition</p>
      </footer>
    </div>
  );
}

export default App;
