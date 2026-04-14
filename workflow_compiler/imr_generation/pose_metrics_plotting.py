"""Plotting utilities for pose metrics visualization."""

import numpy as np
import pandas as pd
from pandas import DataFrame
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from typing import TypedDict
from typing import Sequence, Tuple

from .pose_analysis import (
    get_extension,
    get_individual_extensions,
    get_extrema,
    get_spds,
    get_horz_vert_velocities,
    correlation_by_segment,
    get_times,
    get_segments,
)


class MovementExtensionMetrics(TypedDict):
    times: DataFrame
    hand_spds_over_time: DataFrame
    segments: Sequence[Tuple[int, int]]
    correlations: Sequence[float]
    net_spd: pd.Series
    spd_minima: np.ndarray
    extension: pd.Series
    individual_extensions: DataFrame
    extension_minima: np.ndarray
    extension_maxima: np.ndarray


def plot_extension(times: DataFrame, extension: pd.Series, individual_extensions: DataFrame, minima: np.ndarray, maxima: np.ndarray, ax: Axes):
    """Plot extension (reach distance) over time with extrema marked.
    
    Args:
        times: Time values for x-axis
        extension: Overall extension values
        individual_extensions: Per-limb extension values
        minima: Frame indices of extension minima
        maxima: Frame indices of extension maxima
        ax: Matplotlib axes to plot on
    """
    time_values = times.iloc[:, 0]

    if len(individual_extensions.columns) >= 1:
        ax.plot(time_values, individual_extensions.iloc[:, 0], label='Left Arm Extension', alpha=0.7)
    if len(individual_extensions.columns) >= 2:
        ax.plot(time_values, individual_extensions.iloc[:, 1], label='Right Arm Extension', alpha=0.7)

    ax.plot(time_values, extension, label='Combined Extension', linewidth=1.8)
    ax.plot(time_values.iloc[maxima], extension[maxima], 'o', label='Extension')
    ax.plot(time_values.iloc[minima], extension[minima], 'o', label='Retraction')

    for i in maxima:
        time = time_values.iloc[i]
        ax.annotate(f'{time:0.2f}s', (time_values.iloc[i], extension[i]), xytext=(0, 5), textcoords='offset pixels', fontsize='x-small', horizontalalignment='center', verticalalignment='bottom')
    for i in minima:
        time = time_values.iloc[i]
        ax.annotate(f'{time:0.2f}s', (time_values.iloc[i], extension[i]), xytext=(0, -5), textcoords='offset pixels', fontsize='x-small', horizontalalignment='center', verticalalignment='top')
            
    ax.set_ylabel('Extension (relative to torso)')
    ax.set_xlabel('Time')
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:0.2f}s'))
    ax.legend(loc='upper right', fontsize='x-small')


def plot_correlations(segments: Sequence[Tuple[int, int]], correlations: Sequence[float], times: DataFrame, ax: Axes):
    """Plot correlations between segments as filled areas.
    
    Args:
        segments: Sequence of (start, end) frame indices for each segment
        correlations: Correlation coefficient for each segment
        times: Time values for x-axis
        ax: Matplotlib axes to plot on
    """
    for i, ((start_i, end_i), correlation) in enumerate(zip(segments, correlations)):
        selection_times = times.iloc[start_i: end_i].iloc[:, 0]
        correlation = 0 if np.isnan(correlation) else correlation
        ax.fill_between(selection_times, correlation, label=f'Segment {i}')
    ax.set_ylim(-1, 1)


