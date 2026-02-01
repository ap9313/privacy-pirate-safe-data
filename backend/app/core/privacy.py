import numpy as np
from app.config import (
    DEFAULT_EPSILON,
    L1_SENSITIVITY,
    MIN_EPSILON,
    PRIVACY_BUDGET_THRESHOLD
)


class PrivacyEngine:
    """
    Handles Differential Privacy (DP) mechanisms.
    Implements Laplace Noise for vector perturbations.
    """

    def __init__(self, target_epsilon=None):
        self.epsilon = target_epsilon or DEFAULT_EPSILON
        self.sensitivity = L1_SENSITIVITY

    def add_noise(self, vector: np.ndarray) -> np.ndarray:
        """
        Adds Laplacian noise to an embedding vector to guarantee Differential Privacy.
        Mechanism: f(x) + Lap(sensitivity / epsilon)
        """
        safe_epsilon = max(self.epsilon, MIN_EPSILON)

        scale = self.sensitivity / safe_epsilon
        noise = np.random.laplace(0, scale, vector.shape)

        return vector + noise

    def get_budget_status(self):
        """Returns current privacy budget info (mock implementation for hackathon)"""
        return {
            "current_epsilon": self.epsilon,
            "status": "Healthy" if self.epsilon > PRIVACY_BUDGET_THRESHOLD else "Depleted"
        }