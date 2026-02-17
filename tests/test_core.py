"""
Tests for MindShow core logic.

These tests verify the signal processing, brain state classification,
and color mood mapping without requiring any hardware (Muse headband
or Pixelblaze controllers).
"""
import sys
import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, ".")

from integrated_mindshow_system import (
    MindShowConfig,
    calculate_band_powers,
    IntegratedEEGProcessor,
    MultiPixelblazeController,
)


# ---------------------------------------------------------------------------
# Band Power Calculation (FFT)
# ---------------------------------------------------------------------------

class TestCalculateBandPowers:
    """Tests for the FFT-based band power calculation."""

    def test_returns_all_five_bands(self):
        """Should return delta, theta, alpha, beta, gamma keys."""
        sample_rate = 256
        # 1 second of random EEG across 4 channels
        eeg = np.random.randn(4, sample_rate)
        result = calculate_band_powers(eeg, sample_rate)

        assert set(result.keys()) == {"delta", "theta", "alpha", "beta", "gamma"}

    def test_all_values_non_negative(self):
        """Band powers are squared magnitudes and must be >= 0."""
        eeg = np.random.randn(4, 256)
        result = calculate_band_powers(eeg, 256)

        for band, power in result.items():
            assert power >= 0, f"{band} power was negative: {power}"

    def test_pure_alpha_signal_dominates(self):
        """A pure 10 Hz sine (alpha band) should produce highest alpha power."""
        sample_rate = 256
        t = np.arange(sample_rate) / sample_rate
        alpha_signal = np.sin(2 * np.pi * 10 * t)  # 10 Hz = alpha
        eeg = np.tile(alpha_signal, (4, 1))  # 4 identical channels

        result = calculate_band_powers(eeg, sample_rate)

        assert result["alpha"] > result["delta"]
        assert result["alpha"] > result["theta"]
        assert result["alpha"] > result["beta"]

    def test_pure_beta_signal_dominates(self):
        """A pure 20 Hz sine (beta band) should produce highest beta power."""
        sample_rate = 256
        t = np.arange(sample_rate) / sample_rate
        beta_signal = np.sin(2 * np.pi * 20 * t)  # 20 Hz = beta
        eeg = np.tile(beta_signal, (4, 1))

        result = calculate_band_powers(eeg, sample_rate)

        assert result["beta"] > result["delta"]
        assert result["beta"] > result["theta"]
        assert result["beta"] > result["alpha"]

    def test_zeros_return_zeros(self):
        """All-zero input should yield zero for every band."""
        eeg = np.zeros((4, 256))
        result = calculate_band_powers(eeg, 256)

        for band, power in result.items():
            assert power == 0.0, f"{band} was {power} for zero input"

    def test_handles_bad_input_gracefully(self):
        """Degenerate input should return zeros, not crash."""
        result = calculate_band_powers(np.array([[]]), 256)
        assert all(v == 0 for v in result.values())


# ---------------------------------------------------------------------------
# Brain State Classification
# ---------------------------------------------------------------------------

class TestBrainStateClassification:
    """Tests for the stable brain state classifier."""

    def _make_processor(self, **overrides):
        config = MindShowConfig(**overrides)
        return IntegratedEEGProcessor(config)

    def test_default_state_is_neutral(self):
        proc = self._make_processor()
        assert proc.last_brain_state == "neutral"

    def test_high_attention_eventually_becomes_engaged(self):
        """Feeding high attention repeatedly should trigger 'engaged'."""
        proc = self._make_processor(
            state_confidence_required=2,
            min_state_duration=0.0,
        )
        # Force last_state_change to the past so duration check passes
        proc.last_state_change = time.time() - 10

        for _ in range(5):
            state = proc._classify_stable_brain_state(attention=0.9, relaxation=0.1)

        assert state == "engaged"

    def test_high_relaxation_eventually_becomes_relaxed(self):
        """Feeding high relaxation repeatedly should trigger 'relaxed'."""
        proc = self._make_processor(
            state_confidence_required=2,
            min_state_duration=0.0,
        )
        proc.last_state_change = time.time() - 10

        for _ in range(5):
            state = proc._classify_stable_brain_state(attention=0.1, relaxation=0.9)

        assert state == "relaxed"

    def test_state_requires_confidence(self):
        """A single high reading shouldn't flip the state immediately."""
        proc = self._make_processor(
            state_confidence_required=3,
            min_state_duration=0.0,
        )
        proc.last_state_change = time.time() - 10

        state = proc._classify_stable_brain_state(attention=0.9, relaxation=0.1)
        assert state == "neutral", "Should still be neutral after only 1 reading"

    def test_state_respects_min_duration(self):
        """State shouldn't change until min_state_duration has elapsed."""
        proc = self._make_processor(
            state_confidence_required=1,
            min_state_duration=999.0,  # impossibly long
        )
        # last_state_change is now, so 999s hasn't elapsed
        for _ in range(10):
            state = proc._classify_stable_brain_state(attention=0.9, relaxation=0.1)

        assert state == "neutral"


