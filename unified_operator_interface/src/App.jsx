import React, { useState } from 'react';
import HITLValidation from './components/HITLValidation';

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
            
            <section className="hitl-panel">
              <HITLValidation />
            </section>
          </div>
        ) : (
          <div className="aero-viewport">
            <h2>Viewport 3D Aerodinámico</h2>
            <div className="viewport-3d-placeholder">Visualizando flujos...</div>
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
