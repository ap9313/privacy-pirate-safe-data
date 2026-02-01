from typing import Dict, Any
from app.processors.base import BaseProcessor
from app.core.scanner import Scanner
from app.core.embedder import Embedder
from app.core.privacy import PrivacyEngine
from app.config import L1_SENSITIVITY


class FormProcessor(BaseProcessor):
    def __init__(self):
        self.scanner = Scanner()
        self.embedder = Embedder()
        self.privacy_engine = PrivacyEngine()

    def process(self, input_data: Dict[str, Any], epsilon: float) -> Dict[str, Any]:
        safe_data = {}
        audit_log = []
        combined_text_for_vector = ""

        for key, value in input_data.items():
            str_value = str(value)
            findings = self.scanner.scan(str_value)
            safe_value = self.scanner.redact(str_value, findings)
            safe_data[key] = safe_value

            for f in findings:
                f['field'] = key
                audit_log.append(f)

            combined_text_for_vector += f"{key}: {safe_value}. "

        raw_vector = self.embedder.get_vector(combined_text_for_vector)

        self.privacy_engine.epsilon = epsilon
        safe_vector = self.privacy_engine.add_noise(raw_vector)

        return {
            "original_content": input_data,
            "safe_content": safe_data,
            "audit_log": audit_log,
            "safe_vector": self.format_vector(safe_vector)
        }