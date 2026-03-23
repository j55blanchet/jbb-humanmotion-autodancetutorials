from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from . import pose_identifier


def symmetry_output_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return analysis_dir / f'handanalysis_symmetry_{clip_name}.pdf'


def _safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    valid = np.isfinite(a) & np.isfinite(b)
    a = a[valid]
    b = b[valid]
    if len(a) < 2 or len(b) < 2:
        return np.nan
    if np.nanstd(a) == 0 or np.nanstd(b) == 0:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


def _rolling_corr(left: np.ndarray, right: np.ndarray, window: int) -> np.ndarray:
    n = len(left)
    out = np.full(n, np.nan, dtype=float)
    half = max(1, window // 2)
    for i in range(n):
        a = max(0, i - half)
        b = min(n, i + half + 1)
        out[i] = _safe_corr(left[a:b], right[a:b])
    return out


def _lag_aware_corr(left: np.ndarray, right: np.ndarray, window: int, max_lag: int) -> np.ndarray:
    n = len(left)
    out = np.full(n, np.nan, dtype=float)
    half = max(1, window // 2)
    max_lag = max(0, int(max_lag))

    for i in range(n):
        best_corr = np.nan
        a = max(0, i - half)
        b = min(n, i + half + 1)

        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                l = left[a:b + lag]
                r = right[a - lag:b]
            elif lag > 0:
                l = left[a + lag:b]
                r = right[a:b - lag]
            else:
                l = left[a:b]
                r = right[a:b]

            corr = _safe_corr(l, r)
            if np.isnan(corr):
                continue
            if np.isnan(best_corr) or corr > best_corr:
                best_corr = corr

        out[i] = best_corr

    return out


def _extract_xy(df: pd.DataFrame, prefix: str) -> tuple[np.ndarray, np.ndarray] | tuple[None, None]:
    x_col = f'{prefix}_x'
    y_col = f'{prefix}_y'
    if x_col not in df.columns or y_col not in df.columns:
        return None, None
    return df[x_col].to_numpy(dtype=float), df[y_col].to_numpy(dtype=float)


def _angle_from_xy(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.arctan2(y, x)


def _wrapped_angle_diff(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.arctan2(np.sin(a - b), np.cos(a - b))


def _compute_elbow_angle(shoulder_xy: tuple[np.ndarray, np.ndarray], elbow_xy: tuple[np.ndarray, np.ndarray], wrist_xy: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    sx, sy = shoulder_xy
    ex, ey = elbow_xy
    wx, wy = wrist_xy

    upper_x = sx - ex
    upper_y = sy - ey
    lower_x = wx - ex
    lower_y = wy - ey

    upper_norm = np.hypot(upper_x, upper_y)
    lower_norm = np.hypot(lower_x, lower_y)
    denom = (upper_norm * lower_norm) + 1e-6
    dot = (upper_x * lower_x) + (upper_y * lower_y)
    cos_theta = np.clip(dot / denom, -1.0, 1.0)
    return np.arccos(cos_theta)


def compute_symmetry_metrics(hands: pd.DataFrame, fps: float, smooth_window: int, pose_landmarks: pd.DataFrame | None = None) -> pd.DataFrame:
    eps = 1e-6

    spds = pose_identifier.get_spds(hands, smooth_window=smooth_window)
    if len(spds.columns) < 2:
        raise ValueError('Expected at least two hand speed columns for symmetry metrics.')

    left_speed = spds.iloc[:, 0].to_numpy(dtype=float)
    right_speed = spds.iloc[:, 1].to_numpy(dtype=float)

    ext = pose_identifier.get_individual_extensions(hands, smooth_window=smooth_window)
    left_ext = ext.iloc[:, 0].to_numpy(dtype=float)
    right_ext = ext.iloc[:, 1].to_numpy(dtype=float)

    total_speed = left_speed + right_speed
    coactivation = (2.0 * np.minimum(left_speed, right_speed)) / (total_speed + eps)
    dominance_signed = (right_speed - left_speed) / (total_speed + eps)

    ext_total = left_ext + right_ext
    extension_similarity = 1.0 - (np.abs(left_ext - right_ext) / (ext_total + eps))

    # Geometric congruence: mirror left-arm angle to compare against right-arm angle.
    left_angle = _angle_from_xy(
        hands.iloc[:, 0].to_numpy(dtype=float),
        hands.iloc[:, 1].to_numpy(dtype=float),
    )
    right_angle = _angle_from_xy(
        hands.iloc[:, 2].to_numpy(dtype=float),
        hands.iloc[:, 3].to_numpy(dtype=float),
    )
    left_mirrored_angle = _angle_from_xy(
        -hands.iloc[:, 0].to_numpy(dtype=float),
        hands.iloc[:, 1].to_numpy(dtype=float),
    )
    angle_diff = np.abs(_wrapped_angle_diff(left_mirrored_angle, right_angle))
    angle_congruence = 1.0 - (angle_diff / np.pi)

    elbow_angle_similarity = np.full(len(hands), np.nan, dtype=float)
    if pose_landmarks is not None:
        l_sh = _extract_xy(pose_landmarks, 'leftShoulder')
        l_el = _extract_xy(pose_landmarks, 'leftElbow')
        l_wr = _extract_xy(pose_landmarks, 'leftWrist')
        r_sh = _extract_xy(pose_landmarks, 'rightShoulder')
        r_el = _extract_xy(pose_landmarks, 'rightElbow')
        r_wr = _extract_xy(pose_landmarks, 'rightWrist')

        if all(x is not None for x in (l_sh[0], l_el[0], l_wr[0], r_sh[0], r_el[0], r_wr[0])):
            left_elbow = _compute_elbow_angle(l_sh, l_el, l_wr)
            right_elbow = _compute_elbow_angle(r_sh, r_el, r_wr)
            elbow_angle_similarity = 1.0 - (np.abs(left_elbow - right_elbow) / np.pi)

    rolling_window = max(9, int(round(fps * 0.75)))
    if rolling_window % 2 == 0:
        rolling_window += 1
    max_lag = max(1, int(round(fps * 0.35)))

    corr_local = _rolling_corr(left_speed, right_speed, rolling_window)
    corr_lag_aware = _lag_aware_corr(left_speed, right_speed, rolling_window, max_lag)

    times = pose_identifier.get_times(hands, fps).iloc[:, 0].to_numpy(dtype=float)

    return pd.DataFrame(
        {
            'time': times,
            'left_speed': left_speed,
            'right_speed': right_speed,
            'corr_local': corr_local,
            'corr_lag_aware': corr_lag_aware,
            'coactivation': coactivation,
            'extension_similarity': extension_similarity,
            'angle_congruence': angle_congruence,
            'left_arm_angle': left_angle,
            'right_arm_angle': right_angle,
            'elbow_angle_similarity': elbow_angle_similarity,
            'dominance_signed': dominance_signed,
        }
    )


def plot_symmetry_metrics(metrics: pd.DataFrame, clip_name: str, out_path: Path):
    t = metrics['time']

    fig, axs = plt.subplots(4, 1)
    fig.set_size_inches(6.0, 8.0)

    axs[0].plot(t, metrics['left_speed'], label='Left Speed', alpha=0.9)
    axs[0].plot(t, metrics['right_speed'], label='Right Speed', alpha=0.9)
    axs[0].set_ylabel('Speed')
    axs[0].legend(loc='upper right', fontsize='x-small')
    axs[0].xaxis.set_visible(False)

    axs[1].plot(t, metrics['corr_local'], label='Local Corr', alpha=0.85)
    axs[1].plot(t, metrics['corr_lag_aware'], label='Lag-Aware Corr', alpha=0.85)
    axs[1].set_ylim(-1, 1)
    axs[1].set_yticks([-1, 0, 1])
    axs[1].set_ylabel('Correlation')
    axs[1].legend(loc='upper right', fontsize='x-small')
    axs[1].xaxis.set_visible(False)

    axs[2].plot(t, metrics['coactivation'], label='Coactivation', alpha=0.85)
    axs[2].plot(t, metrics['extension_similarity'], label='Extension Similarity', alpha=0.85)
    axs[2].plot(t, metrics['angle_congruence'], label='Mirror-Angle Congruence', alpha=0.85)
    if metrics['elbow_angle_similarity'].notna().any():
        axs[2].plot(t, metrics['elbow_angle_similarity'], label='Elbow-Angle Similarity', alpha=0.85)
    axs[2].set_ylim(0, 1)
    axs[2].set_yticks([0, 0.5, 1])
    axs[2].set_ylabel('Similarity')
    axs[2].legend(loc='upper right', fontsize='x-small')
    axs[2].xaxis.set_visible(False)

    axs[3].plot(t, metrics['dominance_signed'], label='Dominance (R-L)/(R+L)', alpha=0.9)
    axs[3].set_ylim(-1, 1)
    axs[3].set_yticks([-1, 0, 1])
    axs[3].set_ylabel('Dominance')
    axs[3].set_xlabel('Time')
    axs[3].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:0.2f}s'))

    title = clip_name.replace('$', '\\$')
    fig.suptitle(f'Hand Symmetry Analysis: {title}')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(str(out_path))
    plt.close(fig)


def write_clip_symmetry_analysis(
    clip_name: str,
    hands: pd.DataFrame,
    fps: float,
    smooth_window: int,
    analysis_dir: Path,
    pose_landmarks: pd.DataFrame | None = None,
):
    metrics = compute_symmetry_metrics(hands, fps=fps, smooth_window=smooth_window, pose_landmarks=pose_landmarks)
    out_path = symmetry_output_filepath(analysis_dir, clip_name)
    plot_symmetry_metrics(metrics, clip_name=clip_name, out_path=out_path)
