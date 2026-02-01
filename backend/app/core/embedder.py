import sys
import os
import requests
import numpy as np
# Added EMBED_DIMENSION to imports
from app.config import OLLAMA_BASE_URL, EMBED_MODEL, TIMEOUT_SECONDS, EMBED_DIMENSION


class Embedder:
    def __init__(self):
        self.url = f"{OLLAMA_BASE_URL}/api/embeddings"
        self.model = EMBED_MODEL

    def get_vector(self, text: str) -> np.ndarray:
        """Turns text into a raw vector using local Ollama."""
        clean_text = text.replace("\n", " ").strip()

        payload = {
            "model": self.model,
            "prompt": clean_text
        }

        try:
            response = requests.post(self.url, json=payload, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()

            vector = response.json().get("embedding")
            if not vector:
                raise ValueError(f"No embedding returned for model {self.model}")

            return np.array(vector, dtype=np.float32)

        except Exception as e:
            print(f"[EMBEDDER ERROR]: {e}")
            return np.zeros(EMBED_DIMENSION, dtype=np.float32)


if __name__ == "__main__":
    client = Embedder()
    print(f"Using Model: {client.model}")
    test_vec = client.get_vector("Testing config-based embedding.")
    print(f"Vector Preview: {test_vec[:5]}...")