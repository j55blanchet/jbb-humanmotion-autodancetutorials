"""Pose analysis functions for computing motion metrics from landmark coordinates.

These helpers are coordinate-space agnostic and work with:
- Pixel coordinates
- Pixel coordinates relative to a reference (for example shoulders)
- Normalized relative coordinates
"""

import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from typing import Tuple, Sequence
from scipy.signal import savgol_filter, argrelmin, argrelmax


def sanitize_signal(values: np.ndarray) -> np.ndarray:
    """Return finite signal suitable for filtering.

    Replaces inf with NaN, then interpolates missing values. If all values are
    missing, returns zeros.
    """
    signal = np.asarray(values, dtype=float)
    signal[~np.isfinite(signal)] = np.nan
    if np.isnan(signal).all():
        return np.zeros_like(signal, dtype=float)

    s = Series(signal)
    s = s.interpolate(limit_direction='both')
    s = s.bfill().ffill().fillna(0.0)
    return s.to_numpy(dtype=float)


def smooth_signal(values: np.ndarray, window_length: int) -> np.ndarray:
    """Apply Savitzky-Golay smoothing when the signal is long enough.

    Returns the original finite signal unchanged when it is too short for the
    requested window.
    """
    signal = sanitize_signal(values)
    if len(signal) < 3:
        return signal

    window = max(3, int(window_length))
    if window % 2 == 0:
        window += 1
    if window > len(signal):
        window = len(signal) if len(signal) % 2 == 1 else len(signal) - 1
    if window < 3:
        return signal

    return np.asarray(savgol_filter(signal, window_length=window, polyorder=1), dtype=float)


def validate_normalized_landmarks(landmarks: DataFrame, context: str, max_abs_value: float = 50.0):
    """Raise when a metric helper receives obvious pixel-space coordinates.

    These helpers expect NORMALIZED RELATIVE COORDINATES:
    - Centered on reference joint pair midpoint (typically torso)
    - Scaled by distance between reference joints
    - Typical range: [-5, +5] for full-body motion

    NEVER pass pixel coordinates (range [0, width] or [0, height]).
    NEVER pass raw normalized [0, 1] coordinates from CSV.
    Use landmark_processing.normalize_landmarks() first.

    Args:
        landmarks: DataFrame of normalized relative coordinates
        context: Function name or context string for error message
        max_abs_value: Threshold for detecting mismatched coordinate space (default 50.0)

    Raises:
        ValueError: If landmark magnitude exceeds threshold
    """
    values = landmarks.to_numpy(dtype=float)
    finite_values = values[np.isfinite(values)]
    if finite_values.size == 0:
        return
    max_abs = float(np.max(np.abs(finite_values)))
    if max_abs > max_abs_value:
        raise ValueError(
            f'{context} expects normalized relative coordinates, but received values with '
            f'absolute magnitude {max_abs:.2f}. Did you pass pixel coordinates before normalization?'
        )


def get_extension(landmarks: DataFrame, smooth_window: int) -> Series:
    """Compute per-frame extension from landmark coordinates.

    Extension is the mean Euclidean distance of all landmarks from origin,
    normalized by landmark count. Smoothed via Savitzky-Golay filter.

    COORDINATE SPACE: Works with pixel or normalized coordinates.

    Args:
        landmarks: DataFrame of coordinates, shape (n_frames, 2*n_landmarks)
        smooth_window: Savitzky-Goyal window length (must be odd)

    Returns:
        1D array of smoothed extension values per frame
    """
    extension = landmarks.apply(np.linalg.norm, axis=1)
    extension = extension / (len(landmarks.columns) / 2)
    smoothed_extension = smooth_signal(extension.to_numpy(dtype=float), smooth_window)
    return Series(smoothed_extension, index=landmarks.index)


