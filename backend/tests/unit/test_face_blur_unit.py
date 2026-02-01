import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from app.processors.face_blur import FaceDetection


class TestFaceBlurUnit:

    @patch('app.processors.face_blur.download_model')
    @patch('app.processors.face_blur.YuNet')
    def test_initialization(self, mock_yunet, mock_download):
        """Test that the face detector initializes dependencies correctly."""
        fd = FaceDetection()

        mock_download.assert_called_once()
        mock_yunet.assert_called_once()
        assert fd.detector is not None

    @patch('app.processors.face_blur.cv.imread')
    @patch('app.processors.face_blur.YuNet')
    def test_blur_faces_logic(self, mock_yunet, mock_imread):
        """
        Scenario: YuNet detects 1 face.
        Expectation: GaussianBlur is applied to that region.
        """
        mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_img

        mock_instance = mock_yunet.return_value
        mock_instance.infer.return_value = np.array([[10, 10, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                                                    dtype=np.float32)

        fd = FaceDetection(conf_threshold=0.6)

        with patch('app.processors.face_blur.cv.GaussianBlur') as mock_blur:
            mock_blur.return_value = np.ones((20, 20, 3), dtype=np.uint8) * 255

            result = fd.blur_faces("fake_path.jpg")
            mock_instance.setInputSize.assert_called_with([100, 100])
            mock_instance.infer.assert_called()
            mock_blur.assert_called_once()
            assert result[10, 10, 0] == 255

    @patch('app.processors.face_blur.cv.imread')
    @patch('app.processors.face_blur.YuNet')
    def test_no_faces_found(self, mock_yunet, mock_imread):
        """
        Scenario: YuNet finds 0 faces.
        Expectation: Image returned matches original.
        """
        mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_img

        mock_instance = mock_yunet.return_value
        mock_instance.infer.return_value = np.empty((0, 15))

        fd = FaceDetection()

        with patch('app.processors.face_blur.cv.GaussianBlur') as mock_blur:
            result = fd.blur_faces("fake_path.jpg")

            mock_blur.assert_not_called()
            assert np.array_equal(result, mock_img)