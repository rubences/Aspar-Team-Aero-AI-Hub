"""
RL Environment — Gymnasium environment for aerodynamic design optimization.
Provides a reinforcement learning environment where an agent can explore
different aerodynamic configurations to maximize downforce/drag ratio.
"""

import logging
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

logger = logging.getLogger(__name__)


class AeroDesignEnv(gym.Env):
    """
    Gymnasium environment for aerodynamic wing design optimization.

    The agent controls front wing angle, rear wing angle, and DRS settings.
    The reward function balances downforce, drag, and stability constraints.

    Observation space: current aero parameters + performance metrics.
    Action space: continuous adjustments to aero configuration.
    """

    metadata = {"render_modes": ["human", "rgb_array"]}

    # Aero parameter bounds
    FRONT_WING_MIN, FRONT_WING_MAX = 0.0, 45.0  # degrees
    REAR_WING_MIN, REAR_WING_MAX = 0.0, 60.0    # degrees
    DRS_MIN, DRS_MAX = 0.0, 1.0                  # 0=closed, 1=open

    # Performance metric bounds (normalized)
    DOWNFORCE_MAX = 2000.0  # Newtons
    DRAG_MAX = 500.0        # Newtons

    def __init__(self, target_downforce: float = 1500.0,
                 max_drag: float = 300.0) -> None:
        super().__init__()
        self.target_downforce = target_downforce
        self.max_drag = max_drag
        self.step_count = 0
        self.max_steps = 200

        # Observation: [fw_angle, rw_angle, drs, downforce, drag, balance]
        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0, 0.0, 0.0, 0.0, -1.0], dtype=np.float32),
            high=np.array([45.0, 60.0, 1.0, 2000.0, 500.0, 1.0], dtype=np.float32),
        )

        # Actions: delta changes to [fw_angle, rw_angle, drs]
        self.action_space = spaces.Box(
            low=np.array([-2.0, -2.0, -0.1], dtype=np.float32),
            high=np.array([2.0, 2.0, 0.1], dtype=np.float32),
        )

        self._state = np.zeros(6, dtype=np.float32)

    def reset(self, *, seed: int | None = None,
              options: dict[str, Any] | None = None) -> tuple[np.ndarray, dict]:
        """Reset the environment to a random initial configuration."""
        super().reset(seed=seed)
        self.step_count = 0
        fw_angle = self.np_random.uniform(10.0, 30.0)
        rw_angle = self.np_random.uniform(15.0, 40.0)
        drs = 0.0
        downforce, drag, balance = self._simulate_aero(fw_angle, rw_angle, drs)
        self._state = np.array([fw_angle, rw_angle, drs, downforce, drag, balance],
                                dtype=np.float32)
        return self._state.copy(), {}

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, bool, dict]:
        """Apply an action and advance the environment."""
        self.step_count += 1
        fw_angle = float(np.clip(
            self._state[0] + action[0], self.FRONT_WING_MIN, self.FRONT_WING_MAX
        ))
        rw_angle = float(np.clip(
            self._state[1] + action[1], self.REAR_WING_MIN, self.REAR_WING_MAX
        ))
        drs = float(np.clip(self._state[2] + action[2], self.DRS_MIN, self.DRS_MAX))

        downforce, drag, balance = self._simulate_aero(fw_angle, rw_angle, drs)
        self._state = np.array([fw_angle, rw_angle, drs, downforce, drag, balance],
                                dtype=np.float32)

        reward = self._compute_reward(downforce, drag, balance)
        terminated = False
        truncated = self.step_count >= self.max_steps

        return self._state.copy(), reward, terminated, truncated, {
            "downforce": downforce, "drag": drag, "balance": balance
        }

    def _simulate_aero(self, fw_angle: float, rw_angle: float,
                        drs: float) -> tuple[float, float, float]:
        """Simplified aerodynamic simulation (placeholder for PINN call)."""
        downforce = (fw_angle * 20.0 + rw_angle * 15.0) * (1.0 - 0.3 * drs)
        drag = (fw_angle * 5.0 + rw_angle * 4.0) * (1.0 - 0.5 * drs)
        balance = (fw_angle * 20.0) / max(downforce, 1.0) - 0.5
        return float(downforce), float(drag), float(balance)

    def _compute_reward(self, downforce: float, drag: float,
                         balance: float) -> float:
        """Compute reward balancing downforce, drag efficiency, and balance."""
        downforce_reward = min(downforce / self.target_downforce, 1.0)
        drag_penalty = max(0.0, (drag - self.max_drag) / self.max_drag)
        balance_penalty = abs(balance) * 0.5
        return float(downforce_reward - drag_penalty - balance_penalty)
