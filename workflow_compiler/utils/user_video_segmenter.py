from .workflow_condition_names import workflow_condition_names

# Nov 2021 User Study
segmentations = {
    # 00388bd7-d313-4ce1-89e5-c88091f25357 pajama-party-tutorial-blurred
    '00388bd7-d313-4ce1-89e5-c88091f25357': [0.0, 2.682, 5.365, 8.048, 10.731, 13.913],

    # 0079b262-7575-4ae7-a377-60e21070106e last-christmas-tutorial
    '0079b262-7575-4ae7-a377-60e21070106e': [0.0, 4.352, 8.704, 13.056, 15.066],

    # 02883b27-c152-4415-ae7a-1cb4c5f086e5 last-christmas-blurred
    '02883b27-c152-4415-ae7a-1cb4c5f086e5': [0.0, 4.352, 8.704, 13.056, 15.066],

    # 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3 pajama-party-tutorial-blurred
    '102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3': [0.0, 2.682, 5.365, 8.048, 10.731, 13.913],

    # 44e54afd-19c0-4342-b753-fb4ab123aaad mad-at-disney-tutorial-blurred
    '44e54afd-19c0-4342-b753-fb4ab123aaad': [0.0, 4.04, 8.08, 12.12, 16.16, 18.15],

    # 917fe4e1-9590-44eb-a541-1cef13e4f1ea pajamaparty-tutorial
    '917fe4e1-9590-44eb-a541-1cef13e4f1ea': [0.0, 2.682, 5.365, 8.048, 10.731, 13.913],

    # d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4 mad-at-disney-tutorial-blurred
    'd6ad5749-50d4-4cc7-99b5-6b9ddecebbf4': [0.0, 4.04, 8.08, 12.12, 16.16, 18.15],

    # e525302b-2740-4e73-aa37-170bd8ceb8d1 mad-at-disney-tutorial
    'e525302b-2740-4e73-aa37-170bd8ceb8d1': [0.0, 4.04, 8.08, 12.12, 16.16, 18.15],

    # ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e last-christmas-blurred
    'ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e': [0.0, 4.352, 8.704, 13.056, 15.066],
}

# May 2022 User Study
segmentations_by_name = {
    'bartender': [0.0, 4.498, 8.997, 13.496, 17.995, 18.866],# [0.0, 5.5, 8.316, 10.85, 13.0, 14.9],
    'last-christmas': [0.0, 4.352, 8.704, 13.056, 15.066], #[0.0, 3.643, 4.3521, 6.731, 8.704, 10.541, 11.3, 13.056, 15.067],
    'mad-at-disney': [0.0, 4.04, 8.08, 12.12, 16.16, 18.15], # [0.0, 1.5, 2.13, 4.04, 6.34, 8.08, 10.20, 12.12, 14.14, 16, 18.15],
    'pajamaparty-tutorial': [0.0, 2.682, 5.365, 8.048, 10.731, 13.913], #[0, 2.68, 5.368, 6.713, 8.052, 10.736, 12.5, 13.42, 13.96]
}

segmentations.update({
    '863816e2-19eb-4459-9531-dd84ffaa2e03': segmentations_by_name['bartender'],
    '4a58e38b-adce-42d8-bfbc-997d40084308': segmentations_by_name['bartender'],
    'c096aef4-3cd9-415d-9ca1-f8709a7f770a': segmentations_by_name['bartender'],
    'd114fd87-11bb-4da5-a7c5-f17c55540a8f': segmentations_by_name['bartender'],

    'e1d510c2-5bc5-4b00-9e97-f82139c7be35': segmentations_by_name['last-christmas'],
    '9047689f-b735-4e52-811b-7782ab08931d': segmentations_by_name['last-christmas'],
    '0e6c3e35-4ba3-4e76-8c4e-dd7e1c42e3df': segmentations_by_name['last-christmas'],
    '6d42a03e-8de1-4daf-81c3-7bd7ea3e071c': segmentations_by_name['last-christmas'],

    '0b78f385-a6be-41d7-8898-57f075f777ab': segmentations_by_name['pajamaparty-tutorial'],
    '5e5d43f1-4914-40bf-bf51-bd6f1d9c2013': segmentations_by_name['pajamaparty-tutorial'],
    '786b141b-3b92-48a0-925f-602e5ac8c454': segmentations_by_name['pajamaparty-tutorial'],
    'c489d783-4f40-464d-87ed-e86fdacadece': segmentations_by_name['pajamaparty-tutorial'],

    'f77787d8-9af4-4358-98e0-4cf00813438e': segmentations_by_name['mad-at-disney'],
    '0cb498c3-8cdb-4bd3-80c8-d61f38b0d833': segmentations_by_name['mad-at-disney'],
    '9cf99b96-0a03-4f76-ad94-666b4701e02b': segmentations_by_name['mad-at-disney'],
    '568e88b5-0a90-4755-bef4-3132efd7ffa1': segmentations_by_name['mad-at-disney'],
})

