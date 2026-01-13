"""
Simulator module: implements the repetitive-sampling S^2 control chart analytics
and simulation utilities.

Functions:
- control_limits(sigma2, n, k1, k2)
- single_sample_probs(sigma2, n, k1, k2, c=1.0)
- overall_oc(sigma2, n, k1, k2, c=1.0)
- simulate_run(S2_sequence, n, k1, k2)  # deterministic replay on a sequence
- empirical_ARL_from_runs(runs, n, k1, k2) # compute empirical ARL across many runs
"""

import numpy as np
from scipy.stats import chi2
from typing import Sequence, Tuple, Dict


def control_limits(sigma2: float, n: int, k1: float, k2: float) -> Dict[str, float]:
    """
    Compute outer and inner control limits for S^2 chart.
    Returns dict with UCL1,LCL1,UCL2,LCL2.
    LCL values may be negative mathematically; caller may floor them at 0.
    """
    assert n > 1, "subgroup size n must be > 1"
    assert k1 > k2, f"outer limit k1 ({k1}) must be greater than inner limit k2 ({k2})"
    
    sd_factor = np.sqrt(2.0 * (sigma2**2) / (n - 1))
    UCL1 = sigma2 + k1 * sd_factor
    LCL1 = max(0.0, sigma2 - k1 * sd_factor)
    UCL2 = sigma2 + k2 * sd_factor
    LCL2 = max(0.0, sigma2 - k2 * sd_factor)
    
    return {"UCL1": UCL1, "LCL1": LCL1, "UCL2": UCL2, "LCL2": LCL2}


def single_sample_probs(sigma2: float, n: int, k1: float, k2: float, c: float = 1.0) -> Dict[str, float]:
    """
    Compute single-sample probabilities using chi-square CDF when true variance is c*sigma2.
    Returns {P1_out, P1_in, P_rep}.
    """
    df = n - 1
    limits = control_limits(sigma2, n, k1, k2)
    def G_of_T(T: float) -> float:
        arg = (df * T) / (c * sigma2)
        return chi2.cdf(arg, df) if arg >= 0 else 0.0

    U1 = limits["UCL1"]
    L1 = limits["LCL1"]
    U2 = limits["UCL2"]
    L2 = limits["LCL2"]

    P_ge_U1 = 1.0 - G_of_T(U1)  # upper tail beyond UCL1
    P_le_L1 = G_of_T(L1)        # lower tail below LCL1
    P1_out = P_ge_U1 + P_le_L1

    P1_in = G_of_T(U2) - G_of_T(L2)

    P_left_rep = G_of_T(L2) - G_of_T(L1)
    P_right_rep = G_of_T(U1) - G_of_T(U2)
    P_rep = P_left_rep + P_right_rep

    # Numeric clipping
    P1_out = float(np.clip(P1_out, 0.0, 1.0))
    P1_in = float(np.clip(P1_in, 0.0, 1.0))
    P_rep = float(np.clip(P_rep, 0.0, 1.0))
    return {"P1_out": P1_out, "P1_in": P1_in, "P_rep": P_rep}


def overall_oc(sigma2: float, n: int, k1: float, k2: float, c: float = 1.0) -> Dict[str, float]:
    """
    Compute overall operating characteristics:
        P_out = P1_out / (1 - P_rep),
        ASN = n / (1 - P_rep),
        ARL = 1 / P_out
    for process variance scaled by c.
    """
    probs = single_sample_probs(sigma2, n, k1, k2, c=c)
    P1_out = probs["P1_out"]
    P_rep = probs["P_rep"]
    denom = 1.0 - P_rep
    if denom <= 0:
        return {"P_out": np.inf, "ASN": np.inf, "ARL": np.inf, **probs}
    P_out = P1_out / denom
    ASN = n / denom
    ARL = 1.0 / P_out if P_out > 0 else np.inf
    return {"P_out": P_out, "ASN": ASN, "ARL": ARL, **probs}


def simulate_run(S2_sequence: Sequence[float], n: int, k1: float, k2: float) -> Tuple[int, str]:
    """
    Simulate the repetitive-sampling decision process on a provided sequence of S2 values.
    Returns (samples_consumed, outcome) where outcome is 'out', 'in', or 'no_signal' if
    sequence exhausted without a terminal decision.
    Notes:
        - LCL floored at 0 for decision logic (variance cannot be negative).
        - Caller should provide sequences long enough to capture repeats.
    """
    if len(S2_sequence) == 0:
        return 0, "no_signal"
    limits = control_limits(sigma2=1.0, n=n, k1=k1, k2=k2)  # S2 assumed scaled to nominal sigma2=1 in data sequences
    U1, L1, U2, L2 = limits["UCL1"], limits["LCL1"], limits["UCL2"], limits["LCL2"]
    
    # LCLs already floored by control_limits

    for i, s2 in enumerate(S2_sequence, start=1):
        if s2 >= U1 or s2 <= L1:
            return i, "out"
        if (L2 <= s2 <= U2):
            return i, "in"
        # else: repeat -> continue to next s2 value
    # if sequence ends with no terminal decision:
    return len(S2_sequence), "no_signal"


def empirical_ARL_from_runs(runs: Sequence[Sequence[float]], n: int, k1: float, k2: float, max_samples: int = 1000) -> Dict[str, float]:
    """
    Given many runs (each run is a sequence of S2 values), compute empirical ARL (mean samples to signal)
    separately for in-control runs and shifted runs if runs are labeled; for simplicity this function returns
    overall mean samples-to-out and counts.
    Returns dict with {mean_samples_to_signal, prop_out, mean_samples_by_outcome}
    """
    samples = []
    outcomes = []
    for seq in runs:
        samples_used, outcome = simulate_run(seq[:max_samples], n, k1, k2)
        samples.append(samples_used)
        outcomes.append(outcome)
    samples = np.array(samples)
    # mean excluding no_signal entries for ARL estimation (or treat as censored)
    signaled_mask = np.array([o != "no_signal" for o in outcomes])
    mean_samples = float(np.mean(samples[signaled_mask])) if signaled_mask.any() else np.inf
    prop_out = float(np.sum([o == "out" for o in outcomes]) / len(outcomes))
    return {"mean_samples": mean_samples, "prop_out": prop_out, "samples": samples, "outcomes": outcomes}
