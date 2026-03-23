from pathlib import Path
from typing import Dict, Literal, Sequence

from matplotlib import pyplot as plt
import pandas as pd

from . import pose_identifier
from . import symmetry_analysis


def load_landmark_files(landmark_base_dir: Path):
    landmark_files: Dict[str, Dict[Literal['pose', 'rightHand', 'leftHand', 'face'], Path]] = {}

    def load_landmark(scope: str):
        matching_files = list(landmark_base_dir.rglob(f'*.{scope}.[c][s][v]'))
        keys_values = [(p.stem.replace(f'.{scope}', ''), p) for p in matching_files]
        for key, value in keys_values:
            if key not in landmark_files:
                landmark_files[key] = {}
            landmark_files[key][scope] = value

    load_landmark('pose')
    load_landmark('rightHand')
    load_landmark('leftHand')
    load_landmark('face')

    return landmark_files


def analysis_output_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return analysis_dir / f'handanalysis_{clip_name}.pdf'


def symmetry_output_filepath(analysis_dir: Path, clip_name: str) -> Path:
    return symmetry_analysis.symmetry_output_filepath(analysis_dir, clip_name)


def create_analysis_figure():
    fig, axs = plt.subplots(4, 1)
    fig.set_size_inches(6.0, 8.0)
    return fig, axs


def save_analysis_figure(fig: plt.Figure, clip_name: str, analysis_dir: Path):
    title = clip_name.replace('$', '\\$')
    fig.suptitle(f'Hands Motion Analysis: {title}')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(str(analysis_output_filepath(analysis_dir, clip_name)))
    plt.close(fig)


def write_clip_analysis(
    clip_name: str,
    hands: pd.DataFrame,
    fps: float,
    smooth_window: int,
    extrema_window: int,
    analysis_dir: Path,
    pose_landmarks: pd.DataFrame | None = None,
):
    analysis_fig, analysis_axs = create_analysis_figure()

    chart_handspd = 0
    chart_handspdcorr = 1
    chart_netspd = 2
    chart_extension = 3

    pose_identifier.plot_movement_extension(
        hands,
        fps,
        smooth_window=smooth_window,
        extrema_window=extrema_window,
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
        hands=hands,
        fps=fps,
        smooth_window=smooth_window,
        analysis_dir=analysis_dir,
        pose_landmarks=pose_landmarks,
    )
