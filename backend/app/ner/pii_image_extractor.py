import base64
import io
from pathlib import Path
from typing import Union, cast
import os
import requests
from PIL import Image
from pydantic import BaseModel, Field

# IMPORT ALL SETTINGS FROM CONFIG
from app.config import (
    OLLAMA_BASE_URL,
    VISION_MODEL,
    TIMEOUT_SECONDS,
    PII_TEST_DOCUMENT_IMAGE,
    PII_EXTRACTOR_SYSTEM_PROMPT,
    PII_IMAGE_MAX_DIMENSION,
    PII_IMAGE_QUALITY,
    PII_MODEL_TEMPERATURE
)

ImageInput = Union[str, Path, Image.Image]


class PIIExtractionResult(BaseModel):
    names: list[str] = Field(default_factory=list)
    id_numbers: list[str] = Field(default_factory=list)
    addresses: list[str] = Field(default_factory=list)
    date_of_birth: list[str] = Field(default_factory=list)
    phone_numbers: list[str] = Field(default_factory=list)
    emails: list[str] = Field(default_factory=list)
    social_security_numbers: list[str] = Field(default_factory=list)
    api_keys: list[str] = Field(default_factory=list)
    credit_cards: list[str] = Field(default_factory=list)

    def tolist(self) -> list[str]:
        items: list[str] = []
        items.extend(self.names)
        items.extend(self.id_numbers)
        items.extend(self.addresses)
        items.extend(self.date_of_birth)
        items.extend(self.phone_numbers)
        items.extend(self.emails)
        items.extend(self.social_security_numbers)
        items.extend(self.api_keys)
        items.extend(self.credit_cards)
        return items


class PIIImageExtractor:
    def __init__(self, model_name=VISION_MODEL):
        self.model_name = model_name
        self.api_url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
        self.system_prompt = PII_EXTRACTOR_SYSTEM_PROMPT

    def _encode_resized_jpeg(self, img: Image.Image) -> str:
        img.thumbnail((PII_IMAGE_MAX_DIMENSION, PII_IMAGE_MAX_DIMENSION), Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        buffer = io.BytesIO()
        img.save(
            buffer,
            format="JPEG",
            quality=PII_IMAGE_QUALITY,
            optimize=True
        )
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _encode_image(self, image_source: ImageInput) -> str:
        if isinstance(image_source, Image.Image):
            working = cast(Image.Image, image_source).copy()
            try:
                return self._encode_resized_jpeg(working)
            finally:
                working.close()

        path_like = Path(image_source)
        with Image.open(path_like) as opened:
            return self._encode_resized_jpeg(opened)

    def extract_from_file(self, image_source: ImageInput) -> PIIExtractionResult:
        try:
            base64_image = self._encode_image(image_source)

            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": "Extract PII. Return JSON.",
                        "images": [base64_image]
                    },
                ],
                "stream": False,
                "temperature": PII_MODEL_TEMPERATURE,
                "format": "json"
            }

            response = requests.post(self.api_url, json=payload, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()

            data = response.json()
            if "message" not in data or "content" not in data["message"]:
                print("[PII Extractor] Warning: Unexpected API response format.")
                return PIIExtractionResult()

            content = data["message"]["content"].strip()

            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            if not content:
                print("[PII Extractor] Warning: Model returned empty content.")
                return PIIExtractionResult()

            return PIIExtractionResult.model_validate_json(content)

        except Exception as e:
            print(f"[PII Extractor] Error processing image: {e}")
            return PIIExtractionResult()


if __name__ == "__main__":
    if os.path.exists(PII_TEST_DOCUMENT_IMAGE):
        extractor = PIIImageExtractor()
        result = extractor.extract_from_file(PII_TEST_DOCUMENT_IMAGE)
        print(result.model_dump_json(indent=2))