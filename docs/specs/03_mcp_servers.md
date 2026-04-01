# Specification 03: MCP Servers (Model Context Protocol)

## Overview
This specification defines the Model Context Protocol (MCP) servers to expose Aero-Hub data to internal agents and external tools in a standardized format.

## MCP Metadata
- **Protocol**: MCP v0.1
- **Discovery**: JSON-over-stdio / HTTP SSE

## Servers

### 1. `mcp_telemetry`
- **Data Source**: InfluxDB (`telemetry` bucket).
- **Capabilities**:
  - `list_measurements()`: Retrieve available telemetry tags.
  - `query_series(time_range, fields)`: Fetch specific slices of time-series data.
  - `get_realtime_stream()`: Stream sample data from Kafka.

### 2. `mcp_knowledge`
- **Data Source**: Milvus (`regulatory_knowledge` collection).
- **Capabilities**:
  - `semantic_search(query)`: Vector-based search through technical regulations and historical race reports.
  - `get_document_context(doc_id)`: Retrieve full text for a specific regulation.

## Integration Flow
1. Agents call MCP tools via standardized JSON-RPC.
2. Servers translate MCP calls to Influx/Milvus queries.
3. Formatted data is returned to the agent context.
