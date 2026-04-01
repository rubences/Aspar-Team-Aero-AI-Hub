from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
import os

class InfluxTelemetryClient:
    """
    Client for InfluxDB to handle high-fidelity time-series telemetry.
    """
    def __init__(self, url: str = None, token: str = None, org: str = None, bucket: str = None):
        resolved_url = url or os.getenv("INFLUXDB_URL", "http://localhost:8086")
        resolved_org = org or os.getenv("INFLUXDB_ORG", "aspar-team")
        resolved_bucket = bucket or os.getenv("INFLUXDB_BUCKET", "telemetry")
        resolved_token = token or os.getenv("INFLUXDB_TOKEN")

        self.client = InfluxDBClient(url=resolved_url, token=resolved_token, org=resolved_org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = resolved_bucket
        self.org = resolved_org

    def write_sensor_data(self, sensor_name: str, value: float, bike_id: str, tags: dict = None):
        """
        Writes a single telemetry point.
        """
        point = Point("telemetry") \
            .tag("bike_id", bike_id) \
            .tag("sensor", sensor_name) \
            .field("value", value) \
            .time(datetime.datetime.now(datetime.timezone.utc), WritePrecision.NS)
        
        if tags:
            for key, val in tags.items():
                point.tag(key, val)
                
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def query_recent_telemetry(self, bike_id: str, sensor_name: str, range_start: str = "-15m"):
        """
        Queries telemetry for a specific bike and sensor.
        """
        query = f'from(bucket: "{self.bucket}") \
            |> range(start: {range_start}) \
            |> filter(fn: (r) => r["_measurement"] == "telemetry") \
            |> filter(fn: (r) => r["bike_id"] == "{bike_id}") \
            |> filter(fn: (r) => r["sensor"] == "{sensor_name}")'
        
        return self.query_api.query(org=self.org, query=query)

    def close(self):
        self.client.close()

if __name__ == "__main__":
    # client = InfluxTelemetryClient()
    print("InfluxDB Telemetry Client initialized (Skeleton)")
