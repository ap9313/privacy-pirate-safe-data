from abc import ABC, abstractmethod
from typing import Dict, Any, List
import numpy as np


class BaseProcessor(ABC):
    """
    Ensures every processor returns data the frontend can render blindly.
    """

    @abstractmethod
    def process(self, input_data: Any, epsilon: float) -> Dict[str, Any]:
        pass

    def format_vector(self, vector: np.ndarray) -> List[float]:
        if vector is None:
            return []
        return vector.tolist()

    def calculate_utility_score(self, original_vec: np.ndarray, noisy_vec: np.ndarray) -> float:
        """
        Calculates Cosine Similarity (0-100%) between the raw and protected vector.
        This provides a 'Visual' metric for the UI:
        "How much meaning did we keep?"
        """
        if original_vec is None or noisy_vec is None:
            return 0.0
        dot = np.dot(original_vec, noisy_vec)
        norm_a = np.linalg.norm(original_vec)
        norm_b = np.linalg.norm(noisy_vec)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        similarity = dot / (norm_a * norm_b)
        return round(max(0.0, min(1.0, float(similarity))) * 100, 2)