def compute_movement_extension_metrics(hand_landmarks: DataFrame, fps: float, smooth_window: int, extrema_window: int) -> MovementExtensionMetrics:
    """Compute movement/extension metrics from hand landmark coordinates.

    Args:
        hand_landmarks: DataFrame of hand coordinates (pixel or normalized)
        fps: Frames per second
        smooth_window: Savitzky-Goyal window for velocity computation
        extrema_window: Frame window for extrema detection

    Returns:
        Dictionary of derived metric series and indices used by plotting.
    """
    from scipy.signal import argrelmin

    hand_spds = get_spds(hand_landmarks, smooth_window)
    net_x_vel, net_y_vel = get_horz_vert_velocities(hand_landmarks, smooth_window)
    net_spd = abs(net_x_vel) + abs(net_y_vel)
    spd_minima = argrelmin(net_spd.to_numpy(dtype=float), order=extrema_window)[0]

    extension = get_extension(hand_landmarks, smooth_window=smooth_window)
    individual_extensions = get_individual_extensions(hand_landmarks, smooth_window=smooth_window)
    extension_minima, extension_maxima, _ = get_extrema(extension, extrema_window)

    times = get_times(hand_landmarks, fps)
    time_values = times.iloc[:, 0].astype(float)
    hand_spds_over_time = hand_spds.copy()
    hand_spds_over_time.index = time_values

    segments = get_segments(0, spd_minima, len(hand_landmarks) - 1)

    cols = hand_spds_over_time.columns.to_list()
    if len(cols) < 2:
        raise ValueError('Expected at least two hand landmark speed columns for plotting.')

    leftWrist = hand_spds_over_time[cols[0]]
    rightWrist = hand_spds_over_time[cols[1]]
    correlations = correlation_by_segment(leftWrist, rightWrist, segments)

    return {
        'times': times,
        'hand_spds_over_time': hand_spds_over_time,
        'segments': segments,
        'correlations': correlations,
        'net_spd': net_spd,
        'spd_minima': spd_minima,
        'extension': extension,
        'individual_extensions': individual_extensions,
        'extension_minima': extension_minima,
        'extension_maxima': extension_maxima,
    }


def plot_movement_extension(metrics: MovementExtensionMetrics, ax_spds: Axes, ax_spdcorrelation: Axes, ax_movement_net: Axes, ax_extension: Axes):
    """Render movement/extension plots from precomputed metrics."""
    ax_spdcorrelation.sharex(ax_movement_net)
    ax_extension.sharex(ax_movement_net)

    times = metrics['times']
    hand_spds_over_time = metrics['hand_spds_over_time']
    segments = metrics['segments']
    correlations = metrics['correlations']
    net_spd = metrics['net_spd']
    spd_minima = metrics['spd_minima']
    extension = metrics['extension']
    individual_extensions = metrics['individual_extensions']
    extension_minima = metrics['extension_minima']
    extension_maxima = metrics['extension_maxima']

    hand_spds_over_time.plot(ax=ax_spds, legend=True)
    ax_spds.yaxis.set_visible(False)
    ax_spds.xaxis.set_visible(False)

    plot_correlations(segments, correlations, times, ax_spdcorrelation)
    ax_spdcorrelation.yaxis.set_visible(False)
    ax_spdcorrelation.yaxis.set_ticks([])
    ax_spdcorrelation.xaxis.set_ticks([])

    ax_movement_net.plot(times, net_spd, label="Net Movement")
    ax_movement_net.plot(times.iloc[spd_minima], net_spd[spd_minima], 'o', label="Minima")
    ax_movement_net.yaxis.set_visible(False)
    ax_movement_net.xaxis.set_visible(False)

    alternator = False
    for i in spd_minima:
        alternator = not alternator
        time = np.asarray(times.iat[i, 0], dtype=float).item()
        net_speed_at_i = np.asarray(net_spd[i], dtype=float).item()
        ax_movement_net.annotate(
            f"{time:0.2f}s",
            (time, net_speed_at_i),
            xytext=(0, -5 if alternator else 5),
            textcoords='offset pixels',
            fontsize='x-small',
            horizontalalignment='center',
            verticalalignment='top' if alternator else 'bottom',
        )

    plot_extension(times, extension, individual_extensions, extension_minima, extension_maxima, ax_extension)
    ax_extension.yaxis.set_visible(False)
