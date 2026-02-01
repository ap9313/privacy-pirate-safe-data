import base64
import requests
from app.config import OLLAMA_BASE_URL, VISION_MODEL, TIMEOUT_SECONDS, VISION_ANALYSIS_PROMPT, \
    VISION_PDF_ANALYSIS_PROMPT


class VisionEngine:
    def __init__(self):
        self.url = f"{OLLAMA_BASE_URL}/api/generate"
        self.model = VISION_MODEL

    def describe_image(self, image_bytes: bytes) -> str:
        """Uses the Ollama Vision Model to describe the visual content."""
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "model": self.model,
            "prompt": VISION_ANALYSIS_PROMPT,
            "images": [img_b64],
            "stream": False
        }

        try:
            response = requests.post(self.url, json=payload, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.json().get("response", "No description generated.")
        except Exception as e:
            print(f"[VISION ERROR]: {e}")
            return "Error generating image description."

    def describe_pdf_content(self, image_bytes: bytes) -> str:
        """Uses the Ollama Vision Model to describe the content of the pdf."""
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "model": self.model,
            "prompt": VISION_PDF_ANALYSIS_PROMPT,
            "images": [img_b64],
            "stream": False
        }

        try:
            response = requests.post(self.url, json=payload, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.json().get("response", "No description generated.")
        except Exception as e:
            print(f"[VISION ERROR]: {e}")
            return "Error generating PDF description."