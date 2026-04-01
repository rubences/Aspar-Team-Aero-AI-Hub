import torch
import torch.nn as nn

class AeroPINN(nn.Module):
    """
    Physics-Informed Neural Network (PINN) for Aerodynamic Flow Prediction.
    Learns to predict pressure and velocity fields while constrained by Navier-Stokes.
    """
    def __init__(self, input_dim: int = 3, hidden_dim: int = 50, output_dim: int = 4):
        """
        input_dim: (x, y, z) coordinates.
        output_dim: (u, v, w, p) - velocity components and pressure.
        """
        super(AeroPINN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, coords):
        return self.net(coords)

    def physics_loss(self, coords):
        """
        Calculates the residual of Navier-Stokes equations at given coordinates.
        Uses automatic differentiation (autograd) to find partial derivatives.
        """
        coords.requires_grad = True
        prediction = self.forward(coords)
        u, v, w, p = prediction[:, 0], prediction[:, 1], prediction[:, 2], prediction[:, 3]
        
        # Example: Continuity equation (div U = 0)
        du_dx = torch.autograd.grad(u, coords, grad_outputs=torch.ones_like(u), create_graph=True)[0][:, 0]
        dv_dy = torch.autograd.grad(v, coords, grad_outputs=torch.ones_like(v), create_graph=True)[0][:, 1]
        dw_dz = torch.autograd.grad(w, coords, grad_outputs=torch.ones_like(w), create_graph=True)[0][:, 2]
        
        continuity_residual = du_dx + dv_dy + dw_dz
        loss_f = torch.mean(continuity_residual**2)
        
        return loss_f

if __name__ == "__main__":
    model = AeroPINN()
    mock_coords = torch.randn(10, 3)
    p_loss = model.physics_loss(mock_coords)
    print(f"Physics Loss (Continuity): {p_loss.item()}")
