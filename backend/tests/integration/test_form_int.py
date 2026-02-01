import pytest
import numpy as np
from app.processors.form import FormProcessor


class TestFormIntegration:
    """
    Verifies the FormProcessor logic in isolation.
    Ensures that structured JSON data is correctly scanned, redacted, and vectorized.
    """

    @pytest.fixture
    def processor(self):
        return FormProcessor()

    def test_pii_redaction_in_fields(self, processor):
        """
        Scenario: A user submits a JSON form with varied PII.
        Expectation:
        1. The keys (fields) remain unchanged.
        2. Strong PII (Email, Phone) is definitely redacted.
        3. The audit log identifies which field contained the PII.
        """
        input_data = {
            "username": "super_coder",
            "full_name": "John Doe",
            "contact_email": "elon@spacex.com",
            "phone_number": "555-123-4567",
            "bio": "I love rockets."
        }

        print(f"\n[Form Int] Processing: {input_data}")
        result = processor.process(input_data, epsilon=1.0)

        safe_data = result['safe_content']
        audit_log = result['audit_log']
        print(f"[Form Int] Safe Data: {safe_data}")
        assert safe_data['username'] == "super_coder", "Non-PII field was altered!"
        assert "elon@spacex.com" not in safe_data['contact_email'], "Email was not redacted!"
        assert "<EMAIL" in safe_data['contact_email'], "Missing redaction tag for Email"
        assert "555-123-4567" not in safe_data['phone_number'], "Phone number was not redacted!"
        assert "<PHONE" in safe_data['phone_number'], "Missing redaction tag for Phone"
        email_finding = next((f for f in audit_log if 'spacex' in f['text'] or 'elon' in f['text']), None)
        assert email_finding is not None
        assert email_finding['field'] == 'contact_email', "Audit log lost track of the Email field!"
        phone_finding = next((f for f in audit_log if '555-123-4567' in f['text']), None)
        assert phone_finding is not None
        assert phone_finding['field'] == 'phone_number', "Audit log lost track of the Phone field!"

    def test_vector_generation(self, processor):
        """
        Scenario: Process a form.
        Expectation: A single consolidated vector is generated for the entire form context.
        """
        input_data = {"note": "This is a simple form."}
        result = processor.process(input_data, epsilon=1.0)
        vector = result['safe_vector']
        assert isinstance(vector, list)
        assert len(vector) > 0
        assert np.linalg.norm(vector) > 0.0

    def test_numeric_and_boolean_fields(self, processor):
        """
        Scenario: Form contains non-string types (int, bool).
        Expectation: Processor converts them to string safely and doesn't crash.
        """
        input_data = {
            "age": 30,
            "is_active": True,
            "score": 99.9
        }

        result = processor.process(input_data, epsilon=1.0)
        safe_data = result['safe_content']
        assert str(safe_data['age']) == "30"
        assert str(safe_data['is_active']) == "True"