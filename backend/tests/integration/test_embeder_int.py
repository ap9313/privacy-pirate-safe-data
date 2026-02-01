import pytest
import numpy as np
import requests
from app.core.embedder import Embedder


class TestEmbedderIntegration:
    """
    REQUIRES RUNNING OLLAMA INSTANCE
    """

    def test_live_ollama_connection(self):
        """
        Scenario: Connect to localhost and request a real embedding.
        Expectation: We get a non-zero vector back.
        """
        embedder = Embedder()
        print(f"\n[Integration] Pinging Ollama at {embedder.url} with model {embedder.model}...")

        try:
            base_url = embedder.url.replace("/api/embeddings", "")
            requests.get(base_url, timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.fail("Could not connect to Ollama. Is 'ollama serve' running?")

        text = "Integration testing is crucial for winning hackathons."
        vector = embedder.get_vector(text)

        assert isinstance(vector, np.ndarray), "Result must be a numpy array"
        assert vector.dtype == np.float32, "Result must be float32"

        assert vector.shape[0] > 0, f"Vector should have dimensions, got {vector.shape}"

        magnitude = np.linalg.norm(vector)
        assert magnitude > 0.0, "Embedder returned a zero-vector. The model failed to process the text."