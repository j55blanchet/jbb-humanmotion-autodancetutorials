import sys
from pathlib import Path
import json

from ..datatypes import IMR
from .video_manipulation import make_trimmed_video

if __name__ == "__main__":
    database_file = Path(sys.argv[1])
    video_dir = Path(sys.argv[2])
    imr_dir = Path(sys.argv[3])
    clip_out_dir = Path(sys.argv[4])

    clip_out_dir.mkdir(exist_ok=True, parents=True)

    imr_files = list(imr_dir.rglob('*.[i][m][r].[j][s][o][n]'))
    out_clip_files = [
        clip_out_dir.joinpath(
            imr_path.relative_to(imr_dir).parent,
            imr_path.stem.replace('.imr', '') + '.mp4'
        )
        for imr_path in imr_files
    ]

    for imr_filepath, out_clipath in imr_files:
        pass