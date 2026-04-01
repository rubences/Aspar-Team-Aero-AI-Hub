"""
MCP ML Core Server
Exposes PINN and GRU neural networks for on-demand aerodynamic prediction via MCP.
"""

import logging
from pathlib import Path
from typing import Any

import numpy as np
import torch

logger = logging.getLogger(__name__)


class MCPMLCoreServer:
    """Universal MCP connector for ML models (PINN and GRU)."""

    def __init__(self, pinn_model_path: str, gru_model_path: str) -> None:
        self.pinn_model_path = Path(pinn_model_path)
        self.gru_model_path = Path(gru_model_path)
        self._pinn_model: torch.nn.Module | None = None
        self._gru_model: torch.nn.Module | None = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _load_pinn(self) -> torch.nn.Module:
        """Lazy-load the PINN model."""
        if self._pinn_model is None:
            self._pinn_model = torch.load(
                self.pinn_model_path, map_location=self.device
            )
            self._pinn_model.eval()
        return self._pinn_model

    def _load_gru(self) -> torch.nn.Module:
        """Lazy-load the GRU model."""
        if self._gru_model is None:
            self._gru_model = torch.load(
                self.gru_model_path, map_location=self.device
            )
            self._gru_model.eval()
        return self._gru_model

    def predict_aerodynamics(self, geometry_params: list[float],
                              flow_conditions: list[float]) -> dict[str, Any]:
        """Run PINN model for aerodynamic prediction."""
        model = self._load_pinn()
        input_tensor = torch.tensor(
            [geometry_params + flow_conditions], dtype=torch.float32
        ).to(self.device)
        with torch.no_grad():
            output = model(input_tensor)
        result = output.cpu().numpy()[0]
        return {
            "drag_coefficient": float(result[0]),
            "lift_coefficient": float(result[1]),
            "downforce": float(result[2]),
            "model": "PINN",
        }

    def predict_anomalies(self, telemetry_sequence: list[list[float]]) -> dict[str, Any]:
        """Run GRU model to detect anomalies in telemetry sequences."""
        model = self._load_gru()
        seq_tensor = torch.tensor(
            [telemetry_sequence], dtype=torch.float32
        ).to(self.device)
        with torch.no_grad():
            output = model(seq_tensor)
        scores = torch.sigmoid(output).cpu().numpy()[0]
        anomalies = [
            {"step": i, "score": float(s), "is_anomaly": float(s) > 0.5}
            for i, s in enumerate(scores)
        ]
        return {
            "anomalies": anomalies,
            "max_score": float(np.max(scores)),
            "model": "GRU",
        }

    def get_mcp_manifest(self) -> dict[str, Any]:
        """Return the MCP server manifest for agent discovery."""
        return {
            "name": "mcp_ml_core",
            "version": "1.0.0",
            "description": "Exposes PINN/GRU neural networks for on-demand prediction via MCP",
            "capabilities": ["predict_aerodynamics", "predict_anomalies"],
        }