def get_individual_extensions(landmarks: DataFrame, smooth_window: int) -> DataFrame:
    """Compute per-limb extension from landmark coordinates.

    For each joint pair (x, y), compute Euclidean distance from origin,
    then apply Savitzky-Golay smoothing.

    COORDINATE SPACE: Works with pixel or normalized coordinates.

    Args:
        landmarks: DataFrame of coordinates, shape (n_frames, 2*n_landmarks)
        smooth_window: Savitzky-Golay window length (must be odd)

    Returns:
        DataFrame indexed by frame, columns are <jointName> with extension values
    """
    extensions = DataFrame(index=landmarks.index)
    for col_i in range(0, len(landmarks.columns), 2):
        col_name = landmarks.columns[col_i].replace('_x', '')
        xy = landmarks.iloc[:, col_i:col_i + 2]
        ext = xy.apply(np.linalg.norm, axis=1)
        extensions[col_name] = Series(smooth_signal(ext.to_numpy(dtype=float), smooth_window), index=landmarks.index)
    return extensions


def get_extrema(data: Series | np.ndarray, frame_window: int):
    """Find local minima and maxima in data.
    
    Args:
        data: 1D array-like data to find extrema in
        frame_window: Minimum distance between extrema (in frames)
        
    Returns:
        Tuple of (indices_minima, indices_maxima, all_extrema)
    """
    values = np.asarray(data, dtype=float)
    indices_minima = argrelmin(values, order=frame_window)[0]
    indices_maxima = argrelmax(values, order=frame_window)[0]
    all_extrema: np.ndarray = np.concatenate((indices_minima, indices_maxima))
    all_extrema.sort()
    return indices_minima, indices_maxima, all_extrema


def get_net_movement(landmarks: pd.DataFrame):
    """Compute total Euclidean distance traveled (per frame) from landmark coordinates.

    Sums the distances of all landmark displacements in one frame.

    COORDINATE SPACE: Works with pixel or normalized coordinates.

    Args:
        landmarks: DataFrame of coordinates

    Returns:
        Float, total distance traveled in input coordinate space
    """
    velocities = landmarks.diff().iloc[1:]
    spds = velocities.abs()
    accumulated_motion = spds.apply(np.trapezoid, axis=0)
    return accumulated_motion.sum()


def get_cartesian_distance(landmarks: pd.DataFrame, frame1: int, frame2: int):
    """Compute Cartesian distance between two frames.
    
    Args:
        landmarks: DataFrame of coordinates
        frame1: First frame index
        frame2: Second frame index
        
    Returns:
        Combined distance of all x and y components
    """
    x_velocities = landmarks.iloc[:, 0::2]
    y_velocities = landmarks.iloc[:, 1::2]
    return np.linalg.norm(x_velocities.iloc[frame1] - x_velocities.iloc[frame2]) + np.linalg.norm(y_velocities.iloc[frame1] - y_velocities.iloc[frame2])


def get_horz_vert_velocities(landmarks: DataFrame, smooth_window: int) -> Tuple[Series, Series]:
    """Compute horizontal and vertical velocity components from landmark coordinates.

    Separates 2D velocity into x and y components using Savitzky-Golay smoothing.

    COORDINATE SPACE: Works with pixel or normalized coordinates.

    Args:
        landmarks: DataFrame of coordinates
        smooth_window: Savitzky-Golay window length (must be odd)

    Returns:
        Tuple of (horizontal_velocities, vertical_velocities)
    """
    velocity = landmarks.diff()
    x_velocities = velocity.iloc[:, 0::2]
    y_velocities = velocity.iloc[:, 1::2]
    net_x_vel = sanitize_signal(x_velocities.sum(axis=1).to_numpy(dtype=float))
    net_y_vel = sanitize_signal(y_velocities.sum(axis=1).to_numpy(dtype=float))
    net_x_vel = Series(smooth_signal(net_x_vel, smooth_window), index=landmarks.index)
    net_y_vel = Series(smooth_signal(net_y_vel, smooth_window), index=landmarks.index)
    return net_x_vel, net_y_vel


