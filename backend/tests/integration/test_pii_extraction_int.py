import pytest
import os
from pathlib import Path
from PIL import Image, ImageDraw
from app.ner.pii_image_extractor import PIIImageExtractor, PIIExtractionResult


class TestPIIExtractorIntegration:
    """
    REQUIRES: 'ollama serve' running locally.
    """

    @pytest.fixture
    def real_extractor(self):
        model = "qwen3-vl:2b"
        return PIIImageExtractor(model_name=model)

    @pytest.fixture
    def generated_pii_image(self, tmp_path):
        """Generates a temporary image with clear text for testing."""
        path = tmp_path / "test_pii.png"
        img = Image.new('RGB', (400, 200), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "Name: John Smith", fill=(0, 0, 0))
        d.text((10, 30), "Email: john.smith@test.com", fill=(0, 0, 0))
        img.save(path)
        return path

    def test_live_connection_to_ollama(self, real_extractor, generated_pii_image):
        """
        Scenario: Send a real image to the local Ollama instance.
        Expectation: 200 OK and a parsed result.
        """
        print(f"\n[PII Int] Connecting to {real_extractor.api_url} with model {real_extractor.model_name}...")

        try:
            result = real_extractor.extract_from_file(generated_pii_image)
            assert isinstance(result, PIIExtractionResult)
            print(f"[PII Int] Model Output: {result.model_dump_json(indent=2)}")
            assert isinstance(result.names, list)
            assert isinstance(result.emails, list)

        except Exception as e:
            pytest.fail(f"Integration test failed to talk to Ollama: {e}")