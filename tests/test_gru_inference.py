"""
Tests for the GRU anomaly detection inference engine.
"""

import numpy as np
import pytest
import torch

from ai_applications.ai_aero_predict.gru_inference.model import (
    ANOMALY_THRESHOLD,
    INPUT_FEATURES,
    SEQUENCE_LENGTH,
    GRUAnomalyDetector,
    GRUInferenceEngine,
)


class TestGRUAnomalyDetector:
    """Test suite for the GRU model architecture."""

    def test_output_shape(self):
        """Model should output (batch, seq_len) scores."""
        model = GRUAnomalyDetector(input_dim=INPUT_FEATURES)
        x = torch.zeros(2, SEQUENCE_LENGTH, INPUT_FEATURES)
        with torch.no_grad():
            out = model(x)
        assert out.shape == (2, SEQUENCE_LENGTH)

    def test_forward_no_nan(self):
        """Forward pass should not produce NaN values."""
        model = GRUAnomalyDetector()
        x = torch.randn(4, 30, INPUT_FEATURES)
        with torch.no_grad():
            out = model(x)
        assert not torch.isnan(out).any()

    def test_output_range_after_sigmoid(self):
        """Sigmoid-activated outputs should be in [0, 1]."""
        model = GRUAnomalyDetector()
        x = torch.randn(2, 20, INPUT_FEATURES)
        with torch.no_grad():
            out = torch.sigmoid(model(x))
        assert (out >= 0.0).all()
        assert (out <= 1.0).all()


class TestGRUInferenceEngine:
    """Test suite for the GRU inference engine."""

    def _make_engine(self) -> GRUInferenceEngine:
        return GRUInferenceEngine(model_path=None, device="cpu")

    def test_predict_returns_expected_keys(self):
        """predict() should return all expected keys."""
        engine = self._make_engine()
        seq = np.random.rand(SEQUENCE_LENGTH, INPUT_FEATURES).astype(np.float32)
        result = engine.predict(seq)
        assert "scores" in result
        assert "anomaly_mask" in result
        assert "anomaly_intervals" in result
        assert "max_score" in result
        assert "mean_score" in result
        assert "is_anomalous" in result

    def test_scores_length_matches_sequence(self):
        """Scores list length should match the input sequence length."""
        engine = self._make_engine()
        seq = np.zeros((SEQUENCE_LENGTH, INPUT_FEATURES), dtype=np.float32)
        result = engine.predict(seq)
        assert len(result["scores"]) == SEQUENCE_LENGTH

    def test_anomaly_mask_is_boolean(self):
        """Anomaly mask should contain boolean values."""
        engine = self._make_engine()
        seq = np.random.rand(SEQUENCE_LENGTH, INPUT_FEATURES).astype(np.float32)
        result = engine.predict(seq)
        assert all(isinstance(v, bool) for v in result["anomaly_mask"])

    def test_intervals_structure(self):
        """Anomaly intervals should be dicts with start/end keys."""
        engine = self._make_engine()
        seq = np.random.rand(SEQUENCE_LENGTH, INPUT_FEATURES).astype(np.float32)
        result = engine.predict(seq)
        for interval in result["anomaly_intervals"]:
            assert "start" in interval
            assert "end" in interval
            assert interval["start"] <= interval["end"]

    def test_find_intervals(self):
        """_find_intervals should correctly identify contiguous runs."""
        mask = np.array([False, True, True, False, True, False])
        intervals = GRUInferenceEngine._find_intervals(mask)
        assert len(intervals) == 2
        assert intervals[0] == {"start": 1, "end": 2}
        assert intervals[1] == {"start": 4, "end": 4}

    def test_find_intervals_empty(self):
        """_find_intervals with no anomalies should return empty list."""
        mask = np.zeros(10, dtype=bool)
        intervals = GRUInferenceEngine._find_intervals(mask)
        assert intervals == []

    def test_predict_batch(self):
        """predict_batch should return one result per sequence."""
        engine = self._make_engine()
        sequences = np.random.rand(3, SEQUENCE_LENGTH, INPUT_FEATURES).astype(np.float32)
        results = engine.predict_batch(sequences)
        assert len(results) == 3
