import pytest
from unittest.mock import patch
from app.processors.text import TextProcessor


class TestTextUnit:

    @pytest.fixture
    def mock_deps(self):
        with patch('app.processors.text.Scanner') as scanner, \
                patch('app.processors.text.Embedder') as embedder, \
                patch('app.processors.text.PrivacyEngine') as privacy:
            yield {
                "scanner": scanner.return_value,
                "embedder": embedder.return_value,
                "privacy": privacy.return_value
            }

    def test_process_flow(self, mock_deps):
        """
        Scenario: Standard text input.
        Expectation: Scan -> Redact -> Vectorize -> Noise.
        """
        mock_deps['scanner'].scan.return_value = []
        mock_deps['scanner'].redact.return_value = "Clean text"
        mock_deps['embedder'].get_vector.return_value = [1.0, 0.0]
        mock_deps['privacy'].add_noise.return_value = [0.9, 0.1]

        processor = TextProcessor()
        result = processor.process("Raw input", epsilon=0.5)
        mock_deps['scanner'].scan.assert_called_once_with("Raw input")
        mock_deps['scanner'].redact.assert_called_once()
        mock_deps['embedder'].get_vector.assert_called_once_with("Clean text")
        assert processor.privacy_engine.epsilon == 0.5
        mock_deps['privacy'].add_noise.assert_called_once()

        assert "metrics" in result
        assert result["metrics"]["epsilon"] == 0.5