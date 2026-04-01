/**
 * TelemetryDashboard — Real-time telemetry display with KPI cards.
 * Shows live vehicle data for speed, RPM, temperatures, and aero forces.
 */

import React, { useEffect, useState, useCallback } from "react";

const KPICard = ({ label, value, unit, status }) => {
  const statusColors = {
    ok: "#22c55e",
    warning: "#f59e0b",
    critical: "#ef4444",
    unknown: "#6b7280",
  };
  const color = statusColors[status] || statusColors.unknown;

  return (
    <div
      style={{
        background: "#1e2433",
        borderRadius: 8,
        padding: "16px 20px",
        minWidth: 140,
        borderLeft: `4px solid ${color}`,
      }}
    >
      <div style={{ color: "#9ca3af", fontSize: 12, marginBottom: 4 }}>{label}</div>
      <div style={{ color: "#f9fafb", fontSize: 24, fontWeight: 700 }}>
        {value !== null && value !== undefined ? value : "—"}
        <span style={{ fontSize: 13, fontWeight: 400, color: "#9ca3af", marginLeft: 4 }}>
          {unit}
        </span>
      </div>
    </div>
  );
};

const TelemetryDashboard = ({ vehicleId = "ASPAR_44", sessionId }) => {
  const [telemetry, setTelemetry] = useState(null);
  const [faults, setFaults] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchTelemetry = useCallback(async () => {
    try {
      const res = await fetch(`/api/telemetry/latest?vehicle_id=${vehicleId}`);
      if (!res.ok) return;
      const data = await res.json();
      setTelemetry(data);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch {
      // Network error — keep stale data
    }
  }, [vehicleId]);

  const fetchFaults = useCallback(async () => {
    try {
      const res = await fetch(`/api/faults/active?vehicle_id=${vehicleId}`);
      if (!res.ok) return;
      const data = await res.json();
      setFaults(data.faults || []);
    } catch {
      // Network error
    }
  }, [vehicleId]);

  useEffect(() => {
    fetchTelemetry();
    fetchFaults();
    const interval = setInterval(() => {
      fetchTelemetry();
      fetchFaults();
    }, 500); // 2 Hz refresh
    return () => clearInterval(interval);
  }, [fetchTelemetry, fetchFaults]);

  const getStatus = (value, high, critical) => {
    if (value === null || value === undefined) return "unknown";
    if (value >= critical) return "critical";
    if (value >= high) return "warning";
    return "ok";
  };

  return (
    <div style={{ background: "#111827", minHeight: "100vh", padding: 24, fontFamily: "monospace" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h2 style={{ color: "#f9fafb", margin: 0 }}>
          🏍 Aspar SmartOps — Live Telemetry
        </h2>
        <span style={{ color: "#6b7280", fontSize: 13 }}>
          Vehicle: {vehicleId} | Last update: {lastUpdate || "—"}
        </span>
      </div>

      {/* KPI Grid */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 24 }}>
        <KPICard
          label="Speed"
          value={telemetry?.speed_kmh?.toFixed(1)}
          unit="km/h"
          status={getStatus(telemetry?.speed_kmh, 280, 330)}
        />
        <KPICard
          label="RPM"
          value={telemetry?.rpm?.toFixed(0)}
          unit="rpm"
          status={getStatus(telemetry?.rpm, 13500, 14000)}
        />
        <KPICard
          label="Oil Temp"
          value={telemetry?.oil_temp_c?.toFixed(1)}
          unit="°C"
          status={getStatus(telemetry?.oil_temp_c, 130, 145)}
        />
        <KPICard
          label="Water Temp"
          value={telemetry?.water_temp_c?.toFixed(1)}
          unit="°C"
          status={getStatus(telemetry?.water_temp_c, 105, 115)}
        />
        <KPICard
          label="Downforce"
          value={telemetry?.downforce_n?.toFixed(0)}
          unit="N"
          status="ok"
        />
        <KPICard
          label="Drag"
          value={telemetry?.drag_n?.toFixed(0)}
          unit="N"
          status="ok"
        />
        <KPICard
          label="Gear"
          value={telemetry?.gear}
          unit=""
          status="ok"
        />
        <KPICard
          label="Throttle"
          value={telemetry?.throttle_pct?.toFixed(0)}
          unit="%"
          status="ok"
        />
      </div>

      {/* Active Faults */}
      {faults.length > 0 && (
        <div style={{ background: "#1e2433", borderRadius: 8, padding: 16 }}>
          <h3 style={{ color: "#ef4444", margin: "0 0 12px" }}>⚠ Active Faults</h3>
          {faults.map((fault, i) => (
            <div
              key={i}
              style={{
                color: fault.severity === "critical" ? "#ef4444" : "#f59e0b",
                fontSize: 13,
                marginBottom: 6,
              }}
            >
              [{fault.severity?.toUpperCase()}] {fault.description}
            </div>
          ))}
        </div>
      )}

      {!telemetry && (
        <div style={{ color: "#6b7280", textAlign: "center", marginTop: 48 }}>
          Waiting for telemetry data...
        </div>
      )}
    </div>
  );
};

export default TelemetryDashboard;
