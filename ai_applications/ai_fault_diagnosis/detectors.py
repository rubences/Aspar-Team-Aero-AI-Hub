import numpy as np

class AnomalyDetector:
    """
    Base Detector for identifying sensor faults and performance deviations.
    """
    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold

    def detect_z_score(self, data: np.ndarray):
        """
        Standard Z-Score anomaly detection.
        """
        mean = np.mean(data)
        std = np.std(data)
        z_scores = np.abs((data - mean) / std)
        return np.where(z_scores > self.threshold)[0]

    def detect_spike(self, data: np.ndarray, max_delta: float):
        """
        Detects sudden jumps (spikes) in continuous sensor readings.
        """
        diffs = np.abs(np.diff(data))
        return np.where(diffs > max_delta)[0]

    def check_health(self, data: np.ndarray) -> dict:
        """
        Aggregated health check for a sensor stream.
        """
        anomalies = self.detect_z_score(data)
        return {
            "is_healthy": len(anomalies) == 0,
            "anomalies_count": len(anomalies),
            "indices": anomalies.tolist()
        }

if __name__ == "__main__":
    # detector = AnomalyDetector()
    print("Anomaly Detector initialized (Skeleton)")
