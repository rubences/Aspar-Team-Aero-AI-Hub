# MCP Telemetry Server
# Provides universal access to InfluxDB and Kafka telemetry streams.

from fastapi import FastAPI

app = FastAPI(title="MCP Telemetry Server")

@app.get("/schema")
def get_schema():
    return {"protocols": ["influxdb", "kafka"], "endpoints": ["/stream", "/historical"]}
