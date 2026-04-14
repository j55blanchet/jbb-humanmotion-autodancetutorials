"""Analysis pipeline orchestration for motion capture data.

This module discovers landmark files (both .pose.csv and .pose2d.csv formats),
routes them to the appropriate parser, and coordinates analysis functions.

The pipeline keeps coordinates in pixel space for metric calculations. Format
conversion happens at ingestion boundary via load_pose_landmarks() based on
filename suffix:

  - .pose2d.csv -> get_pose2d_pixel_landmarks() (no scaling, canonicalize names)
  - .pose.csv   -> get_pixel_landmarks() (scale by width/height, canonicalize names)
  
Both return pixel-space DataFrames consumed directly by downstream metrics.

For detailed schema information, see landmark_processing module docstring.
"""

from pathlib import Path
from typing import Dict, Iterable, Literal, Sequence

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import pandas as pd

from . import gendered_movement_analysis
from . import pose_metrics_plotting
from . import symmetry_analysis
from .landmark_processing import get_pixel_landmarks, get_pose2d_pixel_landmarks


def detect_gender_pair_key(clip_name: str) -> tuple[str, Literal['femme', 'masc']] | None:
    """Infer pair key and role for clips that encode a femme/masc variant.

    Supported naming patterns include:
    - <base>_femme / <base>_masc
    - <base>_left_femme / <base>_right_masc (side-by-side split clips)

    Returns:
        (pair_key, role) if clip_name represents one side of a femme/masc pair,
        otherwise None.
    """
    tokens = clip_name.split('_')
    if len(tokens) < 2:
        return None

    role = tokens[-1]
    if role not in ('femme', 'masc'):
        return None

    base_tokens = tokens[:-1]
    if base_tokens and base_tokens[-1] in ('left', 'right') and 'sidebyside' in base_tokens:
        base_tokens = base_tokens[:-1]

    if not base_tokens:
        return None

    return '_'.join(base_tokens), role


def detect_complete_gender_pairs(entries: Iterable[dict]) -> dict[str, dict[str, str]]:
    """Detect complete femme/masc clip pairs from database entries.

    Returns:
        Dict[pair_key -> {'femme': clip_name, 'masc': clip_name}] for keys where
        both roles are present in the input entries.
    """
    grouped: dict[str, dict[str, str]] = {}
    for entry in entries:
        clip_name = entry.get('clipName')
        if not isinstance(clip_name, str):
            continue
        pair_info = detect_gender_pair_key(clip_name)
        if pair_info is None:
            continue

        pair_key, role = pair_info
        grouped.setdefault(pair_key, {})[role] = clip_name

    return {
        pair_key: roles
        for pair_key, roles in grouped.items()
        if 'femme' in roles and 'masc' in roles
    }


def discover_landmark_files(landmark_base_dir: Path):
    """Recursively discover all landmark files in a directory tree.

    Searches for landmark files using these scope patterns:
    - .pose.csv    (normalized web-frontend format)
    - .pose2d.csv  (pixel genderdance format)
    - .rightHand.csv, .leftHand.csv (hand-specific landmarks)
    - .face.csv (facial landmarks)

    Returns:
        Dict[clip_name → Dict[scope → Path]]
        Example: {
            'clip_001': {
                'pose': Path('.../clip_001.pose.csv'),
                'pose2d': Path('.../clip_001.pose2d.csv'),
                'rightHand': Path('.../clip_001.rightHand.csv'),
                ...
            },
            'clip_002': {...},
        }
    """
    landmark_files: Dict[str, Dict[Literal['pose', 'pose2d', 'rightHand', 'leftHand', 'face'], Path]] = {}

    def load_landmark(scope: Literal['pose', 'pose2d', 'rightHand', 'leftHand', 'face']):
        matching_files = list(landmark_base_dir.rglob(f'*.{scope}.[c][s][v]'))
        keys_values = [(p.stem.replace(f'.{scope}', ''), p) for p in matching_files]
        for key, value in keys_values:
            if key not in landmark_files:
                landmark_files[key] = {}
            landmark_files[key][scope] = value

    load_landmark('pose')
    load_landmark('pose2d')
    load_landmark('rightHand')
    load_landmark('leftHand')
    load_landmark('face')

    return landmark_files

