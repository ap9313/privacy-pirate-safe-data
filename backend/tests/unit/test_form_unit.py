import pytest
from unittest.mock import patch, MagicMock
from app.processors.form import FormProcessor


class TestFormUnit:

    @pytest.fixture
    def mock_deps(self):
        with patch('app.processors.form.Scanner') as scanner, \
                patch('app.processors.form.Embedder') as embedder, \
                patch('app.processors.form.PrivacyEngine') as privacy:
            yield {
                "scanner": scanner.return_value,
                "embedder": embedder.return_value,
                "privacy": privacy.return_value
            }

    def test_process_flattens_and_scans(self, mock_deps):
        """
        Scenario: Input dictionary with 2 fields.
        Expectation: Both fields scanned, redacted, and audit log populated.
        """
        mock_deps['scanner'].scan.return_value = [{"text": "secret", "label": "KEY"}]
        mock_deps['scanner'].redact.return_value = "<REDACTED>"
        mock_deps['embedder'].get_vector.return_value = [0.1, 0.2]
        mock_deps['privacy'].add_noise.return_value = [0.11, 0.22]

        processor = FormProcessor()

        input_data = {"field1": "value1", "field2": "value2"}
        result = processor.process(input_data, epsilon=1.0)

        assert mock_deps['scanner'].scan.call_count == 2
        assert len(result['audit_log']) == 2
        assert result['audit_log'][0]['field'] in ["field1", "field2"]

        combined_call = mock_deps['embedder'].get_vector.call_args[0][0]
        assert "field1: <REDACTED>" in combined_call
        assert "field2: <REDACTED>" in combined_call

    def test_process_handles_non_string_types(self, mock_deps):
        """Test robust handling of integers/booleans."""
        processor = FormProcessor()
        mock_deps['scanner'].redact.return_value = "123"

        input_data = {"age": 123, "active": True}
        result = processor.process(input_data, epsilon=1.0)

        assert result['safe_content']['age'] == "123"