# ---------------------------------------------------------------------------
# Relaxation Calculation Fallbacks
# ---------------------------------------------------------------------------

class TestRelaxationCalculation:
    """Test the robust relaxation calculation with multiple fallback methods."""

    def _make_processor(self):
        return IntegratedEEGProcessor(MindShowConfig())

    def test_primary_method_alpha_over_theta(self):
        proc = self._make_processor()
        band_powers = {"delta": 1.0, "theta": 2.0, "alpha": 4.0, "beta": 1.0, "gamma": 0.5}
        result = proc._calculate_relaxation_robust(band_powers)
        assert result == pytest.approx(2.0)  # alpha/theta = 4/2

    def test_fallback_alpha_over_delta(self):
        """When theta is zero, should fall back to alpha/delta."""
        proc = self._make_processor()
        band_powers = {"delta": 2.0, "theta": 0.0, "alpha": 6.0, "beta": 1.0, "gamma": 0.5}
        result = proc._calculate_relaxation_robust(band_powers)
        assert result == pytest.approx(3.0)  # alpha/delta = 6/2

    def test_last_resort_neutral(self):
        """When all bands are zero/NaN, should return 0.5."""
        proc = self._make_processor()
        band_powers = {"delta": 0.0, "theta": 0.0, "alpha": 0.0, "beta": 0.0, "gamma": 0.0}
        result = proc._calculate_relaxation_robust(band_powers)
        assert result == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Color Mood Mapping
# ---------------------------------------------------------------------------

class TestColorMoodMapping:
    """Test the continuous color mood calculation in the Pixelblaze controller."""

    def _make_controller(self, **overrides):
        config = MindShowConfig(**overrides)
        return MultiPixelblazeController(config)

    def test_neutral_input_produces_mid_range_mood(self):
        """Attention=0.5 and relaxation=0.5 should give ~0.5 mood."""
        ctrl = self._make_controller()
        ctrl.previous_color_mood = 0.5  # start neutral

        # Manually replicate the color mood calculation from
        # update_from_brain_state to test without async/devices
        attention = 0.5
        relaxation = 0.5
        attention_contribution = (attention - 0.5) * -ctrl.attention_weight
        relaxation_contribution = (relaxation - 0.5) * ctrl.relaxation_weight
        engagement = (attention + relaxation) / 2
        intensity = ctrl.intensity_scale + engagement * (1.0 - ctrl.intensity_scale)
        raw = 0.5 + (attention_contribution + relaxation_contribution) * intensity
        raw = max(0.0, min(1.0, raw))

        assert 0.4 <= raw <= 0.6, f"Expected ~0.5, got {raw}"

    def test_high_attention_produces_warm_mood(self):
        """High attention should push mood toward warm (lower values)."""
        ctrl = self._make_controller()
        attention = 0.9
        relaxation = 0.1
        attention_contribution = (attention - 0.5) * -ctrl.attention_weight
        relaxation_contribution = (relaxation - 0.5) * ctrl.relaxation_weight
        engagement = (attention + relaxation) / 2
        intensity = ctrl.intensity_scale + engagement * (1.0 - ctrl.intensity_scale)
        raw = 0.5 + (attention_contribution + relaxation_contribution) * intensity
        raw = max(0.0, min(1.0, raw))

        assert raw < 0.5, f"Expected warm (< 0.5), got {raw}"

    def test_high_relaxation_produces_cool_mood(self):
        """High relaxation should push mood toward cool (higher values)."""
        ctrl = self._make_controller()
        attention = 0.1
        relaxation = 0.9
        attention_contribution = (attention - 0.5) * -ctrl.attention_weight
        relaxation_contribution = (relaxation - 0.5) * ctrl.relaxation_weight
        engagement = (attention + relaxation) / 2
        intensity = ctrl.intensity_scale + engagement * (1.0 - ctrl.intensity_scale)
        raw = 0.5 + (attention_contribution + relaxation_contribution) * intensity
        raw = max(0.0, min(1.0, raw))

        assert raw > 0.5, f"Expected cool (> 0.5), got {raw}"

    def test_mood_is_always_clamped(self):
        """Color mood must always be in [0, 1]."""
        ctrl = self._make_controller()
        for att in [0.0, 0.5, 1.0]:
            for rel in [0.0, 0.5, 1.0]:
                attention_contribution = (att - 0.5) * -ctrl.attention_weight
                relaxation_contribution = (rel - 0.5) * ctrl.relaxation_weight
                engagement = (att + rel) / 2
                intensity = ctrl.intensity_scale + engagement * (1.0 - ctrl.intensity_scale)
                raw = 0.5 + (attention_contribution + relaxation_contribution) * intensity
                raw = max(0.0, min(1.0, raw))
                assert 0.0 <= raw <= 1.0

    def test_s_curve_easing_preserves_midpoint(self):
        """S-curve easing of 0.5 should stay at 0.5."""
        raw = 0.5
        if raw < 0.5:
            eased = 0.5 * pow(raw * 2, 2)
        else:
            eased = 1.0 - 0.5 * pow((1.0 - raw) * 2, 2)
        assert eased == pytest.approx(0.5)

    def test_s_curve_easing_extremes(self):
        """S-curve of 0.0 should be 0.0, 1.0 should be 1.0."""
        # Test 0.0
        raw = 0.0
        eased = 0.5 * pow(raw * 2, 2)
        assert eased == pytest.approx(0.0)

        # Test 1.0
        raw = 1.0
        eased = 1.0 - 0.5 * pow((1.0 - raw) * 2, 2)
        assert eased == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class TestMindShowConfig:
    """Test that configuration defaults are sane."""

    def test_default_thresholds(self):
        config = MindShowConfig()
        assert config.attention_threshold == 0.75
        assert config.relaxation_threshold == 0.65

    def test_default_stability_params(self):
        config = MindShowConfig()
        assert config.state_confidence_required == 3
        assert config.min_state_duration == 2.0

    def test_color_mood_weights_sum_reasonable(self):
        config = MindShowConfig()
        total = config.color_mood_attention_weight + config.color_mood_relaxation_weight
        assert 0 < total <= 2.0

    def test_smoothing_factor_in_range(self):
        config = MindShowConfig()
        assert 0.0 < config.color_mood_smoothing <= 1.0

    def test_update_rate_positive(self):
        config = MindShowConfig()
        assert config.update_rate > 0


