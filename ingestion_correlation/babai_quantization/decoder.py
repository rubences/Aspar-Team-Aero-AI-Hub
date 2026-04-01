import numpy as np

class BabaiDecoder:
    """
    Babai's Closest Plane Algorithm Decoder for Quantized Telemetry.
    Used to reconstruct high-fidelity telemetry vectors from discrete integer representations.
    """
    def __init__(self, basis_matrix: np.ndarray):
        """
        Initialize with the lattice basis matrix B.
        B: (n, n) matrix where each column is a basis vector.
        """
        self.B = basis_matrix
        self.B_inv = np.linalg.inv(basis_matrix)
        # Gram-Schmidt orthogonalization for Babai's algorithm (Lattice decoding)
        self.Q, self.R = np.linalg.qr(basis_matrix)

    def decode(self, z: np.ndarray) -> np.ndarray:
        """
        Reconstructs the original vector x from the integer vector z.
        x = B * z
        """
        return np.dot(self.B, z)

    def quantize(self, x: np.ndarray) -> np.ndarray:
        """
        Finds the closest lattice point to vector x using Babai's Closest Plane algorithm.
        This is typically what happens on the bike (on-board).
        Included here for reciprocity and testing.
        """
        n = x.shape[0]
        b = np.copy(x)
        z = np.zeros(n, dtype=int)
        
        # Babai's Closest Plane algorithm
        for i in reversed(range(n)):
            # Calculate the coefficient for the i-th basis vector
            # This is a simplified version; full Babai uses the GS orthogonal basis
            # and iterative subtraction.
            c = np.dot(b, self.Q[:, i]) / self.R[i, i]
            z[i] = int(np.round(c))
            b -= z[i] * self.B[:, i]
            
        return z

if __name__ == "__main__":
    # Example usage for verification
    basis = np.array([[1.0, 0.5], [0.0, 0.866]]) # Hexagonal lattice
    decoder = BabaiDecoder(basis)
    
    original = np.array([10.2, 5.7])
    quantized = decoder.quantize(original)
    reconstructed = decoder.decode(quantized)
    
    print(f"Original: {original}")
    print(f"Quantized (Integer Vector): {quantized}")
    print(f"Reconstructed: {reconstructed}")
    print(f"Error: {np.linalg.norm(original - reconstructed)}")
