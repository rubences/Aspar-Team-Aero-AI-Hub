import numpy as np
import logging

logger = logging.getLogger("FaultDiagnosis")

class FaultDiagnosisAgent:
    """
    Advanced Diagnostic Engine for Aspar Team.
    Performs multivariate analysis and geometric fault correlation.
    """
    def __init__(self, thresholds: dict = None):
        self.thresholds = thresholds or {
            "engine_temp_max": 110.0,
            "rake_min": 0.5, # mm
            "rake_max": 2.5, # mm
            "suspension_mismatch": 5.0 # mm tolerance
        }

    def analyze_geo_fault(self, rake: float, front_suspension: float, rear_suspension: float) -> list:
        """
        Correlates vertical movement with aero rake to identify mechanical/geometric failures.
        """
        alerts = []
        
        # Theoretical Rake calculation based on suspension (simplified model)
        # In a real scenario, this would be a lookup table or a small PINN
        theoretical_rake = (rear_suspension - front_suspension) * 0.1
        
        # Cross-validation: If sensors say rake is dropping but suspension is stable, 
        # it's likely an aerodynamic stall or sensor drift.
        diff = abs(rake - theoretical_rake)
        
        if diff > self.thresholds["suspension_mismatch"]:
            alerts.append({
                "severity": "CRITICAL",
                "msg": f"Geometric mismatch: Rake ({rake:.2f}) doesn't match suspension state. Probable Aero Stall.",
                "code": "GEO-A01"
            })
            
        return alerts

    def diagnose_multivariate(self, telemetry: dict) -> list:
        """
        Run deep diagnostics on the telemetry bundle.
        """
        alerts = []
        
        # 1. Thermal - Pressure Correlation
        temp = telemetry.get("engine_temp", 0)
        pressure = telemetry.get("oil_pressure", 5.0)
        
        if temp > self.thresholds["engine_temp_max"] and pressure < 3.0:
            alerts.append({"severity": "CRITICAL", "msg": "Compromised engine health: High temp + Low pressure", "code": "ENG-H01"})
        
        # 2. Geometric Correlation
        rake = telemetry.get("rake", 1.2)
        f_susp = telemetry.get("front_suspension", 50.0)
        r_susp = telemetry.get("rear_suspension", 55.0)
        
        geo_alerts = self.analyze_geo_fault(rake, f_susp, r_susp)
        alerts.extend(geo_alerts)
        
        return alerts

if __name__ == "__main__":
    diag = FaultDiagnosisAgent()
    # Case: Rake is 0.2 (critical stall) but suspension is at normal cruising state
    case = {"rake": 0.2, "front_suspension": 50, "rear_suspension": 55, "engine_temp": 112, "oil_pressure": 2.5}
    results = diag.diagnose_multivariate(case)
    for r in results:
        print(f"[{r['severity']}] {r['code']}: {r['msg']}")
