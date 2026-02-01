import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.core.embedder import Embedder
from app.config import OLLAMA_BASE_URL, EMBED_MODEL


class TestEmbedderUnit:

    def test_initialization(self):
        """Test that the embedder loads config correctly."""
        embedder = Embedder()
        assert embedder.url == f"{OLLAMA_BASE_URL}/api/embeddings"
        assert embedder.model == EMBED_MODEL

    @patch('app.core.embedder.requests.post')
    def test_get_vector_success(self, mock_post):
        """
        Scenario: API returns a valid embedding.
        Expectation: Returns a numpy array of float32.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        fake_vector = [0.1, 0.5, -0.2]
        mock_response.json.return_value = {"embedding": fake_vector}
        mock_post.return_value = mock_response

        embedder = Embedder()
        vector = embedder.get_vector("Test text")

        assert isinstance(vector, np.ndarray)
        assert vector.dtype == np.float32
        assert len(vector) == 3
        assert vector[0] == 0.1

        args, kwargs = mock_post.call_args
        assert kwargs['json']['prompt'] == "Test text"

    @patch('app.core.embedder.requests.post')
    def test_get_vector_connection_error_fallback(self, mock_post):
        """
        Scenario: Ollama is down or connection times out.
        Expectation: Returns a fallback Zero-Vector (size 768).
        """
        mock_post.side_effect = Exception("Connection Refused")

        embedder = Embedder()
        vector = embedder.get_vector("This will fail")

        assert isinstance(vector, np.ndarray)
        assert len(vector) == 768
        assert np.all(vector == 0)

    @patch('app.core.embedder.requests.post')
    def test_get_vector_empty_response(self, mock_post):
        """
        Scenario: API returns 200 OK but missing 'embedding' field.
        Expectation: Raises ValueError internally, catches it, returns Zero-Vector.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  
        mock_post.return_value = mock_response

        embedder = Embedder()
        vector = embedder.get_vector("Test")

        assert np.all(vector == 0)