def load_pose_landmarks(landmark_path: Path, width: int, height: int) -> pd.DataFrame:
    """Format-agnostic loader: route .pose.csv or .pose2d.csv to appropriate parser.

    This function is the ingestion boundary for pose landmark data. It detects the
    source format by filename suffix and routes to the correct parser while
    maintaining a consistent pixel-coordinate output format.

    ROUTING LOGIC:
    - If filename ends with .pose2d.csv:
      -> get_pose2d_pixel_landmarks(path)
        Converts UPPERCASE_UNDERSCORE column names to camelCase
        Drops distance/visibility columns
        Returns pixel coordinates (NO scaling, already in frame space)

    - Otherwise (assumes .pose.csv):
      -> get_pixel_landmarks(path, width, height)
        Canonicalizes lowercase camelCase names (e.g., leftShoulder_x)
        Drops visibility columns
        Returns pixel coordinates (scaled: x *= width, y *= height)

    INVARIANT: Output is always in pixel coordinate space [0, width] x [0, height]
    Downstream analysis computes metrics directly in pixel space.

    Args:
        landmark_path: Path to either .pose.csv or .pose2d.csv
        width: Video frame width (required for .pose.csv scaling)
        height: Video frame height (required for .pose.csv scaling)

    Returns:
        DataFrame with pixel coordinates, columns are <jointName>_x, <jointName>_y
    """
    if landmark_path.name.endswith('.pose2d.csv'):
        return get_pose2d_pixel_landmarks(landmark_path)
    return get_pixel_landmarks(landmark_path, width, height)


def handanalysis_output_dir(analysis_dir: Path) -> Path:
    return analysis_dir / 'handanalysis'


def analysis_output_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return handanalysis_output_dir(analysis_dir) / f'{clip_name}_handsmotion.pdf'


def symmetry_output_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return symmetry_analysis.symmetry_output_filepath(analysis_dir, clip_name)


def gendered_movement_output_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return gendered_movement_analysis.gendered_movement_output_filepath(analysis_dir, clip_name)


def gendered_movement_data_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return gendered_movement_analysis.gendered_movement_data_filepath(analysis_dir, clip_name)


def gendered_movement_ratio_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return gendered_movement_analysis.gendered_movement_ratio_filepath(analysis_dir, clip_name)


def create_analysis_figure():
    fig, axs = plt.subplots(4, 1)
    fig.set_size_inches(6.0, 8.0)
    return fig, axs


def save_analysis_figure(fig: Figure, clip_name: str, analysis_dir: Path):
    title = clip_name.replace('$', '\\$')
    fig.suptitle(f'Hands Motion Analysis: {title}')
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    handanalysis_output_dir(analysis_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(str(analysis_output_filepath(analysis_dir, clip_name)))
    plt.close(fig)


def write_clip_analysis(
    clip_name: str,
    pixel_hands: pd.DataFrame,
    fps: float,
    smooth_window: int,
    extrema_window: int,
    analysis_dir: Path,
    pose_landmarks: pd.DataFrame | None = None,
    segmentation_times: list[float] | None = None,
):
    analysis_fig, analysis_axs = create_analysis_figure()

    chart_handspd = 0
    chart_handspdcorr = 1
    chart_netspd = 2
    chart_extension = 3

    movement_metrics = pose_metrics_plotting.compute_movement_extension_metrics(
        hand_landmarks=pixel_hands,
        fps=fps,
        smooth_window=smooth_window,
        extrema_window=extrema_window,
    )

    pose_metrics_plotting.plot_movement_extension(
        metrics=movement_metrics,
        ax_spds=analysis_axs[chart_handspd],
        ax_spdcorrelation=analysis_axs[chart_handspdcorr],
        ax_movement_net=analysis_axs[chart_netspd],
        ax_extension=analysis_axs[chart_extension],
    )

    # analysis_axs[chart_handspd].set_title(clip_name)

    analysis_axs[chart_handspd].yaxis.set_visible(True)
    analysis_axs[chart_handspd].yaxis.set_ticks([])
    analysis_axs[chart_handspd].set_ylabel('Speeds')

    analysis_axs[chart_handspdcorr].yaxis.set_visible(True)
    analysis_axs[chart_handspdcorr].yaxis.set_ticks([-1, 0, 1])
    analysis_axs[chart_handspdcorr].set_ylabel('Correlation')

    analysis_axs[chart_netspd].yaxis.set_visible(True)
    analysis_axs[chart_netspd].yaxis.set_ticks([])
    analysis_axs[chart_netspd].set_ylabel('Net Speed')

    analysis_axs[chart_extension].yaxis.set_visible(True)
    analysis_axs[chart_extension].yaxis.set_ticks([])
    analysis_axs[chart_extension].set_ylabel('Extension')

    save_analysis_figure(analysis_fig, clip_name, analysis_dir)

    symmetry_analysis.write_clip_symmetry_analysis(
        clip_name=clip_name,
        pixel_hands=pixel_hands,
        fps=fps,
        smooth_window=smooth_window,
        analysis_dir=analysis_dir,
        pose_landmarks=pose_landmarks,
    )

    gendered_result = None
    if pose_landmarks is not None:
        gendered_result = gendered_movement_analysis.write_clip_gendered_movement_analysis(
            clip_name=clip_name,
            pose_landmarks=pose_landmarks,
            fps=fps,
            smooth_window=smooth_window,
            analysis_dir=analysis_dir,
            segmentation_times=segmentation_times,
        )

    return {
        'clipName': clip_name,
        'gendered_result': gendered_result,
    }
