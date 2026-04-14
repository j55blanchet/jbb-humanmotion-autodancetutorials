from pathlib import Path
import json
import sys

import matplotlib
import pandas as pd

from .landmark_processing import PoseLandmark, choose_landmarks
from . import analysis_pipeline
from . import gendered_movement_analysis


def _gender_labels_from_tags(tags: object) -> str:
    if not isinstance(tags, list):
        return ''
    labels = [tag for tag in tags if tag in ('femme', 'masc')]
    return ','.join(sorted(dict.fromkeys(labels)))


def _stringify_metadata_value(value: object) -> object:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=True)
    return value


def _build_scalar_row(motion_entry: dict, scalar_summary: dict) -> dict:
    row = {
        'clipName': motion_entry.get('clipName', ''),
        'title': motion_entry.get('title', ''),
        'clipPath': motion_entry.get('clipPath', ''),
        'thumbnailSrc': motion_entry.get('thumbnailSrc', ''),
        'audioSrc': motion_entry.get('audioSrc', ''),
        'genderLabels': _gender_labels_from_tags(motion_entry.get('tags')),
    }

    for key in (
        'frameCount',
        'fps',
        'duration',
        'width',
        'height',
        'startTime',
        'endTime',
        'poseUpperBodyOnly',
        'bpm',
        'tags',
        'landmarkScope',
    ):
        row[key] = _stringify_metadata_value(motion_entry.get(key))

    row.update(scalar_summary)
    return row


if __name__ == '__main__':
    import argparse

    matplotlib.use('pdf')

    parser = argparse.ArgumentParser()
    parser.add_argument('database_filepath', type=Path, help='Path to the database file')
    parser.add_argument('landmark_dir', type=Path, help='Path to the directory containing the landmark files')
    parser.add_argument('analysis_dir', type=Path, help='Path to the directory where generated analysis files will be saved')
    parser.add_argument('--skip-existing', '-s', dest='skip_existing', action='store_true', help='Skip songs that already have analysis output')
    args = parser.parse_args()

    analysis_dir = args.analysis_dir
    analysis_dir.mkdir(parents=True, exist_ok=True)

    landmark_files = analysis_pipeline.discover_landmark_files(args.landmark_dir)

    with open(args.database_filepath, 'r', encoding='utf-8') as db_file:
        db = json.load(db_file)
    complete_pairs = analysis_pipeline.detect_complete_gender_pairs(db)

    done = 0
    scalar_rows: list[dict] = []
    metrics_by_clip: dict[str, pd.DataFrame] = {}

    for motion_entry in db:
        clip_name = motion_entry['clipName']
        fps = motion_entry['fps']
        start_time = motion_entry['startTime']
        end_time = motion_entry['endTime']
        width = motion_entry['width']
        height = motion_entry['height']
        landmark_scope = motion_entry['landmarkScope']

        if 'pose' not in landmark_scope:
            continue

        analysis_out = analysis_pipeline.analysis_output_filepath(analysis_dir, clip_name)
        symmetry_out = analysis_pipeline.symmetry_output_filepath(analysis_dir, clip_name)
        gendered_out = analysis_pipeline.gendered_movement_output_filepath(analysis_dir, clip_name)
        if args.skip_existing and analysis_out.exists() and symmetry_out.exists() and gendered_out.exists():
            print(f'Skipping {clip_name} because analysis already exists')
            continue

        pose_landmark_path = landmark_files.get(clip_name, {}).get('pose2d') or landmark_files.get(clip_name, {}).get('pose')
        if pose_landmark_path is None:
            print(f"   Missing pose landmark file for {clip_name}", file=sys.stderr)
            continue

        done += 1
        print(f"Analyzing #{done: 2d} {clip_name}")

        extrema_window = int(fps // 3)
        smooth_window = int(fps // 3)
        if smooth_window < 3:
            smooth_window = 3
        if smooth_window % 2 == 0:
            smooth_window += 1

        pixel_landmarks = analysis_pipeline.load_pose_landmarks(pose_landmark_path, width, height)
        if len(pixel_landmarks) == 0:
            print(f"   Invalid landmark file for {clip_name} @ '{pose_landmark_path}'", file=sys.stderr)
            continue

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        clipped_pixel_landmarks = pixel_landmarks[start_frame:end_frame]

        # Extract pixel-space hands for symmetry analysis (isotropic metrics)
        pixel_shoulders = choose_landmarks(clipped_pixel_landmarks, [PoseLandmark.leftShoulder, PoseLandmark.rightShoulder])
        pixel_hands = choose_landmarks(clipped_pixel_landmarks, [PoseLandmark.leftWrist, PoseLandmark.rightWrist], relative_to=pixel_shoulders)

        clip_result = analysis_pipeline.write_clip_analysis(
            clip_name=clip_name,
            pixel_hands=pixel_hands,
            fps=fps,
            smooth_window=smooth_window,
            extrema_window=extrema_window,
            analysis_dir=analysis_dir,
            pose_landmarks=clipped_pixel_landmarks,
        )

        gendered_result = clip_result.get('gendered_result') if clip_result is not None else None
        if gendered_result is not None:
            scalar_rows.append(_build_scalar_row(motion_entry, gendered_result['scalar_summary']))
            metrics_by_clip[clip_name] = gendered_result['metrics']

    if scalar_rows:
        scalar_summary = pd.DataFrame(scalar_rows).sort_values('clipName')
        scalar_summary.to_csv(
            gendered_movement_analysis.gendered_movement_scalar_summary_filepath(analysis_dir),
            index=False,
        )

    for pair_key, pair_roles in sorted(complete_pairs.items()):
        femme_name = pair_roles['femme']
        masc_name = pair_roles['masc']
        if femme_name not in metrics_by_clip or masc_name not in metrics_by_clip:
            continue

        gendered_movement_analysis.plot_gendered_movement_comparison(
            left_metrics=metrics_by_clip[femme_name],
            right_metrics=metrics_by_clip[masc_name],
            left_clip_name=femme_name,
            right_clip_name=masc_name,
            out_path=gendered_movement_analysis.gendered_movement_comparison_filepath(analysis_dir, pair_key),
        )
