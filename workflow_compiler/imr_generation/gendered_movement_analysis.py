from __future__ import annotations

"""Gendered movement analysis and scalar motion feature extraction.

Motion Feature Extraction Spec (implemented subset for 2D pixel inputs)
=====================================================================
This module implements the clip-level scalar feature pipeline requested in the
project spec for YouTube + Mediapipe pose data.

Implemented preprocessing steps (P1-P9)
---------------------------------------
- P1 Joint subset: pelvis (from hips), hips, shoulders, wrists (+ optional head)
- P2 Visibility handling: if vis columns are present, low-visibility samples are
    masked and interpolated (up to short gaps); if no vis columns are present in
    input, finite-value masking is used with unit visibility weights
- P3 Temporal smoothing: Savitzky-Golay via pose_analysis.smooth_signal
- P4 Root-centered normalization: subtract pelvis/root per frame
- P5 Scale normalization: divide by median shoulder width
- P6 Root translation retained separately for global features
- P7 Derivatives: central differences using dt = 1 / fps
- P8 Time normalization: features are reduced to one scalar via weighted mean
- P9 Visibility weighting: weighted mean with per-frame visibility-derived weights

Implemented scalar features (2D)
--------------------------------
- HipSway_2D
- HipYawVar_2D
- Smoothness_2D (jerk magnitude, pelvis + wrists)
- Decoupling_2D (1 - max abs cross-correlation)
- ArmSparsity_2D (velocity thresholded at p70)
- Curvature_2D (pelvis + wrists)
- Optional global features: root_travel_distance, vertical_bounce

All scalar outputs are emitted per clip and can be aggregated into a single
root-level CSV by the batch runner.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.signal import argrelmin

from . import pose_analysis
from .landmark_processing import PoseLandmark, choose_landmarks


def gendered_movement_output_dir(analysis_dir: Path) -> Path:
    return analysis_dir / 'gendered_movement'


def gendered_movement_output_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return gendered_movement_output_dir(analysis_dir) / f'{clip_name}_hipshouldermovement.pdf'


def gendered_movement_data_filepath(analysis_dir: Path, clip_name: str) -> Path:
    metric_name = 'hipmovementshare'
    return gendered_movement_output_dir(analysis_dir) / f'{clip_name}_{metric_name}.csv'


def gendered_movement_ratio_filepath(analysis_dir: Path, clip_name: str) -> Path:
    metric_name = 'hipshoulderratio'
    return gendered_movement_output_dir(analysis_dir) / f'{clip_name}_{metric_name}.csv'


def gendered_movement_scalar_summary_filepath(analysis_dir: Path) -> Path:
    return analysis_dir / 'gendered_movement_scalar_summary.csv'


def gendered_movement_comparison_filepath(analysis_dir: Path, pair_base_name: str) -> Path:
    return gendered_movement_output_dir(analysis_dir) / f'{pair_base_name}_femme_vs_masc.pdf'


def _get_joint_xy(landmarks: pd.DataFrame, joint_name: str) -> np.ndarray:
    """Return Nx2 array for a joint from <joint>_x/<joint>_y columns."""
    return landmarks[[f'{joint_name}_x', f'{joint_name}_y']].to_numpy(dtype=float)


def _get_joint_visibility(landmarks: pd.DataFrame, joint_name: str) -> np.ndarray | None:
    """Return per-frame visibility for a joint when available, else None."""
    vis_col = f'{joint_name}_vis'
    if vis_col not in landmarks.columns:
        return None
    return landmarks[vis_col].to_numpy(dtype=float)


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
        smoothed[col] = pose_analysis.smooth_signal(smoothed[col].to_numpy(dtype=float), window)
    return smoothed


def _preprocess_joint_series(
    values: np.ndarray,
    visibility: np.ndarray | None,
    fps: float,
    smooth_window: int,
    interp_gap_max: int = 5,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Apply spec-aligned preprocessing to one joint coordinate stream.

    Relevant spec excerpts embedded:
    - P2: low-visibility samples are invalid, interpolate short gaps
    - P3: temporal smoothing (window 5-7)
    - P9: return per-frame weights for weighted means

    Returns:
        cleaned_values: NxD finite array
        weight: N-vector in [0, 1]
        interpolated_fraction: fraction of points filled by interpolation
    """
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    d = arr.shape[1] if arr.ndim == 2 else 1
    if arr.ndim == 1:
        arr = arr[:, None]

    finite_mask = np.all(np.isfinite(arr), axis=1)
    if visibility is None:
        valid_mask = finite_mask
        weight = np.ones(n, dtype=float)
    else:
        vis = np.asarray(visibility, dtype=float)
        valid_mask = finite_mask & (vis > 0.5)
        weight = np.clip(vis, 0.0, 1.0)

    cleaned = arr.copy()
    interpolated_points = 0
    for j in range(d):
        s = pd.Series(cleaned[:, j])
        s[~valid_mask] = np.nan
        before = s.isna().sum()
        s = s.interpolate(limit=interp_gap_max, limit_direction='both')
        after_interp = s.isna().sum()
        s = s.bfill().ffill()
        interpolated_points += int(before - after_interp)
        cleaned[:, j] = pose_analysis.sanitize_signal(s.to_numpy(dtype=float))

        # P3 smoothing with target window in [5, 7]
        target_window = 7 if smooth_window >= 7 else 5
        cleaned[:, j] = pose_analysis.smooth_signal(cleaned[:, j], target_window)

    interp_fraction = interpolated_points / max(1, n * d)
    if d == 1:
        cleaned = cleaned[:, 0]
    return cleaned, weight, interp_fraction


