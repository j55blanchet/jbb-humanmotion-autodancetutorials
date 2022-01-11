from .mp_processing import process_video
from typing import *
import os
from pathlib import Path

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def load_landmark_files(landmark_base_dir: os.PathLike):
    landmark_files: Dict[str, Dict[Literal['pose', 'rightHand', 'leftHand', 'face'], Path]] = {}

    def load_landmark(scope: str):
        print(f"Finding {scope} files")
        matching_files = list(Path(landmark_base_dir).rglob(f'*.{scope}.[c][s][v]'))
        keys_values = [
            (p.stem.replace(f'.{scope}', ''), p) for p in matching_files
        ]
        for key, value in keys_values:
            print(f"   FOUND {scope} file: {key}: {value}")
            if not key in landmark_files:
                landmark_files[key] = {}
            landmark_files[key][scope] = value
    
    load_landmark('pose')
    load_landmark('rightHand')
    load_landmark('leftHand')
    load_landmark('face')
    
    return landmark_files

def process_landmarks(clip_name: str, frame_count: int, video_path: Path, clip_relative_dir: Path, landmarkScope: List[str], landmark_outdir: Path, landmark_files: Dict[str, Dict[Literal['pose', 'rightHand', 'leftHand', 'face'], Path]]):
    pose_outpath = landmark_outdir.joinpath(clip_relative_dir, clip_name + '.pose.csv')
    left_outpath = landmark_outdir.joinpath(clip_relative_dir, clip_name + '.leftHand.csv')
    right_outpath = landmark_outdir.joinpath(clip_relative_dir, clip_name + '.rightHand.csv')
    face_outpath = landmark_outdir.joinpath(clip_relative_dir, clip_name + '.face.csv')

    scopes = set(landmarkScope)

    pose_outpath = pose_outpath   if 'pose' in scopes else None
    left_outpath = left_outpath   if 'leftHand' in scopes else None
    right_outpath = right_outpath if 'rightHand' in scopes else None
    face_outpath = face_outpath   if 'face' in scopes else None

    needs_processing = False
    for path in [pose_outpath, left_outpath, right_outpath, face_outpath]:
        if path is not None and not path.exists():
            needs_processing = True
            break

    if needs_processing:
        print(f'\tProcessing landmarks for {clip_name}: {landmarkScope}')
        process_video(
            video_path.as_posix(),
            frame_count,
            pose_outpath,
            left_outpath,
            right_outpath,
            face_outpath
        )
    else:
        print(f'\tLandmarks already exist for {clip_name} {video_path}')

    landmarks = {
        'pose': pose_outpath,
        'leftHand': left_outpath,
        'rightHand': right_outpath,
        'face': face_outpath
    }

    return dict([
        (k, v) for k, v in landmarks.items() if v is not None
    ])

VIDEO_FILE_EXTENSIONS = [
    'mp4',
    'm4v',
    'mov'
]

USAGE_INSTRUCTIONS = """
Calculates and saves Intermediate Motion Representations (IMRs) from video files. Optionally
processes the landmarks in the videos.

Usage:
    python batch_generation.py <database.json> <process_landmarks> <video_directory> <landmark_directory> <imr_output_directory>

- <database.json>: The json file containing info about the motions that are to be processed.
- <video_directory>: Base directory for all video files
- <landmark_directory>: Base directory for all landmark .csv files
"""


if __name__ == "__main__":

    import sys
    import json

    # Process command line arguments
    database_path = Path(sys.argv[1])
    video_directory = Path(sys.argv[2])
    landmark_directory = Path(sys.argv[3])

    assert database_path.exists() and database_path.is_file()
    assert video_directory.exists() and video_directory.is_dir()
    landmark_directory.mkdir(parents=True, exist_ok=True)

    video_files = []

    for file_extension in VIDEO_FILE_EXTENSIONS:
        video_files.extend(video_directory.rglob(f'*.{file_extension}'))

    # Load existing landmark files
    landmark_files = load_landmark_files(landmark_directory)

    # Load database.json
    db = []
    with open(database_path, 'r', encoding='utf-8') as db_file:
        db = json.load(db_file)

    # Create the IMRs
for i, motion_entry in enumerate(db):
    clipName = motion_entry['clipName']
    clipPath = Path(motion_entry['clipPath'])
    frameCount = motion_entry['frameCount']
    fps = motion_entry['fps']
    duration = motion_entry['duration']
    width = motion_entry['width']
    height = motion_entry['height']
    startTime = motion_entry['startTime']
    endTime = motion_entry['endTime']
    poseUpperBodyOnly = motion_entry['poseUpperBodyOnly']
    landmarkScope = motion_entry['landmarkScope']

    relative_dir = clipPath.parent
    full_vid_path = video_directory.joinpath(clipPath)

    print(f'{i+1}/{len(db)} Creating landmarks for {clipName} @ {clipPath}')
    landmark_files[clipName] = process_landmarks(clipName, frameCount, full_vid_path, relative_dir, landmarkScope, landmark_directory, landmark_files)