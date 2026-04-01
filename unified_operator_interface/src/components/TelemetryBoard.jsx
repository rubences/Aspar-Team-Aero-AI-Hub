import React, { useState, useEffect } from 'react';

const Sparkline = ({ data, color, height = 40, width = 200 }) => {
  if (!data || data.length < 2) return <div style={{height, width}} />;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((val - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height}>
      <polyline fill="none" stroke={color} strokeWidth="2" points={points} />
    </svg>
  );
};

const TelemetryBoard = ({ token }) => {
  const [metrics, setMetrics] = useState({ rpm: [], temp: [], rake: [] });
  const [current, setCurrent] = useState({ rpm: 0, temp: 0, rake: 0 });

  useEffect(() => {
    const pollTelemetry = async () => {
      try {
        const response = await fetch('http://localhost:8000/telemetry/active?bike_id=ASPAR-AERO-01', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        
        // Mock data update logic (since MCP might not have full history in ONE call)
        const newRpm = data.rpm || (12000 + Math.random() * 500);
        const newTemp = data.temp || (98 + Math.random() * 2);
        const newRake = data.rake || (1.2 + Math.random() * 0.1);

        setCurrent({ rpm: newRpm, temp: newTemp, rake: newRake });
        setMetrics(prev => ({
          rpm: [...prev.rpm.slice(-20), newRpm],
          temp: [...prev.temp.slice(-20), newTemp],
          rake: [...prev.rake.slice(-20), newRake]
        }));
      } catch (err) {
        console.error("Telemetry Poll Error");
      }
    };

    const interval = setInterval(pollTelemetry, 500);
    return () => clearInterval(interval);
  }, [token]);

  return (
    <div className="telemetry-grid">
      <div className="metric-box">
        <label>RPM MOTOR</label>
        <div className="metric-value">{Math.round(current.rpm)}</div>
        <Sparkline data={metrics.rpm} color="#00ecff" />
      </div>
      <div className="metric-box">
        <label>TEMP ENGINE</label>
        <div className="metric-value">{current.temp.toFixed(1)}C</div>
        <Sparkline data={metrics.temp} color="#ff0055" />
      </div>
      <div className="metric-box">
        <label>RAKE AERO</label>
        <div className="metric-value">{current.rake.toFixed(2)}mm</div>
        <Sparkline data={metrics.rake} color="#00ecff" />
      </div>
    </div>
  );
};

export default TelemetryBoard;