def _weighted_winsorized_mean(values: np.ndarray, weights: np.ndarray, q_low: float = 1.0, q_high: float = 99.0) -> float:
    """Compute weighted mean after percentile clipping (spec implementation note)."""
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if not np.any(mask):
        return float('nan')
    v = v[mask]
    w = w[mask]
    lo = np.percentile(v, q_low)
    hi = np.percentile(v, q_high)
    v = np.clip(v, lo, hi)
    return float(np.average(v, weights=w))


def _zscore(values: np.ndarray) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    mu = np.nanmean(v)
    sigma = np.nanstd(v)
    if not np.isfinite(sigma) or sigma == 0:
        return np.zeros_like(v)
    return (v - mu) / sigma


def _max_abs_xcorr(a: np.ndarray, b: np.ndarray, max_lag: int) -> float:
    """Max absolute cross-correlation over lag window."""
    a = _zscore(a)
    b = _zscore(b)
    max_lag = max(1, int(max_lag))
    best = 0.0
    n = len(a)
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            x = a[:n + lag]
            y = b[-lag:]
        elif lag > 0:
            x = a[lag:]
            y = b[:n - lag]
        else:
            x = a
            y = b
        if len(x) < 2 or len(y) < 2:
            continue
        if np.nanstd(x) == 0 or np.nanstd(y) == 0:
            continue
        c = np.corrcoef(x, y)[0, 1]
        if np.isfinite(c):
            best = max(best, abs(float(c)))
    return float(best)


