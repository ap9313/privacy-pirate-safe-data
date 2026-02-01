import pytest
from unittest.mock import MagicMock, patch
from app.core.scanner import Scanner


class TestScannerUnit:

    @patch('app.core.scanner.GLiNER')
    def test_scanner_initialization(self, mock_gliner):
        """Test that scanner initializes without crashing."""
        scanner = Scanner()
        assert scanner.ner_model is not None
        mock_gliner.from_pretrained.assert_called_once()

    @patch('app.core.scanner.GLiNER')
    def test_boomerang_map_creation(self, mock_gliner):
        """
        Scenario: We found entities.
        Expectation: Convert them to distinct tags (<PERSON_1>, <LOC_1>).
        """
        scanner = Scanner()

        findings = [
            {'text': 'Attila', 'label': 'person', 'score': 0.99},
            {'text': 'Romania', 'label': 'location', 'score': 0.95}
        ]

        entity_map = scanner.create_boomerang_map(findings)

        assert 'Attila' in entity_map
        assert 'Romania' in entity_map
        assert entity_map['Attila'] == '<PERSON_1>'
        assert entity_map['Romania'] == '<LOCATION_1>'

    @patch('app.core.scanner.GLiNER')
    def test_boomerang_restoration(self, mock_gliner):
        """
        Scenario: The AI returns text with tags.
        Expectation: We swap tags back to real names.
        """
        scanner = Scanner()
        entity_map = {'Attila': '<PERSON_1>'}

        ai_response = "Hello <PERSON_1>, you are hired."
        restored = scanner.restore_from_map(ai_response, entity_map)
        assert restored == "Hello Attila, you are hired."

    @patch('app.core.scanner.GLiNER')
    def test_redact_strict_mode(self, mock_gliner):
        """Test standard redaction (just removing PII)."""
        scanner = Scanner()
        text = "Call John at 555-0199."
        findings = [
            {'text': 'John', 'label': 'person', 'start': 5, 'end': 9},
            {'text': '555-0199', 'label': 'phone_number', 'start': 13, 'end': 21}
        ]

        safe_text = scanner.redact(text, findings)
        assert "Call <PERSON>" in safe_text
        assert "at <PHONE_NUMBER>" in safe_text