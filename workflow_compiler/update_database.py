from os import PathLike
from pathlib import Path

import json
import sys
import cv2
from typing import Dict, List

from numpy.core.fromnumeric import trace
from .utils.video_manipulation import extract_audio

valid_file_endings = [
    'mp4',
    'm4v',
    'mov',
    
]

USAGE_INSTRUCTIONS = """
    This program updates the database.json file with videos 
    detected in the video directory.

    Usage:
        python update_database.py path/to/database.json path/containing/videos path/for/audio
"""

def update_create_entry(entry: Dict, video_path: Path, clip_name: str, clip_path: PathLike):
    if entry is None:
        entry = {}

    out_entry = {}

    out_entry['title'] = entry.get('title', clip_name)
    out_entry['clipName'] = clip_name
    out_entry['clipPath'] = Path(clip_path).as_posix()

    vid_data = cv2.VideoCapture(video_path.as_posix())
    frame_count = vid_data.get(cv2.CAP_PROP_FRAME_COUNT)
    out_entry['frameCount'] = int(frame_count)
    fps = vid_data.get(cv2.CAP_PROP_FPS)
    out_entry['fps'] = fps
    duration = frame_count / fps
    out_entry['duration'] = duration
    out_entry['width'] = int(vid_data.get(cv2.CAP_PROP_FRAME_WIDTH))
    out_entry['height'] = int(vid_data.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out_entry['startTime'] = entry.get('startTime', 0)
    out_entry['endTime'] = entry.get('endTime', duration)

    out_entry['poseUpperBodyOnly'] = entry.get('poseUpperBodyOnly', False)
    out_entry['tags'] = entry.get('tags', [])
    out_entry['landmarkScope'] =     entry.get('landmarkScope', [
        'pose',
        'rightHand',
        'leftHand',
        'face'
    ])
    vid_data.release()

    return out_entry

def create_thumbnail(video_path: Path, relative_path: Path, timestamp: float, thumbnails_dir: Path):
    thumbnail_path = relative_path.parent.joinpath(relative_path.stem + '.jpg')
    thumbnail_path = thumbnails_dir.joinpath(thumbnail_path)
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    thumbnail_frame = int(fps * timestamp)
    success, image = cap.read()
    frame_i = 0
    while success and frame_i < thumbnail_frame:
        success, image = cap.read()
        frame_i += 1
    
    if success and frame_i == thumbnail_frame:
        thumbnail_path.parent.mkdir(exist_ok=True, parents=True)
        saved_successfully = cv2.imwrite(str(thumbnail_path), image)
        if not saved_successfully: 
            raise Exception(f'Unabled to save thumbnail {str(thumbnail_path)}')
    else:
        raise Exception(f'Unable to create thumbnail for {relative_path}. (got to frame {frame_i}, wanted to get thumbnail at frame {thumbnail_frame}, for timestamp {timestamp})')
    
    return thumbnail_path

def update_database(database_path: PathLike, videos_dir: PathLike, thumbnails_dir: PathLike, audio_path: PathLike):
    videos_dir = Path(videos_dir)
    database_path = Path(database_path)
    thumbnails_dir = Path(thumbnails_dir)
    audio_dir = Path(audio_path)
    audio_dir.mkdir(exist_ok=True, parents=True)
    thumbnails_dir.mkdir(exist_ok=True, parents=True)

    video_paths: List[Path] = []
    for file_ending in valid_file_endings:
        video_paths.extend(videos_dir.rglob(f'*.{file_ending}'))    

    db = []
    if database_path.exists():
        with open(database_path, 'r', encoding='utf-8') as db_file:
            db = json.load(db_file)
    else:
        database_path.parent.mkdir(parents=True, exist_ok=True)

    out_db = {}
    for entry in db:
        out_db[entry['clipName']] = entry
    
    for video_path in video_paths:
        
        relative_path = video_path.relative_to(videos_dir)
        print(f'Processing {relative_path.as_posix()}')
        clip_name = relative_path.stem

        prev_entry = out_db.get(clip_name)
        entry = update_create_entry(
            entry = prev_entry, 
            video_path = video_path, 
            clip_name = clip_name, 
            clip_path = relative_path
        )
        start_time: float = entry['startTime']
        thumbnail_path = create_thumbnail(videos_dir.joinpath(relative_path), relative_path, start_time, thumbnails_dir)
        entry['thumbnailSrc'] = thumbnail_path.relative_to(thumbnails_dir).as_posix()

        audio_path = extract_audio(videos_dir.joinpath(relative_path), relative_path, audio_dir)
        if audio_path is not None:
            entry['audioSrc'] = audio_path.relative_to(audio_dir).as_posix()
        out_db[clip_name] = entry
    
    new_db = list(out_db.values())
    with open(database_path, 'w', encoding='utf-8') as db_file:
        json.dump(new_db, db_file, indent=2)


    
if __name__ == "__main__":
    try:
        update_database(
            database_path = sys.argv[1],
            videos_dir = sys.argv[2],
            thumbnails_dir = sys.argv[3],
            audio_path= sys.argv[4],
        )
    except Exception as e:
        import traceback
        print('Error while updating the database:')
        traceback.print_exc(file=sys.stderr)

        print(USAGE_INSTRUCTIONS)
        
    