import argparse
from pathlib import Path
import pathlib
import sys, os

from .video_manipulation import make_trimmed_video
# import signal
# import librosa
# import numpy as np


def is_float(element) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False


def parse_videofile_name_userstudy1(filename: str):  
    workflow_id = filename[:36]
    user_id = filename[37:41]
    remaining_filename = filename[42:]

    id_start = remaining_filename.index(workflow_id)
    clipname = remaining_filename[:id_start-1]

    suffix_info = remaining_filename[id_start + 1 + len(workflow_id):]

    speed = 1.0
    return workflow_id, user_id, clipname, suffix_info, speed


def parse_videofile_name_userstudy2(filename: str):
    #userPARTICIPANTID4163-uploadvidUpload--clip=bartender-workflow=d114fd87-11bb-4da5-a7c5-f17c55540a8f-spd=50-workflowd114fd87-11bb-4da5-a7c5-f17c55540a8f.webm
    user_index = filename.find('user')
    user_id = filename[user_index + 4:filename.find('-', user_index)]
    user_id = user_id.replace("PARTICIPANTID", "")
    user_id = 'useridmissing' if user_id == '' else user_id

    upload_index = filename.find('upload')
    uploadType = filename[upload_index + 6: filename.find("-", upload_index)]

    clip_index = filename.find('clip=')
    workflow_index = filename.find('workflow=')
    spd_index = filename.find("spd=")
    clip_name = filename[clip_index + 5: workflow_index - 1]
    workflow_id = filename[workflow_index + 9: spd_index - 1]
    spd = filename[spd_index + 4: filename.find('-', spd_index)]
    if is_float(spd):
        spd = (float(spd) / 100)
    else:
        spd = 1.0
    return workflow_id, user_id, clip_name, '', spd #f"spd={spd}-type={uploadType}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest-folder', type=str, required=True)
    parser.add_argument('--study', type=int, required=False, default=1),
    parser.add_argument('--normalize_1x_speed', default=False, action="store_true")
    parser.add_argument('input_files', nargs="*", metavar='video inputs', type=str, help='User Video Clips to generate segmentated clips for')
    args = parser.parse_args()

    dest_folder = Path(args.dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    segmentations_by_name_keys = list(segmentations_by_name.keys())

    if len(args.input_files) == 1:
        path = pathlib.Path(args.input_files[0])
        files = list(path.parent.glob(path.name))
        args.input_files = files

    parse_videofile = parse_videofile_name_userstudy1 if args.study == 1 else parse_videofile_name_userstudy2

    for i, video_filepath_str in enumerate(args.input_files):
        video_filepath = Path(video_filepath_str)
        print(f"Processing {i+1}/{len(args.input_files)}...")
        print(f"    {video_filepath.name=}")
        print(f"    ", end='')
        try:
            workflow_id, user_id, clip_name, suffix_info, vidspd = parse_videofile(video_filepath.stem)
        
            segmentation = segmentations.get(workflow_id)
            workflow_condition = workflow_condition_names.get(workflow_id)

            if segmentation is None:
                print('Error!')
                print(f'No segmentation found for id={workflow_id} at {video_filepath}', file=sys.stderr)
                continue
            if workflow_condition is None:
                print('Error!')
                print(f'No workflow condition name found for id={workflow_id} at {video_filepath}', file=sys.stderr)
                continue
            
            segments = len(segmentation) - 1
            print(f'{user_id=}, {workflow_condition=}, {segments=}')
            segment_start_ends = list(enumerate(zip(segmentation[:-1], segmentation[1:])))
            for j, (start, end) in segment_start_ends:
                if not args.normalize_1x_speed:
                    start = start / vidspd
                    end = end / vidspd
                clip_path = dest_folder / f'user{user_id}____{suffix_info.replace(".", "-")}____{workflow_condition}____workflowid-{workflow_id}____clip{j+1}.mp4'
                print(f'    ({j+1}/{segments}) [{start}s, {end}s]', end='') # ==> {clip_path.name}')
                if clip_path.exists():
                    print('Cached')
                    continue
                else:
                    print()
                clip_path.unlink(missing_ok=True)
                speed_up_factor = 1.0 if not args.normalize_1x_speed else (1 / vidspd)
                make_trimmed_video(
                    video_filepath,
                    clip_path,
                    start,
                    end,
                    speedUpFactor=speed_up_factor,
                    copyEncoding=False
                )
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()

if __name__ == "__main__":
    main()