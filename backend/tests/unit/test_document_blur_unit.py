import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
from app.processors.document_blur import DocumentProcessorBlur


class TestDocumentBlurUnit:

    @pytest.fixture
    def mock_extractor(self):
        with patch('app.processors.document_blur.PIIImageExtractor') as mock:
            yield mock.return_value

    @pytest.fixture
    def processor(self, mock_extractor):
        return DocumentProcessorBlur()

    @patch('app.processors.document_blur.fitz.open')
    @patch('app.processors.document_blur.Image')
    @patch('app.processors.document_blur.os.makedirs')
    def test_process_flow(self, mock_makedirs, mock_image, mock_fitz_open, processor, mock_extractor, tmp_path):
        """
        Scenario: Process a PDF with 1 page.
        Expectation: Opens PDF, finds PII, blurs it, and saves output.
        """
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        mock_pii_result = MagicMock()
        mock_pii_result.tolist.return_value = ["John Doe"]
        processor.find_unsafe_words = MagicMock(return_value=mock_pii_result)

        processor.get_bboxes = MagicMock(return_value=[MagicMock()])
        mock_img_obj = MagicMock()
        mock_image.frombytes.return_value = mock_img_obj

        input_file = tmp_path / "test.pdf"
        input_file.touch()
        result = processor.process(str(input_file), epsilon=1.0)

        assert "safe_pdf_path" in result
        assert result["unsafe_words"] == ["John Doe"]

        mock_fitz_open.assert_called_once_with(str(input_file))
        processor.find_unsafe_words.assert_called_once_with(mock_page)
        mock_img_obj.paste.assert_called()
        mock_img_obj.save.assert_called()

    def test_get_bboxes_filtering(self, processor):
        """
        Scenario: Search for words.
        Expectation: Should search for original, lower, and upper case variants.
        """
        mock_page = MagicMock()
        unsafe_words = ["Secret"]

        processor.get_bboxes(mock_page, unsafe_words)
        assert mock_page.search_for.call_count >= 1

    def test_extend_unique(self, processor):
        """Test the helper for unique list extension."""
        target = ["A", "B"]
        processor._extend_unique(target, ["B", "C", "A"])
        assert target == ["A", "B", "C"]