"""Document processor that blurs unsafe words in PDFs and returns findings."""

from __future__ import annotations
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence

import fitz  # type: ignore[import-not-found]
from PIL import Image, ImageFilter  # type: ignore[import-not-found]

from app.config import DATA_DIR, UPLOAD_DIR
from app.processors.base import BaseProcessor
from app.ner.pii_image_extractor import PIIImageExtractor, PIIExtractionResult
from app.core.scanner import Scanner

DEFAULT_EPSILON = 1.0
DEFAULT_TEST_PDF = Path(DATA_DIR) / "test_data" / "sample.pdf"
RESULTS_DIR = Path(DATA_DIR) / "results"


class DocumentProcessorBlur(BaseProcessor):
    """Blurs predefined unsafe words within a PDF and reports findings."""

    SAFE_PREFIX = "blurred"

    def __init__(self, gliner_scanner: Scanner, scale: int = 2, blur_radius: int = 10):
        self.gliner_scanner = gliner_scanner
        self.scale = scale
        self.blur_radius = blur_radius
        self.pii_extractor = PIIImageExtractor()

    def process(self, input_data: Any, epsilon: float) -> Dict[str, Any]:  # noqa: ARG002
        source_path = Path(str(input_data))
        if not source_path.exists():
            raise FileNotFoundError(f"Document not found: {source_path}")

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        output_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=UPLOAD_DIR)
        output_tmp.close()
        output_path = Path(output_tmp.name)
        doc = fitz.open(str(source_path))

        processed_images: List[Image.Image] = []
        unsafe_words: List[str] = []

        try:
            for page_index in range(len(doc)):
                page = doc[page_index]

                unsafe_page_words: PIIExtractionResult = self.find_unsafe_words(page)
                additional_findings = self.rescan_page_text(page)

                page_word_list = list(unsafe_page_words.tolist())
                additional_values = [value for finding in additional_findings for value in finding.values()]
                page_word_list.extend(additional_values)

                self._extend_unique(unsafe_words, page_word_list)
                self._extend_unique(unsafe_words, additional_values)

                pix = page.get_pixmap(matrix=fitz.Matrix(self.scale, self.scale))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                for rect in self.get_bboxes(page, page_word_list):
                    self._blur_rect(img, rect)

                processed_images.append(img)
        finally:
            doc.close()

        self._write_pdf(processed_images, output_path)

        return {
            "safe_pdf_path": str(output_path),
            "unsafe_words": unsafe_words,
        }

    def rescan_page_text(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Additional scan using the gliner scanner on the page text."""
        try:
            text = page.get_text()
            findings = self.gliner_scanner.scan(text)
            print(f'[DocumentProcessorBlur] Rescanned page {page.number}, found {len(findings)} items.')
            return [{f['label']: f['text']} for f in findings]
        except Exception as e:
            print(f'[DocumentProcessorBlur] Error rescanning page {page.number}: {e}')
            return []

    def find_unsafe_words(self, page: fitz.Page) -> PIIExtractionResult:
        """Mock rule set for unsafe content discovery."""
        matrix = fitz.Matrix(self.scale, self.scale)
        pix = page.get_pixmap(matrix=matrix)
        mode = "RGBA" if pix.alpha else "RGB"
        image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        if image.mode != "RGB":
            image = image.convert("RGB")

        try:
            return self.pii_extractor.extract_from_file(image)
        finally:
            image.close()

    def get_bboxes(self, page: fitz.Page, unsafe_words: Sequence[str]) -> List[fitz.Rect]:
        boxes: List[fitz.Rect] = []
        seen: set[str] = set()
        for word in unsafe_words:
            if not word:
                continue
            for variant in {word, word.lower(), word.upper()}:
                if not variant or variant in seen:
                    continue
                seen.add(variant)
                boxes.extend(page.search_for(variant))
        return boxes

    def _blur_rect(self, image: Image.Image, rect: fitz.Rect) -> None:
        padding = 4
        box = (
            max(int(rect.x0 * self.scale) - padding, 0),
            max(int(rect.y0 * self.scale) - padding, 0),
            int(rect.x1 * self.scale) + padding,
            int(rect.y1 * self.scale) + padding,
        )
        region = image.crop(box)
        blurred = region.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))
        image.paste(blurred, box)

    def _build_output_path(self, source_path: Path) -> Path:
        """Retained for compatibility; currently unused."""
        suffix = source_path.suffix or ".pdf"
        base = source_path.stem
        return source_path.with_name(f"{self.SAFE_PREFIX}_{base}{suffix}")

    def _write_pdf(self, images: List[Image.Image], output_path: Path) -> None:
        if not images:
            raise ValueError("No rendered pages to write")

        first, *rest = images
        first.save(
            str(output_path),
            save_all=True,
            append_images=rest,
            format="PDF",
        )

    def _extend_unique(self, target: List[str], to_add: Sequence[str]) -> None:
        for item in to_add:
            if item not in target:
                target.append(item)


if __name__ == "__main__":  # pragma: no cover - manual run helper
    processor = DocumentProcessorBlur(Scanner())
    result = processor.process(DEFAULT_TEST_PDF, DEFAULT_EPSILON)
    print(f"Redaction complete. Unsafe words: {result['unsafe_words']}")
    print(f"Blurred PDF written to: {result['safe_pdf_path']}")
