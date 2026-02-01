import pytest
import fitz
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.processors.document_blur import DocumentProcessorBlur


class TestDocumentBlurIntegration:

    @pytest.fixture
    def sample_pdf(self, tmp_path):
        """Creates a real PDF file with the word 'SECRET' on it."""
        path = tmp_path / "int_test.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "This is a SECRET document.", fontsize=20)
        doc.save(str(path))
        doc.close()
        return path

    def test_real_pdf_blurring_mechanics(self, sample_pdf):
        """
        Scenario: Run the full processor on a real PDF on disk.
        We mock ONLY the AI detection part to ensure we test the PDF/Image manipulation mechanics deterministically.
        """
        processor = DocumentProcessorBlur(scale=2, blur_radius=20)
        mock_result = MagicMock()
        mock_result.tolist.return_value = ["SECRET"]

        with patch.object(processor, 'find_unsafe_words', return_value=mock_result):
            result = processor.process(sample_pdf, epsilon=1.0)

            assert "safe_pdf_path" in result
            assert "unsafe_words" in result
            assert "SECRET" in result["unsafe_words"]

            output_path = Path(result["safe_pdf_path"])
            assert output_path.exists()
            assert output_path.stat().st_size > 0
            assert output_path.suffix == ".pdf"

            doc = fitz.open(str(output_path))
            page = doc[0]
            text = page.get_text()

            assert "This is a SECRET document" not in text
            doc.close()

            print(f"\n[DocBlur Int] Successfully processed PDF -> {output_path}")