import os
from faster_whisper import WhisperModel
from app.processors.base import BaseProcessor
from app.config import DATA_DIR, WHISPER_MODEL_SIZE, WHISPER_DEVICE

class AudioProcessor(BaseProcessor):
    def __init__(self):
        model_path = os.path.join(DATA_DIR, "models", f"whisper-{WHISPER_MODEL_SIZE}")
        print(f"Loading Whisper Audio Model ({WHISPER_MODEL_SIZE})...")
        self.model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type="int8",
            download_root=model_path
        )

    def extract_text(self, file_path: str) -> str:
        """Transcribe text from audio file using Whisper."""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        segments, _ = self.model.transcribe(file_path)
        return " ".join([segment.text for segment in segments])

    def process(self, *args, **kwargs): pass