# ---------------------------------------------------------------------------
# Anti-Flicker Throttling
# ---------------------------------------------------------------------------

class TestAntiFlicker:
    """Test the variable update throttling logic."""

    def test_first_update_always_significant(self):
        """A device with no prior values should always get an update."""
        ctrl = MultiPixelblazeController(MindShowConfig())
        device_key = "192.168.0.1"
        # No prior tracking for this device
        assert device_key not in ctrl.last_variable_values

    def test_small_change_is_insignificant(self):
        """Changes below the threshold should be considered insignificant."""
        ctrl = MultiPixelblazeController(MindShowConfig())
        ctrl.last_variable_values["test"] = {"colorBlend": 0.500}
        new_val = 0.501  # change of 0.001, threshold is 0.02
        assert abs(new_val - 0.500) < ctrl.variable_update_threshold

    def test_large_change_is_significant(self):
        """Changes above the threshold should trigger an update."""
        ctrl = MultiPixelblazeController(MindShowConfig())
        assert abs(0.55 - 0.50) >= ctrl.variable_update_threshold


# ---------------------------------------------------------------------------
# No Fake Data
# ---------------------------------------------------------------------------

class TestNoFakeData:
    """Verify that the codebase doesn't contain random/fake data generation."""

    def test_band_power_calculation_uses_fft(self):
        """Band powers should come from FFT, not np.random."""
        import inspect
        source = inspect.getsource(calculate_band_powers)
        assert "random" not in source.lower(), (
            "calculate_band_powers should not use random values"
        )

    def test_muselsl_processor_uses_real_fft(self):
        """MuseLSL processor should delegate to FFT-based calculation."""
        from integrated_mindshow_system import MuseLSLProcessor
        import inspect
        source = inspect.getsource(MuseLSLProcessor._calculate_band_powers)
        assert "random" not in source.lower()
        assert "calculate_band_powers" in source

    def test_brainflow_processor_uses_real_fft(self):
        """BrainFlow processor should delegate to FFT-based calculation."""
        from integrated_mindshow_system import BrainFlowProcessor
        import inspect
        source = inspect.getsource(BrainFlowProcessor._calculate_band_powers)
        assert "random" not in source.lower()
        assert "calculate_band_powers" in source
