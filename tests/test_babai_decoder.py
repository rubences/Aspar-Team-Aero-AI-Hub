"""
Tests for the Babai nearest plane quantization decoder.
"""

import numpy as np
import pytest

from ingestion_correlation.babai_quantization.decoder import BabaiDecoder


class TestBabaiDecoder:
    """Test suite for the Babai CVP decoder."""

    def test_identity_basis_returns_rounded_vector(self):
        """With the identity basis, the decoded vector should be the rounded input."""
        basis = np.eye(3)
        decoder = BabaiDecoder(basis)
        target = np.array([1.7, 2.3, -0.8])
        decoded = decoder.decode(target)
        expected = np.round(target).astype(float)
        np.testing.assert_array_almost_equal(decoded, expected)

    def test_decoded_vector_is_lattice_point(self):
        """The decoded vector should lie on the lattice defined by the basis."""
        basis = np.array([[2.0, 0.0], [0.0, 3.0]])
        decoder = BabaiDecoder(basis)
        target = np.array([3.1, 4.7])
        decoded = decoder.decode(target)
        # Decoded should be a linear combination with integer coefficients
        # i.e., decoded = n1 * [2,0] + n2 * [0,3] for integer n1, n2
        coords = np.linalg.solve(basis.T, decoded)
        np.testing.assert_array_almost_equal(coords, np.round(coords))

    def test_quantization_error_is_non_negative(self):
        """Quantization error should always be non-negative."""
        basis = np.eye(4)
        decoder = BabaiDecoder(basis)
        target = np.random.rand(4)
        error = decoder.quantization_error(target)
        assert error >= 0.0

    def test_quantization_error_identity_basis(self):
        """With identity basis, quantization error should be ≤ sqrt(n)/2."""
        n = 5
        basis = np.eye(n)
        decoder = BabaiDecoder(basis)
        for _ in range(10):
            target = np.random.uniform(-5, 5, n)
            error = decoder.quantization_error(target)
            # Maximum possible error with identity basis is sqrt(n)/2
            assert error <= np.sqrt(n) / 2 + 1e-9

    def test_batch_decode_shape(self):
        """Batch decode should return array of same shape as input."""
        basis = np.eye(3)
        decoder = BabaiDecoder(basis)
        targets = np.random.rand(10, 3)
        decoded = decoder.batch_decode(targets)
        assert decoded.shape == targets.shape

    def test_decode_exact_lattice_point(self):
        """A target that is already a lattice point should decode to itself."""
        basis = np.eye(3)
        decoder = BabaiDecoder(basis)
        target = np.array([2.0, -3.0, 5.0])  # already on Z^3 lattice
        decoded = decoder.decode(target)
        np.testing.assert_array_almost_equal(decoded, target)

    def test_gram_schmidt_orthogonality(self):
        """Gram-Schmidt basis vectors should be mutually orthogonal."""
        basis = np.array([[1.0, 1.0, 0.0], [0.0, 1.0, 1.0], [1.0, 0.0, 1.0]])
        decoder = BabaiDecoder(basis)
        gs = decoder._gs_basis
        n = gs.shape[0]
        for i in range(n):
            for j in range(i):
                dot = np.dot(gs[i], gs[j])
                assert abs(dot) < 1e-9, f"GS vectors {i} and {j} are not orthogonal: dot={dot}"
