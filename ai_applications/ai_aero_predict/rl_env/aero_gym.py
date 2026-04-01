import gymnasium as gym
from gymnasium import spaces
import numpy as np

class AeroOptimizationEnv(gym.Env):
    """
    Gymnasium Environment for Aerodynamic Component Optimization.
    The agent adjusts wing angles/slots to minimize drag while maintaining downforce.
    """
    def __init__(self):
        super(AeroOptimizationEnv, self).__init__()
        # Actions: [wing_angle_delta, slot_gap_delta] (-1.0 to 1.0)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)
        
        # Observation: [current_angle, current_gap, airspeed, drag, lift]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(5,), dtype=np.float32)
        
        self.state = np.array([12.0, 5.0, 300.0, 150.0, 80.0], dtype=np.float32)
        self.steps = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array([12.0, 5.0, 300.0, 150.0, 80.0], dtype=np.float32)
        self.steps = 0
        return self.state, {}

    def step(self, action):
        self.steps += 1
        # Update physical state (Simple linear model for demo)
        angle_delta, gap_delta = action
        self.state[0] += angle_delta
        self.state[1] += gap_delta
        
        # Calculate Reward: Penalize Drag, Reward Lift/Drag ratio
        drag = 0.5 * self.state[3] * (1.0 + 0.1 * angle_delta)
        lift = 0.5 * self.state[4] * (1.0 + 0.3 * angle_delta)
        
        reward = (lift / max(drag, 1.0)) - (drag * 0.01)
        
        terminated = self.steps > 50
        truncated = False
        
        return self.state, reward, terminated, truncated, {}

if __name__ == "__main__":
    env = AeroOptimizationEnv()
    obs, _ = env.reset()
    for _ in range(5):
        action = env.action_space.sample()
        obs, reward, term, trunc, info = env.step(action)
        print(f"Action: {action}, Reward: {reward:.4f}")
