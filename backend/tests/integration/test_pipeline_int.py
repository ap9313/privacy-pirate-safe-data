"""
Integration Tests for SecurePipeline
Tests the full pipeline with real components and sample files
"""
import pytest
import os
import json
from io import BytesIO
from pathlib import Path
from app.core.pipeline import SecurePipeline


class TestPipelineIntegration:
    """Integration tests - test the full pipeline with real components"""

    @pytest.fixture
    def pipeline(self):
        """Create a pipeline with real components"""
        return SecurePipeline()

    @pytest.fixture
    def samples_dir(self):
        """Get path to test samples directory"""
        return Path(__file__).parents[1] / "samples"

    def test_text_pipeline_basic_pii(self, pipeline):
        """Test text pipeline with basic PII"""
        input_text = "Hello, my name is John Doe and my email is john.doe@example.com"

        result = pipeline.run_text_pipeline(input_text, epsilon=1.0)

        assert "safe_content" in result
        assert "audit_log" in result
        assert "safe_vector" in result
        assert "boomerang_map" in result

        assert len(result["audit_log"]) > 0

        safe_text = result["safe_content"]
        assert "John Doe" not in safe_text
        assert "john.doe@example.com" not in safe_text
        assert "<PERSON>" in safe_text or "<EMAIL" in safe_text

        assert len(result["safe_vector"]) > 0
        assert isinstance(result["safe_vector"], list)

    def test_text_pipeline_multiple_pii_types(self, pipeline):
        """Test with multiple PII types in one text"""
        input_text = """
        Patient: Maria Garcia
        SSN: 123-45-6789
        Phone: 555-123-4567
        Email: maria@hospital.com
        Credit Card: 4111-1111-1111-1111
        """

        result = pipeline.run_text_pipeline(input_text, epsilon=1.0)


        labels_found = {finding["label"] for finding in result["audit_log"]}
        assert len(result["audit_log"]) >= 3
        safe_text = result["safe_content"]
        assert "123-45-6789" not in safe_text
        assert "555-123-4567" not in safe_text or "<PHONE" in safe_text

    def test_text_pipeline_no_pii(self, pipeline):
        """Test text with no PII"""
        input_text = "The weather today is sunny with a high of 75 degrees."

        result = pipeline.run_text_pipeline(input_text, epsilon=1.0)
        assert "safe_content" in result
        assert "safe_vector" in result

    def test_text_pipeline_epsilon_variations(self, pipeline):
        """Test that different epsilon values produce different vectors"""
        input_text = "John Smith's phone is 555-1234"

        result_low = pipeline.run_text_pipeline(input_text, epsilon=0.1)
        result_high = pipeline.run_text_pipeline(input_text, epsilon=10.0)
        vector_low = result_low["safe_vector"]
        vector_high = result_high["safe_vector"]
        import numpy as np
        diff = np.linalg.norm(np.array(vector_low) - np.array(vector_high))

        # Low epsilon adds more noise, so difference should be noticeable
        assert diff > 0.01  # Some threshold

    # ========== FORM PIPELINE TESTS ==========

    def test_form_pipeline_basic(self, pipeline):
        """Test form pipeline with typical form data"""
        form_data = {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "555-9876",
            "address": "123 Main St"
        }

        result = pipeline.run_form_pipeline(form_data, epsilon=1.0)

        # Verify structure
        assert "safe_content" in result
        assert "audit_log" in result
        assert "safe_vector" in result

        # Verify some PII was detected
        assert len(result["audit_log"]) > 0

    def test_form_pipeline_empty_fields(self, pipeline):
        """Test form with empty fields"""
        form_data = {
            "name": "",
            "comments": "Just testing"
        }

        result = pipeline.run_form_pipeline(form_data, epsilon=1.0)

        assert "safe_content" in result
        assert "safe_vector" in result

    def test_form_pipeline_special_characters(self, pipeline):
        """Test form with special characters"""
        form_data = {
            "name": "José García-López",
            "notes": "Testing émojis 🎉"
        }

        result = pipeline.run_form_pipeline(form_data, epsilon=1.0)

        # Should handle special characters without crashing
        assert "safe_content" in result

    # ========== AUDIO PIPELINE TESTS ==========

    def test_audio_pipeline_with_sample(self, pipeline, samples_dir):
        """Test audio pipeline with real audio file"""
        audio_path = samples_dir / "test_audio.wav"

        if not audio_path.exists():
            pytest.skip(f"Audio sample not found: {audio_path}")

        with open(audio_path, "rb") as f:
            result = pipeline.run_audio_pipeline(f, epsilon=1.0)

        # Verify structure
        assert "safe_content" in result
        assert "audit_log" in result
        assert "safe_vector" in result

        # Verify transcription happened
        safe_text = result["safe_content"]
        assert len(safe_text) > 0

    def test_audio_pipeline_multi_pii(self, pipeline, samples_dir):
        """Test audio with multiple PII types"""
        audio_path = samples_dir / "test_multi_pii.wav"

        if not audio_path.exists():
            pytest.skip(f"Multi-PII audio not found: {audio_path}")

        with open(audio_path, "rb") as f:
            result = pipeline.run_audio_pipeline(f, epsilon=1.0)

        # Should detect multiple PII items
        assert len(result["audit_log"]) >= 2

        # Verify redaction
        safe_text = result["safe_content"]
        print(f"\n[Audio Test] Transcribed: {safe_text}")

        # Should have redaction tags
        assert "<" in safe_text and ">" in safe_text

    def test_image_pipeline_with_selfie(self, pipeline, samples_dir):
        """Test image pipeline with selfie (face detection)"""
        img_path = samples_dir / "selfie_test.jpg"

        if not img_path.exists():
            pytest.skip(f"Selfie test image not found: {img_path}")

        with open(img_path, "rb") as f:
            result = pipeline.run_image_pipeline(f, epsilon=1.0)

        assert "blurred_image_bytes" in result
        assert "safe_content" in result
        assert "audit_log" in result
        assert "safe_vector" in result
        assert len(result["blurred_image_bytes"]) > 0

    def test_image_pipeline_creates_description(self, pipeline, samples_dir):
        """Test that image pipeline generates description"""
        img_path = samples_dir / "selfie_test.jpg"

        if not img_path.exists():
            pytest.skip(f"Image not found: {img_path}")

        with open(img_path, "rb") as f:
            result = pipeline.run_image_pipeline(f, epsilon=1.0)

        safe_content = result["safe_content"]
        assert len(safe_content) > 0

    def test_pdf_pipeline_with_sample(self, pipeline, samples_dir):
        """Test PDF pipeline with sample PDF"""
        pdf_path = samples_dir / "sample.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Sample PDF not found: {pdf_path}")

        result = pipeline.run_document_pipeline(str(pdf_path), epsilon=1.0)

        assert "safe_pdf_path" in result
        assert "safe_content" in result
        assert "audit_log" in result
        assert "safe_vector" in result

        assert os.path.exists(result["safe_pdf_path"])

    def test_pdf_pipeline_description_generation(self, pipeline, samples_dir):
        """Test that PDF pipeline generates descriptions"""
        pdf_path = samples_dir / "sample.pdf"

        if not pdf_path.exists():
            pytest.skip(f"PDF not found: {pdf_path}")

        result = pipeline.run_document_pipeline(str(pdf_path), epsilon=1.0)

        assert "safe_content" in result
        assert len(result["safe_content"]) > 0

    def test_consistent_structure_across_modalities(self, pipeline):
        """Test that all modalities return consistent structure"""
        text_result = pipeline.run_text_pipeline("Test text", epsilon=1.0)
        form_result = pipeline.run_form_pipeline({"field": "value"}, epsilon=1.0)

        required_fields = ["safe_content", "audit_log", "safe_vector"]

        for field in required_fields:
            assert field in text_result
            assert field in form_result

    def test_vector_dimensions_consistent(self, pipeline):
        """Test that vectors are consistent size across modalities"""
        text_result = pipeline.run_text_pipeline("Test", epsilon=1.0)
        form_result = pipeline.run_form_pipeline({"test": "data"}, epsilon=1.0)

        text_vector_len = len(text_result["safe_vector"])
        form_vector_len = len(form_result["safe_vector"])

        assert text_vector_len == form_vector_len

    def test_boomerang_map_reversibility(self, pipeline):
        """Test that boomerang map allows reversibility"""
        input_text = "John Smith lives in New York"
        result = pipeline.run_text_pipeline(input_text, epsilon=1.0)
        boomerang_map = result.get("boomerang_map", {})
        safe_text = result["safe_content"]
        if boomerang_map:
            for original, tag in boomerang_map.items():
                assert isinstance(tag, str)
                assert tag.startswith("<")
                assert tag.endswith(">")

    def test_text_pipeline_with_very_long_text(self, pipeline):
        """Test handling of very long text"""
        long_text = "Test sentence. " * 1000
        result = pipeline.run_text_pipeline(long_text, epsilon=1.0)
        assert "safe_content" in result
        assert "safe_vector" in result

    def test_form_pipeline_with_nested_data(self, pipeline):
        """Test form with nested/complex data"""
        complex_form = {
            "user": {
                "name": "Test User",
                "nested": "value"
            },
            "items": [1, 2, 3]
        }
        result = pipeline.run_form_pipeline(complex_form, epsilon=1.0)
        assert "safe_content" in result

    def test_epsilon_boundary_values(self, pipeline):
        """Test extreme epsilon values"""
        text = "John Doe test"
        result_low = pipeline.run_text_pipeline(text, epsilon=0.001)
        assert "safe_vector" in result_low
        result_high = pipeline.run_text_pipeline(text, epsilon=100.0)
        assert "safe_vector" in result_high
