import torch
import torch.nn as nn
import numpy as np

class DynamicsGRU(nn.Module):
    """
    Gated Recurrent Unit (GRU) model for vehicle dynamics and anomaly prediction.
    Features state concatenation with historical vector context.
    """
    def __init__(self, input_dim: int, context_dim: int, hidden_dim: int, output_dim: int, n_layers: int = 2):
        super(DynamicsGRU, self).__init__()
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        
        # Combined input: current telemetry (input_dim) + historical context (context_dim)
        self.gru = nn.GRU(input_dim + context_dim, hidden_dim, n_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x, context, h=None):
        """
        x: (batch, seq_len, input_dim) - Live telemetry
        context: (batch, seq_len, context_dim) - Retrieved historical context
        h: Initial hidden state
        """
        # Concatenate live telemetry with retrieved context
        combined = torch.cat((x, context), dim=-1)
        
        out, h = self.gru(combined, h)
        # We take the output of the last time step
        out = self.fc(out[:, -1, :])
        return out, h

class GRUInferenceEngine:
    """
    Handles model loading and real-time inference for Aspar Team.
    """
    def __init__(self, input_dim: int, context_dim: int, hidden_dim: int, output_dim: int):
        self.model = DynamicsGRU(input_dim, context_dim, hidden_dim, output_dim)
        self.model.eval()
        
    def predict_dynamics(self, telemetry: np.ndarray, context: np.ndarray) -> np.ndarray:
        """
        Predicts next state and anomaly score.
        """
        tele_tensor = torch.FloatTensor(telemetry).unsqueeze(0) # Batch size 1
        ctx_tensor = torch.FloatTensor(context).unsqueeze(0)
        
        with torch.no_grad():
            prediction, _ = self.model(tele_tensor, ctx_tensor)
            
        return prediction.squeeze().numpy()

if __name__ == "__main__":
    # Test initialization
    engine = GRUInferenceEngine(input_dim=10, context_dim=64, hidden_dim=128, output_dim=5)
    
    # Mock data [batch=1, seq_len=1, dim]
    mock_telemetry = np.random.randn(1, 10)
    mock_context = np.random.randn(1, 64)
    
    pred = engine.predict_dynamics(mock_telemetry, mock_context)
    print(f"Dynamics Prediction Shape: {pred.shape}")
    print(f"Prediction: {pred}")
