import React, { useState } from 'react';
import HITLValidation from './components/HITLValidation';
import ChatPanel from './chat_interface/ChatPanel';
import Viewport3D from './Viewport3D';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>ASPAR TEAM | AERO-AI-HUB</h1>
        <nav>
          <button onClick={() => setActiveTab('dashboard')}>Muro de Boxes</button>
          <button onClick={() => setActiveTab('aero')}>Análisis Aero</button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' ? (
          <div className="dashboard-grid">
            <section className="telemetry-panel">
              <h2>Telemetría en Vivo (Decodificada Babai)</h2>
              <div className="chart-placeholder">Monitorizando...</div>
            </section>
            
            <section className="chat-panel-section">
              <ChatPanel />
            </section>

            <section className="hitl-panel">
              <HITLValidation />
            </section>
          </div>
        ) : (
          <div className="aero-viewport-container">
            <h2>Viewport 3D Aerodinámico (PINN Flow)</h2>
            <Viewport3D />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 Aspar Team - Edge-AI Powered Operations</p>
      </footer>
    </div>
  );
}

export default App;
