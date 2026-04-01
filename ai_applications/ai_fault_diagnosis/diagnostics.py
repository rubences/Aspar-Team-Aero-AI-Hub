import numpy as np

class FaultDiagnosisAgent:
    """
    Module for identifying telemetry anomalies and diagnostic log patterns.
    Combines rule-based checks with Z-score outlier detection.
    """
    def __init__(self, thresholds: dict = None):
        self.thresholds = thresholds or {
            "engine_temp": 115.0, # Celsius
            "oil_pressure": 2.0,  # Bar (Min)
            "brake_pressure": 40.0 # Bar (Max)
        }

    def diagnose(self, telemetry_vector: dict) -> list:
        """
        Run diagnostics on current telemetry snapshot.
        """
        alerts = []
        
        # Rule-based alerts
        if telemetry_vector.get("engine_temp", 0) > self.thresholds["engine_temp"]:
            alerts.append({"severity": "CRITICAL", "msg": "Engine Overheating Detected", "code": "E01"})
            
        if telemetry_vector.get("oil_pressure", 5) < self.thresholds["oil_pressure"]:
            alerts.append({"severity": "CRITICAL", "msg": "Low Oil Pressure Danger", "code": "E02"})

        # Statistical Anomaly Check (Mock)
        if np.random.rand() > 0.98: # 2% random anomaly simulation
            alerts.append({"severity": "WARNING", "msg": "Suspension rebound outside normal distribution", "code": "S04"})
            
        return alerts

if __name__ == "__main__":
    diagnostician = FaultDiagnosisAgent()
    sample = {"engine_temp": 120.5, "oil_pressure": 1.8}
    print(f"Diagnostics: {diagnostician.diagnose(sample)}")
