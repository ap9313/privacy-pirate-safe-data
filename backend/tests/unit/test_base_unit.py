import pytest
import numpy as np
from app.processors.base import BaseProcessor


class DummyProcessor(BaseProcessor):
    def process(self, input_data, epsilon):
        return {"status": "ok"}


class TestBaseProcessor:

    @pytest.fixture
    def processor(self):
        return DummyProcessor()

    def test_format_vector_converts_numpy(self, processor):
        """Test that numpy arrays are converted to standard lists (for JSON)."""
        vec = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        formatted = processor.format_vector(vec)

        assert isinstance(formatted, list)
        assert len(formatted) == 3
        assert formatted[0] == pytest.approx(0.1)

    def test_format_vector_handles_none(self, processor):
        """Test null handling."""
        assert processor.format_vector(None) == []

    def test_utility_score_perfect_match(self, processor):
        """
        Scenario: Vectors are identical.
        Expectation: 100% Similarity.
        """
        vec = np.array([1, 0, 0])
        score = processor.calculate_utility_score(vec, vec)
        assert score == 100.0

    def test_utility_score_orthogonal(self, processor):
        """
        Scenario: Vectors are completely different (90 degrees apart).
        Expectation: 0% Similarity.
        """
        vec_a = np.array([1, 0, 0])
        vec_b = np.array([0, 1, 0])
        score = processor.calculate_utility_score(vec_a, vec_b)
        assert score == 0.0

    def test_utility_score_with_noise(self, processor):
        """
        Scenario: Vector B has some noise but points generally in the same direction.
        Expectation: High score, but less than 100%.
        """
        vec_a = np.array([1.0, 0.0])
        vec_b = np.array([0.9, 0.1])
        score = processor.calculate_utility_score(vec_a, vec_b)
        assert 90.0 < score < 100.0

    def test_utility_score_zero_vector_safety(self, processor):
        """
        Scenario: One vector is all zeros (common in error states).
        Expectation: Return 0.0 instead of crashing with DivisionByZero.
        """
        vec_a = np.array([1, 1, 1])
        vec_zero = np.array([0, 0, 0])

        score = processor.calculate_utility_score(vec_a, vec_zero)
        assert score == 0.0

    def test_clamping_negative_similarity(self, processor):
        """
        Scenario: Vectors are opposite (cosine -1).
        Expectation: Clamped to 0.0 (since negative utility doesn't make sense for this UI metric).
        """
        vec_a = np.array([1, 0])
        vec_b = np.array([-1, 0])
        score = processor.calculate_utility_score(vec_a, vec_b)
        assert score == 0.0