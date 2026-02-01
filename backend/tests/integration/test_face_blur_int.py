import pytest
import os
import cv2 as cv
import numpy as np
from pathlib import Path
from app.processors.face_blur import FaceDetection


class TestFaceBlurIntegration:
    """
    REQUIRES:
    1. 'tests/samples/selfie_test.jpg' (Real image with a face)
    2. YuNet model downloaded in 'data/models/face_detection_yunet/'
    """

    @pytest.fixture
    def processor(self):
        return FaceDetection(conf_threshold=0.6)

    @pytest.fixture
    def sample_image(self):
        # We assume the selfie sample exists from previous steps
        base_dir = Path(__file__).parents[1]
        path = base_dir / "samples" / "selfie_test.jpg"
        if not path.exists():
            pytest.skip(f"Test image not found at {path}")
        return str(path)

    def test_yunet_model_loading(self, processor):
        """
        Scenario: Initialize the processor.
        Expectation: YuNet loads without throwing CV errors.
        """
        assert processor.detector is not None
        assert processor.detector._model is not None

    def test_face_detection_and_blurring(self, processor, sample_image):
        """
        Scenario: specific processing of an image with known faces.
        Expectation: Output image has blurred regions where the faces were.
        """
        print(f"\n[FaceBlur Int] Processing {sample_image}...")
        original = cv.imread(sample_image)
        assert original is not None, "Failed to load original image via OpenCV"

        blurred = processor.blur_faces(sample_image)
        assert blurred is not None
        assert blurred.shape == original.shape

        diff = cv.absdiff(original, blurred)
        non_zero_count = np.count_nonzero(diff)

        print(f"[FaceBlur Int] Pixel differences found: {non_zero_count}")
        assert non_zero_count > 1000, "Image was not modified! Face detection might have failed."

    def test_no_face_image(self, processor, tmp_path):
        """
        Scenario: Image with no faces (e.g., a blank white square).
        Expectation: Returns image identical to original (no blurring applied).
        """
        blank_path = tmp_path / "blank.jpg"
        blank_img = np.ones((300, 300, 3), dtype=np.uint8) * 255
        cv.imwrite(str(blank_path), blank_img)

        result = processor.blur_faces(str(blank_path))

        diff = cv.absdiff(blank_img, result)
        assert np.count_nonzero(diff) == 0, "Blurring applied to an image with no faces!"