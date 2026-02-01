import pytest
from unittest.mock import patch, MagicMock
from backend.app.ner.vision import VisionEngine
from app.config import OLLAMA_BASE_URL, VISION_MODEL


class TestVisionUnit:

    @pytest.fixture
    def engine(self):
        return VisionEngine()

    def test_initialization(self, engine):
        """Test that config values are loaded correctly."""
        assert engine.url == f"{OLLAMA_BASE_URL}/api/generate"
        assert engine.model == VISION_MODEL

    @patch('app.core.vision.requests.post')
    def test_describe_image_success(self, mock_post, engine):
        """
        Scenario: API returns a valid 200 OK response with a description.
        Expectation: Returns the description string.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "A person holding a passport."}
        mock_post.return_value = mock_response

        dummy_bytes = b"fake_image_data"
        result = engine.describe_image(dummy_bytes)
        assert result == "A person holding a passport."

        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        assert payload['model'] == engine.model
        assert payload['stream'] is False
        assert len(payload['images']) == 1

    @patch('app.core.vision.requests.post')
    def test_describe_image_api_failure(self, mock_post, engine):
        """
        Scenario: API returns a 500 error or connection fails.
        Expectation: Returns the fallback error message (does not crash).
        """
        # Simulate a crash/exception
        mock_post.side_effect = Exception("Connection refused")

        result = engine.describe_image(b"data")

        assert result == "Error generating image description."

    @patch('app.core.vision.requests.post')
    def test_describe_image_empty_response(self, mock_post, engine):
        """
        Scenario: API returns 200 but the JSON is missing the 'response' key.
        Expectation: Returns default 'No description generated.'
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Empty JSON
        mock_post.return_value = mock_response

        result = engine.describe_image(b"data")

        assert result == "No description generated."