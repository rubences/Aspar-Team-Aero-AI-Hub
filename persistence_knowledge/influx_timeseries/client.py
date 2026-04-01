import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import time

class InfluxTelemetryClient:
    """
    High-throughput timeseries writer for InfluxDB.
    Stores raw and reconstructed sensor data.
    """
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = bucket
        self.org = org

    def write_snapshot(self, device_id: str, sensor_data: dict, timestamp: int = None):
        """
        Writes a single telemetry snapshot to InfluxDB.
        """
        ts = timestamp or int(time.time() * 1e9) # Nanoseconds
        point = influxdb_client.Point("telemetry_snapshot") \
            .tag("bike_id", device_id)
        
        for key, value in sensor_data.items():
            point.field(key, float(value))
            
        point.time(ts)
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def query_window(self, bike_id: str, window_seconds: int = 60):
        """
        Queries telemetry window using Flux.
        """
        query_api = self.client.query_api()
        flux = f'from(bucket:"{self.bucket}") \
                |> range(start: -{window_seconds}s) \
                |> filter(fn: (r) => r["_measurement"] == "telemetry_snapshot") \
                |> filter(fn: (r) => r["bike_id"] == "{bike_id}")'
        
        return query_api.query(flux, org=self.org)

if __name__ == "__main__":
    # client = InfluxTelemetryClient("http://localhost:8086", "token", "aspar", "telemetry")
    print("InfluxDB Client initialized (Skeleton)")
