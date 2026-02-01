from typing import Dict, Any
import numpy as np
from app.processors.base import BaseProcessor
from app.core.scanner import Scanner
from app.core.embedder import Embedder
from app.core.privacy import PrivacyEngine
from app.config import L1_SENSITIVITY


class TextProcessor(BaseProcessor):
    def __init__(self):
        self.scanner = Scanner()
        self.embedder = Embedder()
        self.privacy_engine = PrivacyEngine()

    def process(self, input_text: str, epsilon: float) -> Dict[str, Any]:
        findings = self.scanner.scan(input_text)
        safe_text = self.scanner.redact(input_text, findings)
        raw_vector = self.embedder.get_vector(safe_text)

        self.privacy_engine.epsilon = epsilon
        safe_vector = self.privacy_engine.add_noise(raw_vector)

        utility_score = self.calculate_utility_score(raw_vector, np.array(safe_vector))

        return {
            "original_content": input_text,
            "safe_content": safe_text,
            "audit_log": findings,
            "safe_vector": self.format_vector(safe_vector),
            "metrics": {
                "utility_score": utility_score,
                "epsilon": epsilon
            }
        }