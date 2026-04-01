from typing import Dict, Any
import numpy as np

class TelemetryNormalizer:
    """
    Standardizes raw telemetry snapshots into a common vector format for AI models.
    Ensures units (km/h vs m/s), ranges (scaling), and missing value handling.
    """
    def __init__(self, feature_map: Dict[str, int], scaling_factors: Dict[str, float] = None):
        self.feature_map = feature_map
        self.inv_map = {v: k for k, v in feature_map.items()}
        self.scaling_factors = scaling_factors or {}
        self.vector_dim = len(feature_map)

    def normalize(self, raw_data: Dict[str, Any]) -> np.ndarray:
        """
        Transforms dict of sensors to a normalized numpy vector.
        """
        vector = np.zeros(self.vector_dim)
        
        for key, value in raw_data.items():
            if key in self.feature_map:
                idx = self.feature_map[key]
                # Apply scaling if defined
                scale = self.scaling_factors.get(key, 1.0)
                vector[idx] = float(value) * scale
                
        return vector

    def denormalize(self, vector: np.ndarray) -> Dict[str, Any]:
        """
        Transforms a vector back into a readable dictionary.
        """
        data = {}
        for idx, value in enumerate(vector):
            key = self.inv_map.get(idx)
            if key:
                scale = self.scaling_factors.get(key, 1.0)
                data[key] = value / scale
        return data

if __name__ == "__main__":
    # Example: 10 sensors
    f_map = {
        "speed": 0, "rpm": 1, "lean_angle": 2, "throttle": 3, 
        "brake_front": 4, "brake_rear": 5, "suspension_f": 6, 
        "suspension_r": 7, "temp_tire_f": 8, "temp_tire_r": 9
    }
    # Scaling to 0-1 approx or standard units
    scales = {"speed": 1/350, "rpm": 1/15000}
    
    normalizer = TelemetryNormalizer(f_map, scales)
    raw = {"speed": 280, "rpm": 12500, "lean_angle": 45, "throttle": 0.8}
    
    norm_vec = normalizer.normalize(raw)
    print(f"Normalized Vector: {norm_vec}")
    print(f"Denormalized Data (Speed): {normalizer.denormalize(norm_vec)['speed']}")
