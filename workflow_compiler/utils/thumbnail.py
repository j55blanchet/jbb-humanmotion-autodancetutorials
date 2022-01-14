from pathlib import Path
from typing import Iterable, Sequence
import cv2



def get_thumbnails(video_path: Path, frames: Iterable[int]):
    cap = cv2.VideoCapture(str(video_path))
    for frame_i in frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_i)
        success, image = cap.read()
        if not success:
            raise Exception(f'Frame {frame_i} not readable')
        yield image
    
    pass
def create_thumbnails(video_path: Path, thumbnail_path: Path, frames: Sequence[int]):
    cap = cv2.VideoCapture(str(video_path))
    
    assert thumbnail_path.is_dir() or not thumbnail_path.exists()
    thumbnail_path.mkdir(exist_ok=True, parents=True)

    for frame_i in frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_i)
        success, image = cap.read()
        if success:
            cv2.imwrite(str(thumbnail_path / f'{frame_i}.jpg'), image)
    
    