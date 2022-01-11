


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

def get_extension(landmarks: DataFrame, smooth_window: int) -> DataFrame:
    extension = landmarks.apply(np.linalg.norm, axis=1)    
    extension = extension / (len(landmarks.columns) / 2)
    smoothed_extension = savgol_filter(extension, window_length=smooth_window, polyorder=1)
    return smoothed_extension

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

def plot_extension(times: DataFrame, extension: DataFrame, minima: np.ndarray, maxima: np.ndarray, ax: Axes, fps: float):

    ax.plot(times, extension, label=f'Extension')
    ax.plot(times.iloc[maxima], extension[maxima], 'o', label='Extension')
    ax.plot(times.iloc[minima], extension[minima], 'o', label='Retraction')

    for i in maxima:
        time = times.iloc[i, 0]
        ax.annotate(f'{time:0.2f}s', (times.iloc[i], extension[i]), xytext=(0, 5), textcoords='offset pixels', fontsize='x-small', horizontalalignment='center', verticalalignment='bottom')
    for i in minima:
        time = times.iloc[i, 0]
        ax.annotate(f'{time:0.2f}s', (times.iloc[i], extension[i]), xytext=(0, -5), textcoords='offset pixels', fontsize='x-small', horizontalalignment='center', verticalalignment='top')
            
    ax.set_ylabel('Extension (relative to torso)')
    ax.set_xlabel('Time')
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:0.2f}s'))

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
    import scipy.integrate
    velocities = landmarks.diff().iloc[1:]
    spds = velocities.abs()
    accumulated_motion = spds.apply(scipy.integrate.trapz, axis=0)
    return accumulated_motion.sum()

def get_cartesian_distance(landmarks: pd.DataFrame, frame1: int, frame2: int):

    x_velocities = landmarks.iloc[:, 0::2]
    y_velocities = landmarks.iloc[:, 1::2]
    return np.linalg.norm(x_velocities.iloc[frame1] - x_velocities.iloc[frame2]) + np.linalg.norm(y_velocities.iloc[frame1] - y_velocities.iloc[frame2])
    
def get_horz_vert_velocities(landmarks: DataFrame, smooth_window: int):
    velocity = landmarks.diff()
    x_velocities = velocity.iloc[:, 0::2]
    y_velocities = velocity.iloc[:, 1::2]
    net_x_vel = x_velocities.sum(axis=1)
    net_y_vel = y_velocities.sum(axis=1)
    net_x_vel = savgol_filter(net_x_vel, window_length=smooth_window, polyorder=1)
    net_y_vel = savgol_filter(net_y_vel, window_length=smooth_window, polyorder=1)
    return net_x_vel, net_y_vel

def get_spds(landmarks: DataFrame, smooth_window: int):
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
            yield a_segment.corr(b_segment)

    return list(generate_correlations())

def plot_correlations(segments: Sequence[Tuple[int, int]], correlations: Sequence[int], times: DataFrame, ax: Axes):
    for i, ((start_i, end_i), correlation) in enumerate(zip(segments, correlations)):
        selection_times = times.iloc[start_i: end_i].iloc[:, 0]
        correlation = 0 if np.isnan(correlation) else correlation
        ax.fill_between(selection_times, correlation, label=f'Segment {i}')

def get_correlations(df: DataFrame):
    for i in range(len(df.columns)):
        for j in range(i+1, len(df.columns)):
            corr = df.iloc[:, i:j+1].corr().iloc[0, 1]
            print(f'{df.columns[i]} and {df.columns[j]} = {corr}')
    pass
# %%
def plot_movement_extension(landmarks: DataFrame, fps: float, smooth_window: int, extrema_window: int, ax_spds: Axes, ax_spdcorrelation: Axes, ax_spd_horz_vs_vertical: Axes, ax_movement_net: Axes, ax_extension: Axes):

    # ax_spds.sharex(ax_spd_horz_vs_vertical)
    ax_spdcorrelation.sharex(ax_spd_horz_vs_vertical)
    ax_movement_net.sharex(ax_spd_horz_vs_vertical)
    ax_extension.sharex(ax_spd_horz_vs_vertical)

    hand_spds = get_spds(landmarks, smooth_window)
    net_x_vel, net_y_vel = get_horz_vert_velocities(landmarks, smooth_window)
    net_spd = abs(net_x_vel) + abs(net_y_vel)
    spd_minima = argrelmin(net_spd, order=extrema_window)[0]

    extension = get_extension(landmarks, smooth_window = smooth_window)
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

    ax_spd_horz_vs_vertical.yaxis.set_ticks([])
    ax_spd_horz_vs_vertical.plot(times, net_x_vel, label="Horizontal")
    ax_spd_horz_vs_vertical.plot(times, net_y_vel, label="Vertical")
    ax_spd_horz_vs_vertical.legend()
    ax_spd_horz_vs_vertical.yaxis.set_visible(False)
    ax_spd_horz_vs_vertical.xaxis.set_visible(False)

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

    plot_extension(times, extension, extension_minima, extension_maxima, ax_extension, fps)
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