"""
GRU Inference — Gated Recurrent Unit network for anomaly prediction.
Processes multi-variate telemetry sequences to detect anomalies,
degradation patterns, and performance deviations in real time.
"""

import logging
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

SEQUENCE_LENGTH = 50
INPUT_FEATURES = 16
HIDDEN_DIM = 128
NUM_LAYERS = 2
ANOMALY_THRESHOLD = 0.5


class GRUAnomalyDetector(nn.Module):
    """
    Multi-layer GRU network for telemetry anomaly detection.

    Takes a sequence of telemetry readings and outputs an anomaly score
    for each time step, allowing detection of point anomalies, contextual
    anomalies, and collective anomaly patterns.
    """

    def __init__(self, input_dim: int = INPUT_FEATURES,
                 hidden_dim: int = HIDDEN_DIM,
                 num_layers: int = NUM_LAYERS,
                 dropout: float = 0.2) -> None:
        super().__init__()
        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Tensor of shape (batch, seq_len, input_dim).

        Returns:
            Anomaly scores of shape (batch, seq_len).
        """
        gru_out, _ = self.gru(x)
        scores = self.classifier(gru_out).squeeze(-1)
        return scores


class GRUInferenceEngine:
    """Manages inference with the GRU anomaly detection model."""

    def __init__(self, model_path: str | None = None,
                 device: str | None = None) -> None:
        self.device = torch.device(
            device or ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.model = GRUAnomalyDetector().to(self.device)
        if model_path and Path(model_path).exists():
            self.load(model_path)
        self.model.eval()

    def predict(self, sequence: np.ndarray) -> dict[str, Any]:
        """
        Run anomaly detection on a telemetry sequence.

        Args:
            sequence: Array of shape (seq_len, input_dim).

        Returns:
            Dictionary with anomaly scores and detected anomaly intervals.
        """
        x = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            raw_scores = self.model(x)
            scores = torch.sigmoid(raw_scores).cpu().numpy()[0]

        anomaly_mask = scores > ANOMALY_THRESHOLD
        intervals = self._find_intervals(anomaly_mask)

        return {
            "scores": scores.tolist(),
            "anomaly_mask": anomaly_mask.tolist(),
            "anomaly_intervals": intervals,
            "max_score": float(np.max(scores)),
            "mean_score": float(np.mean(scores)),
            "is_anomalous": bool(np.any(anomaly_mask)),
        }

    @staticmethod
    def _find_intervals(mask: np.ndarray) -> list[dict[str, int]]:
        """Find contiguous anomaly intervals from a boolean mask."""
        intervals = []
        start = None
        for i, v in enumerate(mask):
            if v and start is None:
                start = i
            elif not v and start is not None:
                intervals.append({"start": start, "end": i - 1})
                start = None
        if start is not None:
            intervals.append({"start": start, "end": len(mask) - 1})
        return intervals

    def predict_batch(self, sequences: np.ndarray) -> list[dict[str, Any]]:
        """Run anomaly detection on a batch of sequences."""
        return [self.predict(seq) for seq in sequences]

    def save(self, path: str) -> None:
        """Save model weights."""
        torch.save(self.model.state_dict(), path)
        logger.info("GRU model saved to %s", path)

    def load(self, path: str) -> None:
        """Load model weights."""
        self.model.load_state_dict(
            torch.load(path, map_location=self.device)
        )
        self.model.eval()
        logger.info("GRU model loaded from %s", path)
