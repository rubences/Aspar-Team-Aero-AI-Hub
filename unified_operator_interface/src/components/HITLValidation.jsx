import React, { useState } from 'react';

const HITLValidation = () => {
  const [recommendations, setRecommendations] = useState([]);

  // Poll for new recommendations
  React.useEffect(() => {
    const fetchQueue = async () => {
      try {
        const response = await fetch('http://localhost:8000/hitl/queue');
        const data = await response.json();
        setRecommendations(data.map(rec => ({
          ...rec,
          type: rec.recommendation.startsWith('PREDICTIVE') ? 'AI FORECAST' : 'ENGINEERING',
          title: `Evento #${rec.id}`,
          description: rec.recommendation,
          status: rec.recommendation.startsWith('PREDICTIVE') ? 'predictive' : rec.status.toLowerCase()
        })));
      } catch (error) {
        console.error("Error polling HITL queue:", error);
      }
    };

    const interval = setInterval(fetchQueue, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleAction = async (id, action) => {
    try {
      await fetch('http://localhost:8000/hitl/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recommendation_id: id, status: action.toUpperCase() })
      });
      
      setRecommendations(prev => prev.map(rec => 
        rec.id === id ? { ...rec, status: action } : rec
      ));
    } catch (error) {
      console.error("Error validating recommendation:", error);
    }
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
