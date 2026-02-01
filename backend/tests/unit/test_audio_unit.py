import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from app.processors.audio import AudioProcessor


class TestAudioUnit:

    @pytest.fixture
    def mock_deps(self):
        """
        Patches all external dependencies: Whisper, Scanner, Embedder, PrivacyEngine.
        This ensures we test logic, not models.
        """
        with patch("app.processors.audio.WhisperModel") as MockWhisper, \
                patch("app.processors.audio.Scanner") as MockScanner, \
                patch("app.processors.audio.Embedder") as MockEmbedder, \
                patch("app.processors.audio.PrivacyEngine") as MockPrivacy:
            mock_whisper_instance = MockWhisper.return_value
            seg1 = MagicMock(text="Hello my name is")
            seg2 = MagicMock(text="John Doe")
            mock_whisper_instance.transcribe.return_value = ([seg1, seg2], None)

            mock_scanner_instance = MockScanner.return_value
            mock_scanner_instance.scan.return_value = [{"text": "John Doe", "label": "PERSON"}]
            mock_scanner_instance.redact.return_value = "Hello my name is <PERSON>"

            mock_embedder_instance = MockEmbedder.return_value
            mock_embedder_instance.get_vector.return_value = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

            mock_privacy_instance = MockPrivacy.return_value
            mock_privacy_instance.add_noise.return_value = np.array([0.11, 0.21, 0.31, 0.41, 0.51])

            yield {
                "whisper": mock_whisper_instance,
                "scanner": mock_scanner_instance,
                "embedder": mock_embedder_instance,
                "privacy": mock_privacy_instance
            }

    def test_initialization(self, mock_deps):
        """Test that the processor initializes all components correctly."""
        processor = AudioProcessor()
        assert processor.model is not None
        assert processor.scanner is not None
        assert processor.embedder is not None

    def test_process_flow_success(self, mock_deps):
        """
        Scenario: Normal audio processing.
        Expectation:
        1. Transcribe is called.
        2. Segments are joined ("Hello my name is" + " " + "John Doe").
        3. Scanner scans that text.
        4. Redactor redacts that text.
        5. Vector is generated and noise added.
        """
        processor = AudioProcessor()

        result = processor.process("fake/path/audio.wav")
        mock_deps["whisper"].transcribe.assert_called_once_with("fake/path/audio.wav")

        expected_text = "Hello my name is John Doe"
        assert result["original_content"] == expected_text

        mock_deps["scanner"].scan.assert_called_once_with(expected_text)

        mock_deps["scanner"].redact.assert_called_once()
        assert result["safe_content"] == "Hello my name is <PERSON>"

        mock_deps["embedder"].get_vector.assert_called_once_with("Hello my name is <PERSON>")
        mock_deps["privacy"].add_noise.assert_called_once()

        assert isinstance(result["vector_preview"], list)
        assert len(result["vector_preview"]) == 5
        assert result["audit_log"][0]["text"] == "John Doe"

    def test_process_model_missing(self, mock_deps):
        """Test graceful failure if model fails to load."""
        processor = AudioProcessor()
        processor.model = None
        result = processor.process("fake.wav")
        assert "error" in result
        assert result["error"] == "Whisper model not loaded"