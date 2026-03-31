from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.signal import argrelmin, savgol_filter

from . import pose_identifier
from .landmark_processing import PoseLandmark, choose_landmarks


def gendered_movement_output_dir(analysis_dir: Path) -> Path:
    return analysis_dir / 'gendered_movement'


def gendered_movement_output_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return gendered_movement_output_dir(analysis_dir) / f'{clip_name}_hipshouldermovement.pdf'


def gendered_movement_data_filepath(analysis_dir: Path, clip_name: str) -> Path:
    metric_name = 'hipmovementshare'
    return gendered_movement_output_dir(analysis_dir) / f'{clip_name}_{metric_name}.csv'


def _normalized_window(window: int, series_length: int) -> int:
    window = max(3, int(window))
    if window % 2 == 0:
        window += 1
    if series_length < 3:
        return 3
    if window > series_length:
        window = series_length if series_length % 2 == 1 else series_length - 1
    return max(3, window)


def _smooth_positions(landmarks: pd.DataFrame, smooth_window: int) -> pd.DataFrame:
    if len(landmarks) < 3:
        return landmarks.copy()

    window = _normalized_window(smooth_window, len(landmarks))
    smoothed = landmarks.copy()
    for col in smoothed.columns:
        smoothed[col] = savgol_filter(smoothed[col].to_numpy(dtype=float), window_length=window, polyorder=1)
    return smoothed


def _pair_speed(landmarks: pd.DataFrame, smooth_window: int) -> np.ndarray:
    smoothed = _smooth_positions(landmarks, smooth_window=smooth_window)
    velocities = smoothed.diff().fillna(0.0)

    speeds: list[np.ndarray] = []
    for col_i in range(0, len(velocities.columns), 2):
        xy = velocities.iloc[:, col_i:col_i + 2].to_numpy(dtype=float)
        speeds.append(np.linalg.norm(xy, axis=1))

    if not speeds:
        return np.zeros(len(landmarks), dtype=float)
    return np.mean(np.vstack(speeds), axis=0)


def _segment_summary(metrics: pd.DataFrame, fps: float) -> list[dict]:
    segment_window = max(3, int(round(fps * 2.0)))
    combined_speed = metrics['hip_speed'].to_numpy(dtype=float) + metrics['shoulder_speed'].to_numpy(dtype=float)
    segment_breaks = argrelmin(combined_speed, order=segment_window)[0]
    segments = pose_identifier.get_segments(0, segment_breaks, len(metrics) - 1)

    output: list[dict] = []
    for start_i, end_i in segments:
        seg = metrics.iloc[start_i:end_i + 1]
        if seg.empty:
            continue

        output.append(
            {
                'start_time': float(seg['time'].iloc[0]),
                'end_time': float(seg['time'].iloc[-1]),
                'hip_shoulder_share_mean': float(seg['hip_shoulder_share'].mean()),
                'hip_shoulder_share_median': float(seg['hip_shoulder_share'].median()),
                'hip_over_shoulder_ratio_mean': float(seg['hip_over_shoulder_ratio'].mean()),
                'hip_over_shoulder_ratio_median': float(seg['hip_over_shoulder_ratio'].median()),
                'hip_speed_mean': float(seg['hip_speed'].mean()),
                'shoulder_speed_mean': float(seg['shoulder_speed'].mean()),
            }
        )

    return output


def segmentation_share_summary(metrics: pd.DataFrame, segmentation_times: list[float]) -> list[dict]:
    output: list[dict] = []
    if len(segmentation_times) < 2:
        return output

    for start_time, end_time in zip(segmentation_times[:-1], segmentation_times[1:]):
        seg = metrics[(metrics['time'] >= start_time) & (metrics['time'] <= end_time)]
        if seg.empty:
            output.append(
                {
                    'start_time': float(start_time),
                    'end_time': float(end_time),
                    'hip_shoulder_share': None,
                }
            )
            continue

        output.append(
            {
                'start_time': float(start_time),
                'end_time': float(end_time),
                'hip_shoulder_share': float(seg['hip_shoulder_share'].mean()),
            }
        )

    return output


