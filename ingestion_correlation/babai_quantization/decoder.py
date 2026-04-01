"""
Babai Quantization — Nearest Plane Algorithm Decoder
Implements Babai's nearest plane algorithm for lattice-based quantization,
used to decode and denoise high-dimensional telemetry sensor data.
"""

import logging

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


class BabaiDecoder:
    """
    Implements Babai's nearest plane (CVP approximation) algorithm.

    Given a lattice basis B and a target vector t, finds the approximate
    closest lattice vector using the Gram-Schmidt orthogonalization process.

    This is used in the ingestion layer to project noisy sensor readings
    onto the nearest valid quantization lattice point, reducing measurement
    noise before correlation and storage.
    """

    def __init__(self, basis: NDArray[np.float64]) -> None:
        """
        Initialize the decoder with a lattice basis matrix.

        Args:
            basis: An (n x n) matrix whose rows form the lattice basis vectors.
        """
        self.basis = np.array(basis, dtype=np.float64)
        self.n = self.basis.shape[0]
        self._gs_basis, self._mu = self._gram_schmidt(self.basis)

    @staticmethod
    def _gram_schmidt(
        basis: NDArray[np.float64],
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute the Gram-Schmidt orthogonalization of the basis."""
        n = basis.shape[0]
        gs = np.zeros_like(basis)
        mu = np.zeros((n, n), dtype=np.float64)

        for i in range(n):
            gs[i] = basis[i].copy()
            for j in range(i):
                mu[i, j] = np.dot(basis[i], gs[j]) / np.dot(gs[j], gs[j])
                gs[i] -= mu[i, j] * gs[j]

        return gs, mu

    def decode(self, target: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Find the approximate nearest lattice vector to the target using
        Babai's nearest plane algorithm.

        Args:
            target: The target vector to decode (1-D array of length n).

        Returns:
            The approximate nearest lattice vector as a 1-D array.
        """
        target = np.array(target, dtype=np.float64)
        coefficients = np.zeros(self.n, dtype=np.float64)
        residual = target.copy()

        for i in range(self.n - 1, -1, -1):
            gs_norm_sq = np.dot(self._gs_basis[i], self._gs_basis[i])
            if gs_norm_sq < 1e-12:
                continue
            c = np.dot(residual, self._gs_basis[i]) / gs_norm_sq
            coefficients[i] = np.round(c)
            residual -= coefficients[i] * self.basis[i]

        decoded = np.dot(coefficients, self.basis)
        logger.debug("Babai decode: target=%s -> decoded=%s", target, decoded)
        return decoded

    def batch_decode(
        self, targets: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """
        Decode a batch of target vectors.

        Args:
            targets: An (m x n) array of m target vectors.

        Returns:
            An (m x n) array of decoded lattice vectors.
        """
        return np.array([self.decode(t) for t in targets])

    def quantization_error(
        self, target: NDArray[np.float64]
    ) -> float:
        """
        Compute the Euclidean distance between the target and its decoded vector.

        Args:
            target: The input target vector.

        Returns:
            The quantization error (Euclidean distance).
        """
        decoded = self.decode(target)
        return float(np.linalg.norm(target - decoded))
