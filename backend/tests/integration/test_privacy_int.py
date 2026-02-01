import pytest
import numpy as np
from app.core.privacy import PrivacyEngine


class TestPrivacyIntegration:
    """
    Verifies the statistical properties of the Privacy Engine.
    We prove that Lower Epsilon = Higher Variance (More Noise).
    """

    def test_privacy_scaling_mechanics(self):
        """
        Scenario: Compare High Privacy (Low Epsilon) vs Low Privacy (High Epsilon).
        Expectation: Low Epsilon must result in significantly larger changes to the vector.
        """
        # 1. High Privacy (Epsilon = 0.1) -> Expect LOTS of noise
        high_privacy_engine = PrivacyEngine(target_epsilon=0.1)

        # 2. Low Privacy (Epsilon = 10.0) -> Expect little noise
        low_privacy_engine = PrivacyEngine(target_epsilon=10.0)

        # Test Vector
        vector = np.zeros(1000)  # Use large vector for statistical significance

        # Apply noise
        noise_high_priv = high_privacy_engine.add_noise(vector.copy())
        noise_low_priv = low_privacy_engine.add_noise(vector.copy())

        # Calculate Magnitude of noise (Standard Deviation or Mean Absolute Error)
        mae_high = np.mean(np.abs(noise_high_priv))
        mae_low = np.mean(np.abs(noise_low_priv))

        print(f"\n[Privacy Stats] MAE (High Priv): {mae_high:.4f} vs MAE (Low Priv): {mae_low:.4f}")

        # The noise from Epsilon 0.1 should be roughly 100x larger than Epsilon 10.0
        assert mae_high > mae_low, "Lower epsilon did not produce higher noise!"

        # Theoretical check: Scale = 1/epsilon.
        # So Ratio should be roughly (1/0.1) / (1/10) = 10 / 0.1 = 100
        ratio = mae_high / mae_low
        assert ratio > 50.0, f"Noise scaling ratio {ratio} is too low. Math might be off."

    def test_consistency_across_runs(self):
        """
        Scenario: Run noise generation multiple times.
        Expectation: The noise is random every time (stochastic), not deterministic.
        """
        engine = PrivacyEngine(target_epsilon=1.0)
        vector = np.ones(50)

        run1 = engine.add_noise(vector.copy())
        run2 = engine.add_noise(vector.copy())

        # Ensure they are different
        correlation = np.corrcoef(run1, run2)[0, 1]

        # Correlation should be low (random noise shouldn't be perfectly correlated)
        assert correlation < 0.99, "Noise generation appears deterministic!"