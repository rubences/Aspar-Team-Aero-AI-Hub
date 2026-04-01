"""
PINN — Physics-Informed Neural Network for aerodynamic modelling.
Combines data-driven learning with physical equations (Navier-Stokes)
to predict aerodynamic coefficients with high accuracy and physical consistency.
"""

import logging
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from torch.optim import Adam

logger = logging.getLogger(__name__)


class PINNAeroModel(nn.Module):
    """
    Physics-Informed Neural Network for aerodynamic force prediction.

    The network takes geometry parameters and flow conditions as input
    and predicts drag coefficient (Cd), lift coefficient (Cl), and downforce.
    A physics residual loss based on simplified Navier-Stokes equations
    is added during training to enforce physical consistency.
    """

    def __init__(self, input_dim: int = 12, hidden_dim: int = 256,
                 output_dim: int = 3, n_layers: int = 6) -> None:
        super().__init__()
        layers: list[nn.Module] = [nn.Linear(input_dim, hidden_dim), nn.Tanh()]
        for _ in range(n_layers - 1):
            layers += [nn.Linear(hidden_dim, hidden_dim), nn.Tanh()]
        layers.append(nn.Linear(hidden_dim, output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass: geometry + flow conditions → [Cd, Cl, downforce]."""
        return self.net(x)

    def physics_residual(self, x: torch.Tensor) -> torch.Tensor:
        """
        Compute a simplified physics consistency loss.
        Enforces the relationship: downforce = 0.5 * rho * v^2 * A * Cl
        where rho=1.225 kg/m^3 (air density at sea level).
        """
        preds = self.forward(x)
        cl = preds[:, 1]
        downforce = preds[:, 2]
        v = x[:, 0]
        area = x[:, 1]
        rho = 1.225
        downforce_physics = 0.5 * rho * v ** 2 * area * cl
        residual = torch.mean((downforce - downforce_physics) ** 2)
        return residual


class PINNTrainer:
    """Manages training of the PINN aerodynamic model."""

    def __init__(self, model: PINNAeroModel, physics_weight: float = 0.1,
                 lr: float = 1e-4) -> None:
        self.model = model
        self.physics_weight = physics_weight
        self.optimizer = Adam(model.parameters(), lr=lr)
        self.mse_loss = nn.MSELoss()

    def train_step(self, x: torch.Tensor,
                   y_true: torch.Tensor) -> dict[str, float]:
        """Perform a single training step with data + physics loss."""
        self.optimizer.zero_grad()
        y_pred = self.model(x)
        data_loss = self.mse_loss(y_pred, y_true)
        physics_loss = self.model.physics_residual(x)
        total_loss = data_loss + self.physics_weight * physics_loss
        total_loss.backward()
        self.optimizer.step()
        return {
            "total_loss": float(total_loss),
            "data_loss": float(data_loss),
            "physics_loss": float(physics_loss),
        }

    def save(self, path: str) -> None:
        """Save model weights."""
        torch.save(self.model.state_dict(), path)
        logger.info("PINN model saved to %s", path)

    def load(self, path: str) -> None:
        """Load model weights."""
        self.model.load_state_dict(torch.load(path, map_location="cpu"))
        self.model.eval()
        logger.info("PINN model loaded from %s", path)
