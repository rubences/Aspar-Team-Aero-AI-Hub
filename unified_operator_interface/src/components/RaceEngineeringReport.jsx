import React, { useMemo, useState } from 'react';

const API_BASE = 'http://localhost:8000';

const RaceEngineeringReport = ({ token }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [report, setReport] = useState(null);

  const executive = useMemo(() => {
    if (!report) return null;
    const meta = report.metadata || {};
    const overview = report.circuit_analysis?.overview || {};
    const mech = report.chassis_dynamics?.mechanical_summary || {};
    const race = report.tire_strategy?.race_strategy || {};
    return {
      event: meta.event,
      circuit: meta.circuit,
      date: meta.generated_at,
      asymmetry: overview?.corners?.asymmetry_ratio,
      thermal: overview.thermal_severity_index,
      wheelbase: mech.wheelbase_delta_mm,
      rake: mech.rake_reduction_deg,
      antiSquat: mech.anti_squat_target_pct,
      raceFront: race.front_compound,
      raceRear: race.rear_compound,
      racePressureFront: race.front_pressure_grid_bar,
      racePressureRear: race.rear_pressure_grid_bar,
      raceViable: race.race_viable,
    };
  }, [report]);

  const fetchReport = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/race-engineering/report`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || 'No se pudo generar el informe.');
      }
      setReport(data.report);
    } catch (e) {
      setError(e.message || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const downloadJson = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'goiania_2026_master_report.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="race-report-container">
      <div className="race-report-toolbar">
        <button onClick={fetchReport} disabled={loading}>
          {loading ? 'Generando informe...' : 'Generar Informe Técnico'}
        </button>
        <button className="ghost" onClick={downloadJson} disabled={!report}>
          Descargar JSON
        </button>
      </div>

      {error && <div className="race-report-error">{error}</div>}

      {!report && !loading && !error && (
        <div className="race-report-empty">
          <h3>Informe Técnico de Ingeniería de Pista</h3>
          <p>
            Ejecuta la generación para cargar el archivo maestro del GP Brasil 2026.
          </p>
        </div>
      )}

      {executive && (
        <div className="race-report-grid">
          <section>
            <h3>Resumen Ejecutivo</h3>
            <ul className="report-list">
              <li><strong>Evento:</strong> {executive.event}</li>
              <li><strong>Circuito:</strong> {executive.circuit}</li>
              <li><strong>Asimetría R/L:</strong> {executive.asymmetry}</li>
              <li><strong>Índice térmico:</strong> {executive.thermal}/10</li>
              <li><strong>Emitido:</strong> {executive.date}</li>
            </ul>
          </section>

          <section>
            <h3>Set-up Propuesto</h3>
            <ul className="report-list">
              <li><strong>Wheelbase:</strong> +{executive.wheelbase} mm</li>
              <li><strong>Rake:</strong> -{executive.rake}°</li>
              <li><strong>Anti-squat objetivo:</strong> {executive.antiSquat}</li>
            </ul>
          </section>

          <section>
            <h3>Estrategia de Carrera</h3>
            <ul className="report-list">
              <li><strong>Neumático delantero:</strong> {executive.raceFront}</li>
              <li><strong>Neumático trasero:</strong> {executive.raceRear}</li>
              <li><strong>Presión delantera:</strong> {executive.racePressureFront} bar</li>
              <li><strong>Presión trasera:</strong> {executive.racePressureRear} bar</li>
              <li>
                <strong>Viabilidad 24 vueltas:</strong>{' '}
                <span className={executive.raceViable ? 'ok' : 'warn'}>
                  {executive.raceViable ? 'Viable' : 'Riesgo térmico'}
                </span>
              </li>
            </ul>
          </section>

          <section>
            <h3>Criterios PoC</h3>
            <ul className="report-list compact">
              {(report.poc_validation_criteria?.success_criteria || []).map((c) => (
                <li key={c.id}>
                  <strong>{c.id}</strong>: {c.metric} <em>({c.target})</em>
                </li>
              ))}
            </ul>
          </section>
        </div>
      )}
    </div>
  );
};

export default RaceEngineeringReport;
