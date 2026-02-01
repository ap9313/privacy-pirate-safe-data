import pytest
from pathlib import Path
from app.core.vision import VisionEngine


class TestVisionIntegration:
    """
    REQUIRES:
    1. Ollama running (ollama serve)
    2. Vision model pulled (ollama pull llama3.2-vision)
    3. 'tests/samples/selfie_test.jpg' to exist
    """

    @pytest.fixture
    def engine(self):
        return VisionEngine()

    @pytest.fixture
    def samples_dir(self):
        return Path(__file__).parents[1] / "samples"

    def test_live_image_description(self, engine, samples_dir):
        """
        Scenario: Send a real image (selfie) to local Ollama.
        Expectation: Receive a textual description describing a face/person.
        """
        image_path = samples_dir / "selfie_test.jpg"
        if not image_path.exists():
            pytest.skip(f"Skipping: Test image not found at {image_path}")

        print(f"\n[Vision Int] Sending {image_path.name} to model {engine.model}...")
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        description = engine.describe_image(image_bytes)
        print(f"[Vision Int] Result: {description}")
        assert isinstance(description, str)
        assert len(description) > 10, "Description was too short to be valid."
        assert description != "Error generating image description.", "Connection to Ollama failed."

        keywords = ["person", "man", "woman", "face", "selfie", "human", "drawing", "sketch"]
        assert any(k in description.lower() for k in keywords), \
            f"Description '{description}' did not contain expected keywords."