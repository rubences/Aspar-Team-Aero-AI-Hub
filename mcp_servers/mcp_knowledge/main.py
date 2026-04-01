# MCP Knowledge Server
# Specialized in Milvus (Regulations) and MongoDB (Setups).

from fastapi import FastAPI

app = FastAPI(title="MCP Knowledge Server")

@app.get("/knowledge/query")
def query_knowledge(q: str):
    return {"matches": ["Regulation 15.1.2 - Aero limits", "Philip Island Setup 2024"]}