def get_spds(landmarks: DataFrame, smooth_window: int):
    """Compute per-landmark speed from landmark coordinates.

    Speed is the Euclidean norm of velocity (change in position per frame).
    Computed after Savitzky-Goyal smoothing.

    COORDINATE SPACE: Works with pixel or normalized coordinates.

    Args:
        landmarks: DataFrame of coordinates, shape (n_frames, 2*n_landmarks)
        smooth_window: Savitzky-Golay window length (must be odd)

    Returns:
        DataFrame indexed by frame, columns are <jointName> with speed values
    """
    smoothed_values = landmarks.to_numpy(dtype=float)
    for col_i in range(smoothed_values.shape[1]):
        col_signal = sanitize_signal(smoothed_values[:, col_i])
        smoothed_values[:, col_i] = smooth_signal(col_signal, smooth_window)
    smoothed_lms = DataFrame(smoothed_values, index=landmarks.index, columns=landmarks.columns)
    velocity = smoothed_lms.diff()
    spds = DataFrame()
    for col_i in range(0, len(landmarks.columns), 2):
        col_name = landmarks.columns[col_i].replace('_x', '')
        vels = velocity.iloc[:, col_i:col_i+1]    
        spd = vels.apply(np.linalg.norm, axis=1)
        spds[col_name] = spd

    return spds


def get_spd_minima(landmarks: DataFrame, smooth_window: int, extrema_window: int):
    """Find frames where velocity is locally minimal from landmark coordinates.

    Useful for keyframe selection (slowest moments = good keyframes).

    COORDINATE SPACE: Works with pixel or normalized coordinates.

    Args:
        landmarks: DataFrame of coordinates
        smooth_window: Savitzky-Golay window for computing speeds
        extrema_window: Minimum distance between detected minima (in frames)

    Returns:
        Array of frame indices where speed is locally minimal
    """
    x, y = get_horz_vert_velocities(landmarks, smooth_window)
    net_spd = abs(x) + abs(y)
    minima = argrelmax(net_spd, order=extrema_window)[0]
    return minima


def correlation_by_segment(a: Series, b: Series, segments: Sequence[Tuple[int, int]]):
    """Compute correlation between two series within specified segments.
    
    Args:
        a: First data series
        b: Second data series
        segments: Sequence of (start, end) frame indices defining segments
        
    Returns:
        List of correlation coefficients for each segment (NaN if undefined)
    """
    def generate_correlations():
        for start_i, end_i in segments:
            a_segment = a.iloc[start_i:end_i]
            b_segment = b.iloc[start_i:end_i]

            a_vals = a_segment.to_numpy(dtype=float)
            b_vals = b_segment.to_numpy(dtype=float)

            valid = np.isfinite(a_vals) & np.isfinite(b_vals)
            a_vals = a_vals[valid]
            b_vals = b_vals[valid]

            # Correlation is undefined for tiny or constant segments.
            if len(a_vals) < 2 or len(b_vals) < 2:
                yield np.nan
                continue
            if np.nanstd(a_vals) == 0 or np.nanstd(b_vals) == 0:
                yield np.nan
                continue

            yield float(np.corrcoef(a_vals, b_vals)[0, 1])

    return list(generate_correlations())


def get_times(data: DataFrame, fps: float):
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


def get_segments(start_frame: int, boundries, end_frame: int):
    """Create segment boundaries from frame indices.
    
    Args:
        start_frame: Starting frame index
        boundries: Frame indices marking segment boundaries
        end_frame: Ending frame index
        
    Returns:
        List of (start, end) tuples for each segment
    """
    from itertools import chain
    return [
        (start_i, end_i) for start_i, end_i in zip(
            chain([0], boundries),
            chain(boundries, [end_frame])
        )
    ]


def get_correlations(df: DataFrame):
    """Compute and print all pairwise correlations between columns.
    
    Args:
        df: DataFrame with columns to correlate
    """
    for i in range(len(df.columns)):
        for j in range(i+1, len(df.columns)):
            corr = df.iloc[:, i:j+1].corr().iloc[0, 1]
            print(f'{df.columns[i]} and {df.columns[j]} = {corr}')
    pass
