


# %%
from matplotlib.axes import Axes
import numpy as np
from os import PathLike
from pathlib import Path
import pandas as pd
from pandas import DataFrame, Series
from typing import List, Tuple, Sequence
from .landmark_processing import choose_landmarks

from scipy.signal import savgol_filter, windows, argrelmin, argrelmax
import matplotlib.pyplot as plt
from itertools import chain


######
# TODO:
#    * Create keyframe selector which varies keyframe density based on accumulated movement.
#####


def validate_normalized_landmarks(landmarks: DataFrame, context: str, max_abs_value: float = 50.0):
    """Raise when a metric helper receives obvious pixel-space coordinates.

    These helpers expect normalized, torso-centered coordinates produced by
    landmark_processing.normalize_landmarks() and choose_landmarks().
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

def get_extension(landmarks: DataFrame, smooth_window: int) -> DataFrame:
    """Compute per-frame extension from normalized relative landmark coordinates."""
    validate_normalized_landmarks(landmarks, 'get_extension')
    extension = landmarks.apply(np.linalg.norm, axis=1)    
    extension = extension / (len(landmarks.columns) / 2)
    smoothed_extension = savgol_filter(extension, window_length=smooth_window, polyorder=1)
    return smoothed_extension


def get_individual_extensions(landmarks: DataFrame, smooth_window: int) -> DataFrame:
    """Compute per-limb extension from normalized relative landmark coordinates."""
    validate_normalized_landmarks(landmarks, 'get_individual_extensions')
    extensions = DataFrame(index=landmarks.index)
    for col_i in range(0, len(landmarks.columns), 2):
        col_name = landmarks.columns[col_i].replace('_x', '')
        xy = landmarks.iloc[:, col_i:col_i + 2]
        ext = xy.apply(np.linalg.norm, axis=1)
        extensions[col_name] = savgol_filter(ext, window_length=smooth_window, polyorder=1)
    return extensions

def get_extrema(data: DataFrame, frame_window: int):
    indices_minima = argrelmin(data, order=frame_window)[0]
    indices_maxima = argrelmax(data, order=frame_window)[0]
    all_extrema: np.ndarray = np.concatenate((indices_minima, indices_maxima))
    all_extrema.sort()
    return indices_minima, indices_maxima, all_extrema

def get_times(data: DataFrame, fps: float) -> List[float]:
    indices = data.index.to_frame()
    indices /= fps
    return indices

def plot_extension(times: DataFrame, extension: DataFrame, individual_extensions: DataFrame, minima: np.ndarray, maxima: np.ndarray, ax: Axes, fps: float):
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
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:0.2f}s'))
    ax.legend(loc='upper right', fontsize='x-small')

# %%
# import sys; sys.path.insert(0, '..')
# import cv2
# from thumbnail import get_thumbnails

# getup_video_path = 'data/2d/videos/tiktok/getup.mp4'
# getup_thumbnails = get_thumbnails(
#     getup_video_path,
#     indices_maxima
# )

# for i, thumbnail_mimg in enumerate(getup_thumbnails):
#     rgb_img = cv2.cvtColor(thumbnail_mimg, cv2.COLOR_BGR2RGB) #Converts from one colour space to the other
    
#     # plt.im
#     plt.imshow(rgb_img)
#     plt.show()
    

# plt.show()

def get_net_movement(landmarks: pd.DataFrame):
    """Compute accumulated movement from normalized relative landmark coordinates."""
    validate_normalized_landmarks(landmarks, 'get_net_movement')
    velocities = landmarks.diff().iloc[1:]
    spds = velocities.abs()
    accumulated_motion = spds.apply(np.trapezoid, axis=0)
    return accumulated_motion.sum()

def get_cartesian_distance(landmarks: pd.DataFrame, frame1: int, frame2: int):

    x_velocities = landmarks.iloc[:, 0::2]
    y_velocities = landmarks.iloc[:, 1::2]
    return np.linalg.norm(x_velocities.iloc[frame1] - x_velocities.iloc[frame2]) + np.linalg.norm(y_velocities.iloc[frame1] - y_velocities.iloc[frame2])
    
def get_horz_vert_velocities(landmarks: DataFrame, smooth_window: int):
    """Compute horizontal and vertical velocities from normalized relative coordinates."""
    validate_normalized_landmarks(landmarks, 'get_horz_vert_velocities')
    velocity = landmarks.diff()
    x_velocities = velocity.iloc[:, 0::2]
    y_velocities = velocity.iloc[:, 1::2]
    net_x_vel = x_velocities.sum(axis=1)
    net_y_vel = y_velocities.sum(axis=1)
    net_x_vel = savgol_filter(net_x_vel, window_length=smooth_window, polyorder=1)
    net_y_vel = savgol_filter(net_y_vel, window_length=smooth_window, polyorder=1)
    return net_x_vel, net_y_vel

def get_spds(landmarks: DataFrame, smooth_window: int):
    """Compute per-landmark speed from normalized relative landmark coordinates."""
    validate_normalized_landmarks(landmarks, 'get_spds')
    def smooth(x):
        return savgol_filter(x, window_length=smooth_window, polyorder=1)
    smoothed_lms = landmarks.apply(smooth, axis=0)
    velocity = smoothed_lms.diff()
    spds = DataFrame()
    for col_i in range(0, len(landmarks.columns), 2):
        col_name = landmarks.columns[col_i].replace('_x', '')
        vels = velocity.iloc[:, col_i:col_i+1]    
        spd = vels.apply(np.linalg.norm, axis=1)
        spds[col_name] = spd

    return spds

def get_segments(start_frame: int, boundries: int, end_frame: int):
    from itertools import chain
    return [
        (start_i, end_i) for start_i, end_i in zip(
            chain([0], boundries),
            chain(boundries, [end_frame])
        )
    ]
    
def get_spd_minima(landmarks: DataFrame, smooth_window: int, extrema_window: int):
    x, y = get_horz_vert_velocities(landmarks, smooth_window)
    net_spd = abs(x) + abs(y)
    minima = argrelmax(net_spd, order=extrema_window)[0]
    return minima

def correlation_by_segment(a: Series, b: Series, segments: Sequence[Tuple[int, int]]):
    def generate_correlations():
        for start_i, end_i in segments:
            a_segment = a[start_i:end_i]
            b_segment = b[start_i:end_i]

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

def plot_correlations(segments: Sequence[Tuple[int, int]], correlations: Sequence[int], times: DataFrame, ax: Axes):
    for i, ((start_i, end_i), correlation) in enumerate(zip(segments, correlations)):
        selection_times = times.iloc[start_i: end_i].iloc[:, 0]
        correlation = 0 if np.isnan(correlation) else correlation
        ax.fill_between(selection_times, correlation, label=f'Segment {i}')
    ax.set_ylim(-1, 1)

def get_correlations(df: DataFrame):
    for i in range(len(df.columns)):
        for j in range(i+1, len(df.columns)):
            corr = df.iloc[:, i:j+1].corr().iloc[0, 1]
            print(f'{df.columns[i]} and {df.columns[j]} = {corr}')
    pass
# %%
def plot_movement_extension(landmarks: DataFrame, fps: float, smooth_window: int, extrema_window: int, ax_spds: Axes, ax_spdcorrelation: Axes, ax_movement_net: Axes, ax_extension: Axes):

    ax_spdcorrelation.sharex(ax_movement_net)
    ax_extension.sharex(ax_movement_net)

    hand_spds = get_spds(landmarks, smooth_window)
    net_x_vel, net_y_vel = get_horz_vert_velocities(landmarks, smooth_window)
    net_spd = abs(net_x_vel) + abs(net_y_vel)
    spd_minima = argrelmin(net_spd, order=extrema_window)[0]

    extension = get_extension(landmarks, smooth_window = smooth_window)
    individual_extensions = get_individual_extensions(landmarks, smooth_window=smooth_window)
    extension_minima, extension_maxima, _ = get_extrema(extension, extrema_window)
    
    times = get_times(landmarks, fps)
    hand_spds_over_time = hand_spds.set_index(hand_spds.index.map(lambda x: times.loc[x]))
    
    segments = get_segments(0, spd_minima, len(landmarks) - 1)

    cols = hand_spds_over_time.columns.to_list()
    leftWrist = hand_spds_over_time[cols[0]]
    rightWrist = hand_spds_over_time[cols[1]]
    correlations = correlation_by_segment(leftWrist, rightWrist, segments)
    
    hand_spds_over_time.plot(ax=ax_spds, legend=True)
    ax_spds.yaxis.set_visible(False)
    ax_spds.xaxis.set_visible(False)

    plot_correlations(segments, correlations, times, ax_spdcorrelation)
    ax_spdcorrelation.yaxis.set_visible(False)
    ax_spdcorrelation.yaxis.set_ticks([])
    ax_spdcorrelation.xaxis.set_ticks([])

    # ax_movement_net.set_title('Movement')
    ax_movement_net.plot(times, net_spd, label="Net Movement")
    ax_movement_net.plot(times.iloc[spd_minima], net_spd[spd_minima], 'o', label="Minima")
    # ax_movement_net.legend()
    ax_movement_net.yaxis.set_visible(False)
    ax_movement_net.xaxis.set_visible(False)

    alternator = False
    for i in spd_minima:
        alternator = not alternator
        time = times.iat[i, 0]
        ax_movement_net.annotate(f"{time:0.2f}s", (times.iat[i, 0], net_spd[i]), xytext=(0, -5 if alternator else 5), textcoords='offset pixels', fontsize='x-small', horizontalalignment='center', verticalalignment='top' if alternator else 'bottom')

    plot_extension(times, extension, individual_extensions, extension_minima, extension_maxima, ax_extension, fps)
    # ax_extension.set_title('Extension')
    ax_extension.yaxis.set_visible(False)

# %%
# def get_poses_spd_accumulation(landmarks: DataFrame):
#     x, y = get_horz_vert_velocities(landmarks, smooth_window=5)
#     spd = abs(x) + abs(y)
#     poses = get_poses(landmarks)
#     poses_spd = pd.concat([poses, pd.DataFrame(spd, columns=['spd'])], axis=1)
#     poses_spd = poses_spd.groupby(['pose']).agg({'spd': 'sum'})
#     poses_spd = poses_spd.reset_index()
#     return poses_spd