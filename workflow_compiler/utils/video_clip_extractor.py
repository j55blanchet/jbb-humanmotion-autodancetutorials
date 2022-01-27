import sys
from pathlib import Path
import json

from ..datatypes import IMR, VideoDatabase
from .video_manipulation import make_trimmed_video

if __name__ == "__main__":
    # database_file = Path(sys.argv[1])
    video_dir = Path(sys.argv[2])
    imr_dir = Path(sys.argv[3])
    clip_out_dir = Path(sys.argv[4])

    clip_out_dir.mkdir(exist_ok=True, parents=True)

    # vid_db = VideoDatabase(database_file)

    imr_files = list(imr_dir.rglob('*.[i][m][r].[j][s][o][n]'))
    out_clip_files = [
        clip_out_dir.joinpath(
            imr_path.relative_to(imr_dir).parent,
            imr_path.stem.replace('.imr', '') + '.mp4'
        )
        for imr_path in imr_files
    ]

    for imr_i, (imr_filepath, out_clippath) in enumerate(zip(imr_files, out_clip_files)):

        imr = None
        with open(imr_filepath, "r", encoding='utf-8') as imrfile:
            imr = IMR.IMR.from_json(json.load(imrfile))

        vid_filepath = video_dir.joinpath(imr.clipPath)
        print(f"{imr_i+1}/{len(imr_files)} - Extracting clips for {str(imr_filepath.relative_to(imr_dir))} [{imr.clipName}] ({len(imr.temporalSegments)} clips)")

        for i, seg in enumerate(imr.temporalSegments):
            out_segment_clippath = out_clippath.parent / Path(out_clippath.stem + f'.clip-{i+1}' + out_clippath.suffix)
            print(f"\tClip {i+1}: {seg.startTime:.2f}s -> {seg.endTime:.2f}s  ==> {str(out_segment_clippath)}")
            make_trimmed_video(vid_filepath, out_segment_clippath, seg.startTime, seg.endTime)