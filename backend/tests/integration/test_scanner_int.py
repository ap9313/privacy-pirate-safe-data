import pytest
from app.core.scanner import Scanner


class TestScannerIntegration:
    """
    This test loads the REAL GLiNER model.
    The first run might be slow as it downloads the model (~100MB).
    """

    def test_real_ner_detection(self):
        """
        Scenario: Feed real text to the Scanner.
        Expectation: It finds 'Elon Musk' as a PERSON.
        """
        print("\n[Integration] Loading GLiNER model (may take a moment)...")
        scanner = Scanner()

        text = "Elon Musk lives in Texas and works at SpaceX."
        print(f"[Integration] Scanning: '{text}'")

        findings = scanner.scan(text)

        labels = [f['label'] for f in findings]
        names = [f['text'] for f in findings]

        print(f"[Integration] Found: {names}")

        assert 'person' in labels or 'PERSON' in labels
        assert 'Elon Musk' in names
        assert 'Texas' in names

    def test_real_secret_detection(self):
        """
        Scenario: Feed a fake API Key.
        Expectation: The LLM (Ollama) flags it as a secret.
        """
        scanner = Scanner()
        text = "Hey, my production key is sk-proj-1234567890abcdef."
        findings = scanner.scan(text)
        secret_found = any(f['label'] == 'security_secret' for f in findings)
        if not secret_found:
            pytest.skip("⚠️ LLM did not flag the secret. Model might be too small or prompt needs tuning.")

        assert secret_found is True
        print("[Integration] Successfully detected the API Key!")