def _derivatives(values: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Central-difference derivatives (P7): velocity, acceleration, jerk."""
    v = np.gradient(values, dt, axis=0)
    a = np.gradient(v, dt, axis=0)
    j = np.gradient(a, dt, axis=0)
    return v, a, j


def _curvature_2d(pos: np.ndarray, dt: float) -> np.ndarray:
    """Trajectory curvature (F1): |x'y''-y'x''| / (x'^2 + y'^2)^(3/2)."""
    v, a, _ = _derivatives(pos, dt)
    x1 = v[:, 0]
    y1 = v[:, 1]
    x2 = a[:, 0]
    y2 = a[:, 1]
    denom = np.power(np.maximum(x1 * x1 + y1 * y1, 1e-9), 1.5)
    num = np.abs(x1 * y2 - y1 * x2)
    return num / denom


def _pair_speed(landmarks: pd.DataFrame, smooth_window: int) -> np.ndarray:
    """Compute mean speed of a pair of landmarks (e.g., hips or shoulders).

    COORDINATE SPACE: Expects pixel coordinates to ensure isotropic speed calculation.
    Using normalized relative coordinates would introduce anisotropic scaling when
    video width != height, biasing hip vs. shoulder movement ratios.

    Args:
        landmarks: DataFrame with pixel coordinates, shape (n_frames, 2*n_landmarks)
        smooth_window: Window size for Savitzky-Golay smoothing

    Returns:
        1D array of mean speeds per frame, shape (n_frames,)
    """
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
    segments = pose_analysis.get_segments(0, segment_breaks, len(metrics) - 1)

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


def _scalar_summary(metrics: pd.DataFrame, clip_name: str) -> dict:
    """Return clip-level time-invariant scalar summary.

    Time-varying (duration-dependent) totals are intentionally omitted. Features
    are reported as means/ratios/proportions, or converted to rates.
    """
    hip_speed_mean = float(metrics['hip_speed'].mean())
    shoulder_speed_mean = float(metrics['shoulder_speed'].mean())
    hip_over_shoulder_ratio_overall = hip_speed_mean / shoulder_speed_mean if shoulder_speed_mean != 0 else float('nan')

    times = metrics['time'].to_numpy(dtype=float)
    clip_duration = float(times[-1] - times[0]) if len(times) >= 2 else float('nan')
    root_travel_distance = float(metrics['feature_root_travel_distance'].iloc[0])
    root_travel_rate = root_travel_distance / clip_duration if np.isfinite(clip_duration) and clip_duration > 0 else float('nan')

    return {
        'clipName': clip_name,
        'hip_over_shoulder_ratio_overall': hip_over_shoulder_ratio_overall,
        'hip_shoulder_share_overall': float(metrics['hip_shoulder_share'].mean()),
        'hip_speed_mean': hip_speed_mean,
        'shoulder_speed_mean': shoulder_speed_mean,
        'hip_over_shoulder_ratio_mean': float(metrics['hip_over_shoulder_ratio'].mean()),
        'hip_shoulder_share_mean': float(metrics['hip_shoulder_share'].mean()),
        'feature_hip_sway_2d': float(metrics['feature_hip_sway_2d'].iloc[0]),
        'feature_hip_yaw_var_2d': float(metrics['feature_hip_yaw_var_2d'].iloc[0]),
        'feature_smoothness_2d': float(metrics['feature_smoothness_2d'].iloc[0]),
        'feature_decoupling_2d': float(metrics['feature_decoupling_2d'].iloc[0]),
        'feature_arm_sparsity_2d': float(metrics['feature_arm_sparsity_2d'].iloc[0]),
        'feature_curvature_2d': float(metrics['feature_curvature_2d'].iloc[0]),
        'feature_root_travel_rate_2d': root_travel_rate,
        'feature_vertical_bounce': float(metrics['feature_vertical_bounce'].iloc[0]),
        'valid_frame_fraction': float(metrics['valid_frame_fraction'].iloc[0]),
        'interpolated_fraction': float(metrics['interpolated_fraction'].iloc[0]),
    }


def _estimate_fps(metrics: pd.DataFrame) -> float:
    times = metrics['time'].to_numpy(dtype=float)
    if len(times) < 2:
        return 30.0
    deltas = np.diff(times)
    positive_deltas = deltas[deltas > 0]
    if len(positive_deltas) == 0:
        return 30.0
    return float(1.0 / np.median(positive_deltas))


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


def _plot_gendered_metric_panels(axs: np.ndarray, metrics: pd.DataFrame, clip_name: str, segment_summary: list[dict]):
    t = metrics['time']

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
    axs[2].xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:0.2f}s'))
    axs[2].legend(loc='upper right', fontsize='x-small')

    title = clip_name.replace('$', '\\$')
    axs[0].set_title(title)


def plot_gendered_movement_comparison(
    left_metrics: pd.DataFrame,
    right_metrics: pd.DataFrame,
    left_clip_name: str,
    right_clip_name: str,
    out_path: Path,
):
    plt.close('all')  # Clear any existing figures to avoid duplication
    left_segments = _segment_summary(left_metrics, fps=_estimate_fps(left_metrics))
    right_segments = _segment_summary(right_metrics, fps=_estimate_fps(right_metrics))

    fig, axs = plt.subplots(3, 2, figsize=(12, 8), sharex='col', sharey='row')
    _plot_gendered_metric_panels(axs[:, 0], left_metrics, left_clip_name, left_segments)
    _plot_gendered_metric_panels(axs[:, 1], right_metrics, right_clip_name, right_segments)

    axs[0, 0].set_ylabel('Speed')
    axs[1, 0].set_ylabel('Share')
    axs[2, 0].set_ylabel('Ratio')
    axs[0, 1].set_ylabel('')
    axs[1, 1].set_ylabel('')
    axs[2, 1].set_ylabel('')

    fig.suptitle('Hip/Shoulder Movement Comparison: femme vs masc')
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path))
    plt.close(fig)


def compute_gendered_movement_metrics(
    pose_landmarks: pd.DataFrame,
    fps: float,
    smooth_window: int,
) -> tuple[pd.DataFrame, list[dict]]:
    """Compute hip/shoulder movement metrics from pixel pose coordinates.

    COORDINATE SPACE: Expects pixel coordinates to ensure isotropic speed metrics.
    Using normalized relative coordinates would introduce anisotropic scaling when
    video width != height, biasing the hip_shoulder_share and hip_over_shoulder_ratio
    calculations toward whichever axis has larger pixel dimensions.

    Args:
        pose_landmarks: DataFrame with pixel coordinates (shape: n_frames x 2*33 landmarks)
        fps: Frames per second
        smooth_window: Smoothing window for velocity calculation

    Returns:
        Tuple of (metrics DataFrame with time/speeds/ratios, segment summary list)
    """
    hips = choose_landmarks(pose_landmarks, [PoseLandmark.leftHip, PoseLandmark.rightHip])
    shoulders = choose_landmarks(pose_landmarks, [PoseLandmark.leftShoulder, PoseLandmark.rightShoulder])

    hip_speed = _pair_speed(hips, smooth_window=smooth_window)
    shoulder_speed = _pair_speed(shoulders, smooth_window=smooth_window)

    eps = 1e-6
    raw_ratio = hip_speed / (shoulder_speed + eps)
    share = hip_speed / (hip_speed + shoulder_speed + eps)

    times = pose_analysis.get_times(pose_landmarks, fps).iloc[:, 0].to_numpy(dtype=float)  # frame index to seconds

    # ---------------------------------------------------------------------
    # Spec feature extraction (2D) from root-centered and scale-normalized pose
    # ---------------------------------------------------------------------
    dt = 1.0 / max(float(fps), 1e-9)
    left_hip = _get_joint_xy(pose_landmarks, 'leftHip')
    right_hip = _get_joint_xy(pose_landmarks, 'rightHip')
    left_shoulder = _get_joint_xy(pose_landmarks, 'leftShoulder')
    right_shoulder = _get_joint_xy(pose_landmarks, 'rightShoulder')
    left_wrist = _get_joint_xy(pose_landmarks, 'leftWrist')
    right_wrist = _get_joint_xy(pose_landmarks, 'rightWrist')

    pelvis = 0.5 * (left_hip + right_hip)
    shoulder_mid = 0.5 * (left_shoulder + right_shoulder)
    root_traj = pelvis.copy()  # P6

    shoulder_width = np.linalg.norm(left_shoulder - right_shoulder, axis=1)
    scale = float(np.nanmedian(shoulder_width[np.isfinite(shoulder_width)])) if np.any(np.isfinite(shoulder_width)) else 1.0
    if not np.isfinite(scale) or scale <= 1e-9:
        scale = 1.0

    pelvis_vis = _get_joint_visibility(pose_landmarks, 'leftHip')
    right_hip_vis = _get_joint_visibility(pose_landmarks, 'rightHip')
    if pelvis_vis is not None and right_hip_vis is not None:
        pelvis_visibility = 0.5 * (pelvis_vis + right_hip_vis)
    else:
        pelvis_visibility = None

    pelvis_clean, pelvis_weight, pelvis_interp_frac = _preprocess_joint_series(pelvis, pelvis_visibility, fps, smooth_window)
    shoulder_clean, shoulder_weight, shoulder_interp_frac = _preprocess_joint_series(shoulder_mid, None, fps, smooth_window)
    left_wrist_clean, left_wrist_weight, left_wrist_interp_frac = _preprocess_joint_series(left_wrist, None, fps, smooth_window)
    right_wrist_clean, right_wrist_weight, right_wrist_interp_frac = _preprocess_joint_series(right_wrist, None, fps, smooth_window)

    # P4+P5: root-centered, scale-normalized streams
    pelvis_norm = (pelvis_clean - pelvis_clean) / scale
    shoulder_norm = (shoulder_clean - pelvis_clean) / scale
    left_wrist_norm = (left_wrist_clean - pelvis_clean) / scale
    right_wrist_norm = (right_wrist_clean - pelvis_clean) / scale
    root_norm = pelvis_clean / scale

    # Feature A: Hip sway amplitude (2D)
    pelvis_x_centered = root_norm[:, 0] - np.mean(root_norm[:, 0])
    hip_sway_2d = _weighted_winsorized_mean(np.abs(pelvis_x_centered), pelvis_weight)

    # Feature B: Hip rotation/yaw variance (2D approximate)
    hip_vec = (right_hip - left_hip) / scale
    hip_theta = np.arctan2(hip_vec[:, 1], hip_vec[:, 0])
    hip_yaw_var_2d = _weighted_winsorized_mean((hip_theta - np.mean(hip_theta)) ** 2, pelvis_weight)

    # Feature C: Smoothness from jerk magnitude (pelvis + wrists)
    _, _, pelvis_jerk = _derivatives(root_norm, dt)
    _, _, lw_jerk = _derivatives(left_wrist_norm, dt)
    _, _, rw_jerk = _derivatives(right_wrist_norm, dt)
    smoothness_signal = (
        np.linalg.norm(pelvis_jerk, axis=1)
        + np.linalg.norm(lw_jerk, axis=1)
        + np.linalg.norm(rw_jerk, axis=1)
    ) / 3.0
    smoothness_2d = _weighted_winsorized_mean(smoothness_signal, pelvis_weight)

    # Feature D: Upper-lower decoupling (1 - max |xcorr|)
    max_corr = _max_abs_xcorr(root_norm[:, 0], shoulder_norm[:, 0], max_lag=int(round(fps)))
    decoupling_2d = float(1.0 - max_corr)

    # Feature E: Arm activation sparsity (velocity > p70)
    lw_v, _, _ = _derivatives(left_wrist_norm, dt)
    rw_v, _, _ = _derivatives(right_wrist_norm, dt)
    arm_speed = 0.5 * (np.linalg.norm(lw_v, axis=1) + np.linalg.norm(rw_v, axis=1))
    arm_threshold = np.percentile(arm_speed[np.isfinite(arm_speed)], 70) if np.any(np.isfinite(arm_speed)) else np.nan
    arm_active = arm_speed > arm_threshold if np.isfinite(arm_threshold) else np.zeros_like(arm_speed, dtype=bool)
    arm_sparsity_2d = _weighted_winsorized_mean(arm_active.astype(float), pelvis_weight)

    # Feature F: Curvilinearity (pelvis + wrists)
    curvature_signal = (
        _curvature_2d(root_norm, dt)
        + _curvature_2d(left_wrist_norm, dt)
        + _curvature_2d(right_wrist_norm, dt)
    ) / 3.0
    curvature_2d = _weighted_winsorized_mean(curvature_signal, pelvis_weight)

    # Optional global features from root trajectory
    root_steps = np.diff(root_norm, axis=0)
    root_travel_distance = float(np.nansum(np.linalg.norm(root_steps, axis=1)))
    vertical_bounce = float(np.nanstd(root_norm[:, 1]))

    valid_frame_fraction = float(np.mean(np.isfinite(root_norm).all(axis=1)))
    interpolated_fraction = float(np.mean([pelvis_interp_frac, shoulder_interp_frac, left_wrist_interp_frac, right_wrist_interp_frac]))

    metrics = pd.DataFrame(
        {
            'time': times,
            'hip_speed': hip_speed,
            'shoulder_speed': shoulder_speed,
            'hip_over_shoulder_ratio': raw_ratio,
            'hip_shoulder_share': share,
            'feature_hip_sway_2d': hip_sway_2d,
            'feature_hip_yaw_var_2d': hip_yaw_var_2d,
            'feature_smoothness_2d': smoothness_2d,
            'feature_decoupling_2d': decoupling_2d,
            'feature_arm_sparsity_2d': arm_sparsity_2d,
            'feature_curvature_2d': curvature_2d,
            'feature_root_travel_distance': root_travel_distance,
            'feature_vertical_bounce': vertical_bounce,
            'valid_frame_fraction': valid_frame_fraction,
            'interpolated_fraction': interpolated_fraction,
        }
    )
    return metrics, _segment_summary(metrics, fps=fps)


def plot_gendered_movement_metrics(
    metrics: pd.DataFrame,
    segment_summary: list[dict],
    clip_name: str,
    out_path: Path,
):
    plt.close('all')  # Clear any existing figures to avoid duplication
    fig, axs = plt.subplots(3, 1)
    fig.set_size_inches(6.0, 8.0)
    _plot_gendered_metric_panels(axs, metrics, clip_name, segment_summary)

    fig.suptitle(f'Hip/Shoulder Movement Analysis: {clip_name.replace('$', '\\$')}')
    fig.tight_layout(rect=(0, 0, 1, 0.97))
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
    out_pdf_path = gendered_movement_output_filepath(analysis_dir, clip_name)
    out_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    scalar_summary = _scalar_summary(metrics, clip_name)

    plot_gendered_movement_metrics(
        metrics=metrics,
        segment_summary=segment_summary,
        clip_name=clip_name,
        out_path=out_pdf_path,
    )

    return {
        'clipName': clip_name,
        'metrics': metrics,
        'segment_summary': segment_summary,
        'scalar_summary': scalar_summary,
        'pdf_path': out_pdf_path,
    }
