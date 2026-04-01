import json

class TelemetryNormalizer:
    """
    Standardizes raw telemetry values to a common SI-based unit system.
    """
    def __init__(self, mapping_file: str = None):
        self.mappings = self._load_mappings(mapping_file)

    def _load_mappings(self, mapping_file: str):
        if mapping_file:
            with open(mapping_file, 'r') as f:
                return json.load(f)
        # Default fallback mappings
        return {
            "temp": {"unit": "C", "scale": 1.0},
            "pressure": {"unit": "bar", "scale": 1.0},
            "rpm": {"unit": "rev/min", "scale": 1.0},
            "speed": {"unit": "km/h", "scale": 1.0}
        }

    def normalize(self, sensor_type: str, raw_value: float) -> dict:
        """
        Applies scaling and unit conversion according to the configured mapping.
        """
        mapping = self.mappings.get(sensor_type, {"unit": "raw", "scale": 1.0})
        normalized_value = raw_value * mapping["scale"]
        
        return {
            "value": normalized_value,
            "unit": mapping["unit"],
            "original_type": sensor_type
        }

    def normalize_batch(self, telemetry_data: list) -> list:
        """
        Normalizes a batch of telemetry sensor readings.
        """
        return [self.normalize(d["sensor"], d["value"]) for d in telemetry_data]

if __name__ == "__main__":
    # normalizer = TelemetryNormalizer()
    print("Telemetry Normalizer initialized (Skeleton)")
