import pytest
import numpy as np
from app.processors.text import TextProcessor


class TestTextIntegration:
    """
    Verifies the TextProcessor logic in isolation.
    Ensures that raw text is correctly scanned, redacted, and vectorized with noise.
    """

    @pytest.fixture
    def processor(self):
        return TextProcessor()

    def test_pii_redaction_flow(self, processor):
        """
        Scenario: Process a sentence containing a name and an email.
        Expectation:
        1. 'audit_log' finds the entities.
        2. 'safe_content' has tags instead of real data.
        """
        input_text = "My name is John Doe and my email is john.doe@example.com."

        print(f"\n[Text Int] Processing: '{input_text}'")
        result = processor.process(input_text, epsilon=1.0)

        safe_text = result['safe_content']
        audit_log = result['audit_log']

        print(f"[Text Int] Safe Text: '{safe_text}'")

        assert "John Doe" not in safe_text, "Name leaked in safe text!"
        assert "john.doe@example.com" not in safe_text, "Email leaked in safe text!"
        assert "<PERSON" in safe_text or "<EMAIL" in safe_text, "Redaction tags missing!"

        found_email = any(f['label'] == 'email_address' or 'email' in f['label'] for f in audit_log)
        assert found_email, "Audit log failed to record the email finding."

    def test_vector_noise_application(self, processor):
        """
        Scenario: Process the same text twice.
        Expectation:
        1. Vectors are not identical (Noise is stochastic).
        2. With HIGH Epsilon (Low Privacy), vectors remain similar (High Utility).
        """
        text = "This is a test sentence for vector analysis."

        test_epsilon = 15.0

        result1 = processor.process(text, epsilon=test_epsilon)
        vec1 = np.array(result1['safe_vector'])

        result2 = processor.process(text, epsilon=test_epsilon)
        vec2 = np.array(result2['safe_vector'])

        assert len(vec1) == 768, "Vector dimension incorrect (should be 768 for Nomic/BERT)."

        assert not np.array_equal(vec1, vec2), "Privacy Engine failed to add random noise!"

        dot = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        similarity = dot / (norm_a * norm_b)

        print(f"[Text Int] Vector Similarity (Epsilon={test_epsilon}): {similarity:.4f}")
        assert similarity > 0.8, f"Utility destroyed even at Epsilon {test_epsilon}!"

    def test_utility_metrics(self, processor):
        """
        Scenario: Check the 'metrics' dictionary in the response.
        Expectation: Utility score is calculated and returned.
        """
        text = "Simple text."
        result = processor.process(text, epsilon=1.0)

        metrics = result['metrics']
        assert 'utility_score' in metrics
        assert 'epsilon' in metrics
        assert metrics['epsilon'] == 1.0
        assert 0 <= metrics['utility_score'] <= 100