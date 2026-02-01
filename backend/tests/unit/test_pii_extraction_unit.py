import pytest
import base64
from PIL import Image
from unittest.mock import patch, MagicMock
from app.ner.pii_image_extractor import PIIImageExtractor, PIIExtractionResult
from app.config import OLLAMA_BASE_URL
import requests
from pydantic import ValidationError

class TestPIIImageExtractorUnit:

    @pytest.fixture
    def extractor(self):
        """Creates an instance for testing."""
        return PIIImageExtractor(model_name="test-model")

    @pytest.fixture
    def dummy_image(self):
        """Creates a tiny 10x10 white image for testing encoding."""
        return Image.new("RGB", (10, 10), color="white")

    def test_initialization(self, extractor):
        """Test that the API URL is constructed correctly from config."""
        expected_url = f"{OLLAMA_BASE_URL}/api/chat"
        assert extractor.api_url == expected_url
        assert extractor.model_name == "test-model"

    def test_image_encoding(self, extractor, dummy_image):
        """Test that _encode_image returns a valid base64 string."""
        encoded = extractor._encode_image(dummy_image)
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        try:
            decoded = base64.b64decode(encoded)
            assert len(decoded) > 0
        except Exception:
            pytest.fail("Image encoding produced invalid base64 string")

    @patch("app.ner.pii_image_extractor.requests.post")
    def test_extract_success(self, mock_post, extractor, dummy_image):
        """
        Scenario: API returns 200 OK and valid JSON.
        Expectation: Returns a populated PIIExtractionResult.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": '{"names": ["John Doe"], "emails": ["john@example.com"]}'
            }
        }
        mock_post.return_value = mock_response
        result = extractor.extract_from_file(dummy_image)
        assert isinstance(result, PIIExtractionResult)
        assert result.names == ["John Doe"]
        assert result.emails == ["john@example.com"]
        assert result.credit_cards == []

    @patch("app.ner.pii_image_extractor.requests.post")
    def test_extract_api_failure(self, mock_post, extractor, dummy_image):
        """
        Scenario: API connection fails or returns 500.
        Expectation: Should raise an Exception (because of response.raise_for_status).
        """

        mock_post.side_effect = requests.exceptions.ConnectionError("Connection Refused")
        with pytest.raises(requests.exceptions.ConnectionError):
            extractor.extract_from_file(dummy_image)

    @patch("app.ner.pii_image_extractor.requests.post")
    def test_extract_invalid_json_response(self, mock_post, extractor, dummy_image):
        """
        Scenario: API returns text that is NOT valid JSON (e.g. conversational text).
        Expectation: Pydantic should raise a ValidationError.
        """

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": "Sure, I found a name: John Doe."  # Not JSON!
            }
        }
        mock_post.return_value = mock_response
        with pytest.raises(ValidationError):
            extractor.extract_from_file(dummy_image)