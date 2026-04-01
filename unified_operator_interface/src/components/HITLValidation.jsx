import React, { useState } from 'react';

const HITLValidation = () => {
  const [recommendations, setRecommendations] = useState([
    {
      id: 1,
      type: 'Aero',
      title: 'Ajuste de Carenado Frontal',
      description: 'La Red GRU predice una pérdida de carga de 0.2kg en la entrada de la curva 3. Se recomienda avance de 2mm.',
      status: 'pending'
    },
    {
      id: 2,
      type: 'Motor',
      title: 'Mapa Energético (E-Map 3)',
      description: 'Basado en RAG (Phillip Island 2023), el consumo actual superará el límite en la vuelta 18. Sugerido cambio a Mapa 3.',
      status: 'pending'
    }
  ]);

  const handleAction = (id, action) => {
    setRecommendations(prev => prev.map(rec => 
      rec.id === id ? { ...rec, status: action } : rec
    ));
    console.log(`Action: ${action} on recommendation ${id}`);
  };

  return (
    <div className="hitl-container">
      <h3>Validación Human-in-the-Loop</h3>
      <p className="p-disclaimer">Prohibición de control bidireccional activa. Confirmación manual requerida.</p>
      
      <div className="recommendations-list">
        {recommendations.map(rec => (
          <div key={rec.id} className={`recommendation-card ${rec.status}`}>
            <div className="rec-header">
              <span className="rec-type">{rec.type}</span>
              <h4>{rec.title}</h4>
            </div>
            <p>{rec.description}</p>
            {rec.status === 'pending' ? (
              <div className="rec-actions">
                <button className="approve-btn" onClick={() => handleAction(rec.id, 'approved')}>APROBAR</button>
                <button className="reject-btn" onClick={() => handleAction(rec.id, 'rejected')}>RECHAZAR</button>
              </div>
            ) : (
              <div className="rec-status-badge">{rec.status.toUpperCase()}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default HITLValidation;
