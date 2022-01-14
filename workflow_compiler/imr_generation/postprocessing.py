import pandas as pd
import numpy as np

def insert_prune_keyframes(startTime: float, endTime: float, kfs: np.ndarray, max_kfspacing: float = 0.2, min_kf_spacing: float = 0.05):
    target_spacing = (max_kfspacing + min_kf_spacing) / 2
    yield startTime
    last = startTime
    for i, kf in enumerate(kfs):
        kf: float = kf
        elapsed = kf - last
        if elapsed > max_kfspacing:
            # Keyframe is too far apart! Yield intermediary kfs
            num_intermediaries = int(elapsed // target_spacing)
            spacing = elapsed / num_intermediaries
            
            for kf_intermediary in np.linspace(last + spacing, kf, num_intermediaries, endpoint=True):
                kf_intermediary: float = kf_intermediary
                yield kf_intermediary
                last = kf_intermediary

        elif elapsed < min_kf_spacing:
            # Skip this keyframe
            continue

        else:
            yield kf
            last = kf
            
    yield endTime