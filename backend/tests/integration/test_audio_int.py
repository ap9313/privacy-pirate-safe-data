import pytest
import os
from app.processors.audio import AudioProcessor


class TestAudioIntegration:
    """
    REQUIRES:
    1. backend/tests/samples/test_audio.wav (We just generated this)
    2. ffmpeg installed (brew install ffmpeg) - required by Whisper
    """

    def test_audio_transcription_and_redaction(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        audio_path = os.path.join(base_dir, "samples", "test_audio.wav")

        if not os.path.exists(audio_path):
            pytest.fail(f"Audio sample not found at {audio_path}. Did you run the 'say' command?")

        print(f"\n[Integration] Processing Audio: {audio_path}")

        processor = AudioProcessor()

        result = processor.process(audio_path, epsilon=1.0)

        original = result['original_content']
        safe = result['safe_content']

        print(f"[Integration] Heard: '{original}'")
        print(f"[Integration] Clean: '{safe}'")

        assert "John" in original or "Doe" in original, "Whisper failed to transcribe the name."

        assert "John" not in safe, "PII was not redacted!"
        assert "<PERSON" in safe, "Redaction tag missing."

        if "sk-" in original:
            assert "sk-" not in safe, "API Key leaked!"

    def test_multi_pii_audio(self):
        """Test 2: Complex PII (Name, Location, Email, Phone, SSN)"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        audio_path = os.path.join(base_dir, "samples", "test_multi_pii.wav")

        if not os.path.exists(audio_path):
            pytest.skip(f"Multi-PII sample not found at {audio_path}. Skipping.")

        print(f"\n[Integration] Processing Multi-PII: {audio_path}")
        processor = AudioProcessor()

        result = processor.process(audio_path, epsilon=1.0)
        original = result['original_content']
        safe = result['safe_content']

        print(f"[Integration] Heard:   '{original}'")
        print(f"[Integration] Cleaned: '{safe}'")

        assert "Maria" in original, "Whisper failed to hear 'Maria'"
        assert "Maria" not in safe, "Name 'Maria' leaked!"
        assert "<PERSON" in safe, "Missing <PERSON> tag"

        assert "Budapest" in original, "Whisper failed to hear 'Budapest'"
        assert "Budapest" not in safe, "Location 'Budapest' leaked!"
        assert "<LOCATION" in safe, "Missing <LOCATION> tag"

        assert "@" in original or "at gmail" in original.lower(), "Whisper failed to hear email structure"
        assert "maria.kovacs" not in safe, "Email handle leaked!"
        assert "1234567" not in safe, "Phone number sequence leaked!"
        assert "123-45" not in safe and "123 dash 45" not in safe, "SSN leaked!"