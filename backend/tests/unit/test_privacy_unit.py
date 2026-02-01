import pytest
import numpy as np
from app.core.privacy import PrivacyEngine
from app.config import DEFAULT_EPSILON, MIN_EPSILON


class TestPrivacyUnit:

    def test_initialization(self):
        """Test that defaults are loaded from config."""
        engine = PrivacyEngine()
        assert engine.epsilon == DEFAULT_EPSILON

        custom_engine = PrivacyEngine(target_epsilon=5.0)
        assert custom_engine.epsilon == 5.0

    def test_add_noise_shape_and_type(self, mocker):
        """Test that output shape matches input shape exactly."""
        engine = PrivacyEngine()
        vector = np.zeros(768, dtype=np.float32)
        noisy_vector = engine.add_noise(vector)
        assert isinstance(noisy_vector, np.ndarray)
        assert noisy_vector.shape == (768,)
        assert noisy_vector.dtype == np.float32 or noisy_vector.dtype == np.float64

    def test_noise_is_actually_added(self):
        """Test that the vector is modified (not identical to input)."""
        engine = PrivacyEngine()
        vector = np.zeros(10)
        noisy = engine.add_noise(vector)
        assert not np.array_equal(vector, noisy)
        assert np.any(noisy != 0)

    def test_min_epsilon_safety(self):
        """Test that epsilon=0 doesn't crash the system."""
        engine = PrivacyEngine(target_epsilon=0.0)
        vector = np.array([1.0, 2.0, 3.0])
        noisy = engine.add_noise(vector)
        assert len(noisy) == 3
        assert np.abs(noisy).max() > 0

    def test_budget_status(self):
        """Test the mocked budget status."""
        engine = PrivacyEngine(target_epsilon=0.1)
        status = engine.get_budget_status()
        assert status["status"] == "Depleted"
        engine = PrivacyEngine(target_epsilon=10.0)
        status = engine.get_budget_status()
        assert status["status"] == "Healthy"