def compute_gendered_movement_metrics(
    pose_landmarks: pd.DataFrame,
    fps: float,
    smooth_window: int,
) -> tuple[pd.DataFrame, list[dict]]:
    hips = choose_landmarks(pose_landmarks, [PoseLandmark.leftHip, PoseLandmark.rightHip])
    shoulders = choose_landmarks(pose_landmarks, [PoseLandmark.leftShoulder, PoseLandmark.rightShoulder])

    hip_speed = _pair_speed(hips, smooth_window=smooth_window)
    shoulder_speed = _pair_speed(shoulders, smooth_window=smooth_window)

    eps = 1e-6
    raw_ratio = hip_speed / (shoulder_speed + eps)
    share = hip_speed / (hip_speed + shoulder_speed + eps)

    times = pose_identifier.get_times(pose_landmarks, fps).iloc[:, 0].to_numpy(dtype=float)
    metrics = pd.DataFrame(
        {
            'time': times,
            'hip_speed': hip_speed,
            'shoulder_speed': shoulder_speed,
            'hip_over_shoulder_ratio': raw_ratio,
            'hip_shoulder_share': share,
        }
    )
    return metrics, _segment_summary(metrics, fps=fps)


def plot_gendered_movement_metrics(
    metrics: pd.DataFrame,
    segment_summary: list[dict],
    clip_name: str,
    out_path: Path,
):
    t = metrics['time']

    fig, axs = plt.subplots(3, 1)
    fig.set_size_inches(6.0, 8.0)

    axs[0].plot(t, metrics['hip_speed'], label='Hip Speed', alpha=0.9)
    axs[0].plot(t, metrics['shoulder_speed'], label='Shoulder Speed', alpha=0.9)
    axs[0].set_ylabel('Speed')
    axs[0].legend(loc='upper right', fontsize='x-small')
    axs[0].xaxis.set_visible(False)

    axs[1].plot(t, metrics['hip_shoulder_share'], label='Hip Share', alpha=0.95)
    axs[1].set_ylim(0, 1)
    axs[1].set_yticks([0, 0.5, 1])
    axs[1].set_ylabel('Share')
    axs[1].legend(loc='upper right', fontsize='x-small')
    axs[1].xaxis.set_visible(False)

    axs[2].plot(t, metrics['hip_over_shoulder_ratio'], label='Hip/Shoulder Ratio', alpha=0.8)
    for seg in segment_summary:
        axs[2].axvspan(seg['start_time'], seg['end_time'], alpha=0.08, color='tab:orange')
        axs[2].hlines(
            seg['hip_over_shoulder_ratio_mean'],
            seg['start_time'],
            seg['end_time'],
            color='tab:red',
            linewidth=1.5,
        )
    axs[2].set_ylabel('Ratio')
    axs[2].set_xlabel('Time')
    axs[2].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:0.2f}s'))
    axs[2].legend(loc='upper right', fontsize='x-small')

    title = clip_name.replace('$', '\\$')
    fig.suptitle(f'Hip/Shoulder Movement Analysis: {title}')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(str(out_path))
    plt.close(fig)


def write_clip_gendered_movement_analysis(
    clip_name: str,
    pose_landmarks: pd.DataFrame,
    fps: float,
    smooth_window: int,
    analysis_dir: Path,
    segmentation_times: list[float] | None = None,
):
    metrics, segment_summary = compute_gendered_movement_metrics(
        pose_landmarks=pose_landmarks,
        fps=fps,
        smooth_window=smooth_window,
    )
    out_csv_path = gendered_movement_data_filepath(analysis_dir, clip_name)
    out_pdf_path = gendered_movement_output_filepath(analysis_dir, clip_name)
    out_csv_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(out_csv_path, index=False)

    plot_gendered_movement_metrics(
        metrics=metrics,
        segment_summary=segment_summary,
        clip_name=clip_name,
        out_path=out_pdf_path,
    )
