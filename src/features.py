"""
Feature engineering for PMSM stator winding temperature estimation.
UCS321 MST Mini Project - Problem Statement 6 (GE Power Systems)
"""
import numpy as np
import pandas as pd

# Sensor inputs available on a real drive (cheap to measure).
# Deliberately EXCLUDES pm / stator_tooth / stator_yoke: those are the
# expensive thermocouple measurements we are trying to replace.
BASE_INPUTS = ["ambient", "coolant", "u_d", "u_q", "motor_speed", "i_d", "i_q", "torque"]
TARGET = "stator_winding"

# Thermal time constants to capture, in SECONDS.
# Sampling is 2 Hz, so span_samples = seconds * 2.
# Short spans catch winding self-heating; long spans catch housing/coolant soak.
EWM_SPANS_S = [30, 120, 600, 1800, 3600]
FS = 2.0  # Hz


def add_physical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive quantities a machines engineer would actually use."""
    out = df.copy()
    # Current and voltage magnitudes in the dq frame (Park transform invariants)
    out["i_s"] = np.sqrt(out["i_d"] ** 2 + out["i_q"] ** 2)
    out["u_s"] = np.sqrt(out["u_d"] ** 2 + out["u_q"] ** 2)
    # Apparent electrical power ~ heat injected into the windings
    out["S_el"] = 1.5 * out["i_s"] * out["u_s"]
    # Ohmic loss proxy: copper loss scales with i^2 (this is the dominant
    # winding heat source, so it should matter far more than raw current)
    out["i_s_sq"] = out["i_s"] ** 2
    # Mechanical power out
    out["P_mech"] = out["torque"] * out["motor_speed"] * 2 * np.pi / 60.0
    # Loss proxy = electrical in minus mechanical out
    out["P_loss"] = out["S_el"] - out["P_mech"].abs()
    return out


EWM_COLS = ["i_s", "u_s", "S_el", "i_s_sq", "P_loss", "motor_speed", "torque", "coolant", "ambient"]


def add_ewm_features(df: pd.DataFrame, spans_s=EWM_SPANS_S) -> pd.DataFrame:
    """
    Exponentially weighted moving averages + standard deviations, computed
    PER PROFILE so no thermal history leaks across measurement sessions.

    This is the core modelling insight: a motor's winding temperature is an
    integral of past losses, not a function of instantaneous current. An EWMA
    with span tau is a first-order low-pass filter - which is exactly the form
    of a lumped-parameter thermal model.
    """
    out = df.copy()
    g = out.groupby("profile_id", sort=False)
    new = {}
    for s in spans_s:
        span = int(s * FS)
        for c in EWM_COLS:
            new[f"{c}_ewma_{s}s"] = g[c].transform(
                lambda x, sp=span: x.ewm(span=sp, adjust=False).mean()
            ).astype("float32")
            new[f"{c}_ewms_{s}s"] = g[c].transform(
                lambda x, sp=span: x.ewm(span=sp, adjust=False).std()
            ).astype("float32")
    out = pd.concat([out, pd.DataFrame(new, index=out.index)], axis=1)
    # ewm std is NaN on the first sample of each profile
    out = out.fillna(0.0)
    return out


def build(df: pd.DataFrame) -> pd.DataFrame:
    return add_ewm_features(add_physical_features(df))


def feature_columns(df: pd.DataFrame):
    drop = {TARGET, "profile_id", "pm", "stator_tooth", "stator_yoke"}
    return [c for c in df.columns if c not in drop]
