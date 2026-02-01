"""
Unit Tests for SecurePipeline
Tests individual methods in isolation with mocking
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from app.core.pipeline import SecurePipeline


class TestSecurePipelineUnit:
    """Unit tests for SecurePipeline - test each method in isolation"""

    @pytest.fixture
    def pipeline(self):
        """Create a fresh pipeline instance for each test"""
        return SecurePipeline()

    @pytest.fixture
    def mock_scanner(self):
        """Mock scanner that returns predictable results"""
        scanner = Mock()
        scanner.scan.return_value = [
            {"text": "John Doe", "label": "person", "score": 0.95, "start": 0, "end": 8}
        ]
        scanner.redact.return_value = "<PERSON> works here"
        scanner.create_boomerang_map.return_value = {"John Doe": "<PERSON_1>"}
        return scanner

    @pytest.fixture
    def mock_embedder(self):
        """Mock embedder that returns a predictable vector"""
        embedder = Mock()
        embedder.get_vector.return_value = np.random.rand(768).astype(np.float32)
        return embedder

    @pytest.fixture
    def mock_privacy_engine(self):
        """Mock privacy engine"""
        engine = Mock()
        engine.add_noise.return_value = np.random.rand(768).astype(np.float32)
        return engine

    def test_apply_standard_security_structure(self, pipeline, mock_scanner, mock_embedder, mock_privacy_engine):
        """Test that _apply_standard_security returns correct structure"""
        pipeline.scanner = mock_scanner
        pipeline.embedder = mock_embedder
        pipeline.privacy_engine = mock_privacy_engine

        result = pipeline._apply_standard_security("John Doe works here", epsilon=1.0)

        # Verify structure
        assert "safe_content" in result
        assert "boomerang_map" in result
        assert "audit_log" in result
        assert "safe_vector" in result
        assert "full_vector_shape" in result

        # Verify types
        assert isinstance(result["safe_content"], str)
        assert isinstance(result["boomerang_map"], dict)
        assert isinstance(result["audit_log"], list)
        assert isinstance(result["safe_vector"], list)
        assert isinstance(result["full_vector_shape"], tuple)

    def test_apply_standard_security_calls_pipeline(self, pipeline, mock_scanner, mock_embedder, mock_privacy_engine):
        """Test that all pipeline components are called in correct order"""
        pipeline.scanner = mock_scanner
        pipeline.embedder = mock_embedder
        pipeline.privacy_engine = mock_privacy_engine

        test_text = "Test text with PII"
        epsilon = 1.5

        result = pipeline._apply_standard_security(test_text, epsilon)

        # Verify call order and arguments
        mock_scanner.scan.assert_called_once_with(test_text)
        mock_scanner.redact.assert_called_once()
        mock_scanner.create_boomerang_map.assert_called_once()
        mock_embedder.get_vector.assert_called_once()
        mock_privacy_engine.add_noise.assert_called_once()

        # Verify epsilon was set
        assert pipeline.privacy_engine.epsilon == epsilon

    def test_run_text_pipeline(self, pipeline, mock_scanner, mock_embedder, mock_privacy_engine):
        """Test text pipeline end-to-end"""
        pipeline.scanner = mock_scanner
        pipeline.embedder = mock_embedder
        pipeline.privacy_engine = mock_privacy_engine

        result = pipeline.run_text_pipeline("John Doe's email is john@example.com", epsilon=1.0)

        assert "safe_content" in result
        assert "audit_log" in result
        assert "safe_vector" in result
        mock_scanner.scan.assert_called_once()

    def test_run_form_pipeline_flattens_json(self, pipeline, mock_scanner, mock_embedder, mock_privacy_engine):
        """Test that form pipeline correctly flattens JSON"""
        pipeline.scanner = mock_scanner
        pipeline.embedder = mock_embedder
        pipeline.privacy_engine = mock_privacy_engine

        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234"
        }

        with patch.object(pipeline, '_apply_standard_security') as mock_security:
            mock_security.return_value = {"safe_content": "test"}

            pipeline.run_form_pipeline(form_data, epsilon=1.0)

            # Check that it was called with flattened text
            call_args = mock_security.call_args[0]
            flattened_text = call_args[0]

            assert "name: John Doe" in flattened_text
            assert "email: john@example.com" in flattened_text
            assert "phone: 555-1234" in flattened_text

    def test_epsilon_values(self, pipeline, mock_scanner, mock_embedder, mock_privacy_engine):
        """Test that different epsilon values are handled correctly"""
        pipeline.scanner = mock_scanner
        pipeline.embedder = mock_embedder
        pipeline.privacy_engine = mock_privacy_engine

        epsilon_values = [0.1, 1.0, 5.0, 10.0]

        for eps in epsilon_values:
            result = pipeline._apply_standard_security("Test text", epsilon=eps)
            assert pipeline.privacy_engine.epsilon == eps

    def test_empty_text_handling(self, pipeline, mock_scanner, mock_embedder, mock_privacy_engine):
        """Test handling of empty text input"""
        pipeline.scanner = mock_scanner
        pipeline.embedder = mock_embedder
        pipeline.privacy_engine = mock_privacy_engine

        mock_scanner.scan.return_value = []
        mock_scanner.redact.return_value = ""

        result = pipeline._apply_standard_security("", epsilon=1.0)

        assert result["safe_content"] == ""
        assert result["audit_log"] == []

    def test_vector_conversion_to_list(self, pipeline, mock_scanner, mock_embedder, mock_privacy_engine):
        """Test that numpy arrays are converted to lists for JSON serialization"""
        pipeline.scanner = mock_scanner
        pipeline.embedder = mock_embedder
        pipeline.privacy_engine = mock_privacy_engine

        result = pipeline._apply_standard_security("Test", epsilon=1.0)

        # Verify vector is a list (JSON serializable)
        assert isinstance(result["safe_vector"], list)
        assert all(isinstance(x, (int, float)) for x in result["safe_vector"])

    @patch('tempfile.NamedTemporaryFile')
    @patch('os.remove')
    def test_audio_pipeline_temp_file_cleanup(self, mock_remove, mock_temp, pipeline):
        """Test that audio pipeline cleans up temporary files"""
        # Setup mock file
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_audio.wav"
        mock_temp.return_value.__enter__.return_value = mock_file

        # Mock audio processor
        mock_audio_proc = Mock()
        mock_audio_proc.extract_text.return_value = "Test transcription"
        pipeline.audio_proc = mock_audio_proc

        # Mock the security wrapper
        with patch.object(pipeline, '_apply_standard_security') as mock_security:
            mock_security.return_value = {"safe_content": "test"}

            # Create a mock file object
            mock_file_obj = Mock()
            mock_file_obj.read.return_value = b"fake audio data"

            pipeline.run_audio_pipeline(mock_file_obj, epsilon=1.0)

            # Verify temp file was removed
            mock_remove.assert_called_once_with(mock_file.name)

    def test_boomerang_map_excludes_secrets(self, pipeline):
        """Test that security secrets are excluded from boomerang map"""
        # This tests the integration with scanner's boomerang map creation
        findings = [
            {"text": "John Doe", "label": "person", "score": 0.95},
            {"text": "sk-abc123", "label": "security_secret", "score": 1.0}
        ]

        boomerang = pipeline.scanner.create_boomerang_map(findings)

        # Secrets should NOT be in the map
        assert "sk-abc123" not in boomerang
        # But regular PII should be
        assert "John Doe" in boomerang

