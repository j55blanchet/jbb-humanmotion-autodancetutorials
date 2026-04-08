


"""Pose identification and keyframe analysis utilities.

This module provides utility functions for identifying keyframes and analyzing poses
from pose landmark data. Core analysis functions have been moved to specialized modules:
- pose_analysis.py: Motion metrics computation (extension, velocity, correlation)
- pose_metrics_plotting.py: Visualization functions
"""

from pathlib import Path
from typing import List, Tuple, Sequence
import pandas as pd
from pandas import DataFrame
from itertools import chain

# Re-export main analysis functions for backward compatibility
from .pose_analysis import (
    validate_normalized_landmarks,
    get_extension,
    get_individual_extensions,
    get_extrema,
    get_net_movement,
    get_cartesian_distance,
    get_horz_vert_velocities,
    get_spds,
    get_spd_minima,
    correlation_by_segment,
    get_correlations,
)

from .pose_metrics_plotting import (
    plot_extension,
    plot_correlations,
    plot_movement_extension,
)

######
# TODO:
#    * Create keyframe selector which varies keyframe density based on accumulated movement.
#####

def get_times(data: DataFrame, fps: float) -> List[float]:
    """Convert frame indices to time values.
    
    Args:
        data: DataFrame with frame indices
        fps: Frames per second
        
    Returns:
        DataFrame with time values in seconds
    """
    indices = data.index.to_frame()
    indices /= fps
    return indices

def get_segments(start_frame: int, boundries: int, end_frame: int):
    """Create segment boundaries from frame indices.
    
    Args:
        start_frame: Starting frame index
        boundries: Frame indices marking segment boundaries
        end_frame: Ending frame index
        
    Returns:
        List of (start, end) tuples for each segment
    """
    return [
        (start_i, end_i) for start_i, end_i in zip(
            chain([0], boundries),
            chain(boundries, [end_frame])
        )
    ]