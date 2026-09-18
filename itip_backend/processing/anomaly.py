import numpy as np
from typing import Tuple, List

def calculate_anomaly_score(current_frp: float, baseline_frp_history: List[float]) -> dict:
    """
    Implements robust MAD (Median Absolute Deviation) to avoid skewed normalizations.
    """
    if len(baseline_frp_history) < 8:
        return {"score": 0.0, "reason_codes": ["insufficient_baseline"]}

    median = np.median(baseline_frp_history)
    mad = np.median(np.abs(np.array(baseline_frp_history) - median))
    scale = 1.4826 * mad
    
    if scale < 1e-6:
        score = 0.0
    else:
        score = (current_frp - median) / scale

    reasons = []
    if score > 3.0:
        reasons.append("frp_above_baseline")
    
    return {"score": round(score, 2), "reason_codes": reasons}
