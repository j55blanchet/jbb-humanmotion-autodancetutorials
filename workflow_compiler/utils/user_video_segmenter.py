
# %%

workflow_condition_names = {
    '00388bd7-d313-4ce1-89e5-c88091f25357': 'userstudy1--pajama-party--sheetmotion',
    '0079b262-7575-4ae7-a377-60e21070106e': 'userstudy1--last-christmas--control',
    '02883b27-c152-4415-ae7a-1cb4c5f086e5': 'userstudy1--last-christmas--skeleton',
    '102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3': 'userstudy1--pajama-party--skeleton',
    '44e54afd-19c0-4342-b753-fb4ab123aaad': 'userstudy1--mad-at-disney--skeleton',
    '917fe4e1-9590-44eb-a541-1cef13e4f1ea': 'userstudy1--pajamaparty--control',
    'd6ad5749-50d4-4cc7-99b5-6b9ddecebbf4': 'userstudy1--mad-at-disney--sheetmotion',
    'e525302b-2740-4e73-aa37-170bd8ceb8d1': 'userstudy1--mad-at-disney--control',
    'ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e': 'userstudy1--last-christmas--sheetmotion',
}
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

import argparse
from pathlib import Path
import sys, os

from .video_manipulation import make_trimmed_video
# import signal
# import librosa
# import numpy as np

def parse_videofile_name_userstudy1(filename: str):  
    workflow_id = filename[:36]
    user_id = filename[37:41]
    clip_name = filename[42:-55]
    return workflow_id, user_id, clip_name

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest-folder', type=str, required=True)
    parser.add_argument('input_files', nargs="*", metavar='video inputs', type=str, help='User Vide Clips to generate segmentated clips for')
    args = parser.parse_args()

    dest_folder = Path(args.dest_folder)

    for i, video_filepath_str in enumerate(args.input_files):
        video_filepath = Path(video_filepath_str)
        workflow_id, user_id, clip_name = parse_videofile_name_userstudy1(video_filepath.stem)
        segmentation = segmentations.get(workflow_id)
        workflow_condition = workflow_condition_names.get(workflow_id)

        print(f"Processing {i+1}/{len(args.input_files)}...", end='')

        if segmentation is None:
            print('Error!')
            print(f'No segmentation found for id={workflow_id} at {video_filepath}', file=sys.stderr)
            continue
        if workflow_condition is None:
            print('Error!')
            print(f'No workflow condition name found for id={workflow_id} at {video_filepath}', file=sys.stderr)
            continue
        
        segments = len(segmentation)
        print(f'{user_id=}, {workflow_condition=}, {segments=}')
        for j, (start, end) in enumerate(zip(segmentation[:-1], segmentation[1:])):
            clip_path = dest_folder / f'user{user_id}_condition-{workflow_condition}_workflowid-{workflow_id}_clip{j+1}.mp4'
            print(f'    ({j+1}) ==> {clip_path}')
            make_trimmed_video(
                video_filepath,
                clip_path,
                start,
                end,
            )






# # %%

# ls_output = """
# 00388bd7-d313-4ce1-89e5-c88091f25357-4324-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5334-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5334-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5334-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5351-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5351-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5351-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5357-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5357-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5357-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5375-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5375-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5375-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5376-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5376-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5376-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5406-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5406-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5406-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5414-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5414-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5414-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5419-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5419-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5419-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5424-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5424-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5424-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5434-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5434-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5434-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5443-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5443-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5443-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5448-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5448-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5448-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5452-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5452-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5452-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5532-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5532-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5532-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5549-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5562-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5562-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5562-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5630-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5630-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5630-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5647-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5647-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5647-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5651-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5651-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5651-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5653-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5653-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-5653-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-9999-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-0.5.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-9999-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-initial-1.0.webm
# 00388bd7-d313-4ce1-89e5-c88091f25357-9999-pajama-party-tutorial-blurred-00388bd7-d313-4ce1-89e5-c88091f25357-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-4324-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-4751-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-4751-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5257-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5257-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5334-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5334-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5357-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5357-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5369-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5369-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5375-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5375-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5377-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5377-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5387-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5387-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5398-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5398-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5414-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5414-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5424-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5424-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5448-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5448-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5456-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5456-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5531-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5531-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5532-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5532-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5533-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5533-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5549-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5566-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5566-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5645-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5645-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5651-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5651-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5653-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-5653-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 0079b262-7575-4ae7-a377-60e21070106e-9999-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-initial.webm
# 0079b262-7575-4ae7-a377-60e21070106e-9999-last-christmas-tutorial-0079b262-7575-4ae7-a377-60e21070106e-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5351-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5351-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5351-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5376-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5376-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5376-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5406-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5406-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5406-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5432-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5432b-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5435-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5435-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5435-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5443-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5443-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5443-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5446-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5446-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5446-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5452-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5452-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5452-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5461-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5461-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5461-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5474-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5474-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5474-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5493-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5493-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5493-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5555-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5562-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5562-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5562-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5630-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5630-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5630-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5640-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5640-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5640-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5647-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-0.5.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5647-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-initial-1.0.webm
# 02883b27-c152-4415-ae7a-1cb4c5f086e5-5647-last-christmas-blurred-02883b27-c152-4415-ae7a-1cb4c5f086e5-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-4751-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-4751-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-4751-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5340-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5340-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5340-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5356-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5369-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5369-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5369-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5377-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5377-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5377-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5381-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5381-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5381-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5387-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5387-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5387-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5396-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5396-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5396-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5398-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5398-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5398-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5404-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5404-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5404-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5410-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5410-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5410-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5427-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5427-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5427-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5489-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5489-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5489-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5531-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5531-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5531-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5533-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5533-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5533-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5566-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5566-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5566-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5610-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-0.5.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5610-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-initial-1.0.webm
# 102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-5610-pajama-party-tutorial-blurred-102d5dd7-f1f4-447d-9c0c-6e10a8afc4c3-performance.webm
# 2067fda2-b26f-405e-9e5d-c3fb1074f937-Anonomous-ahichallenge-7999d72d-30fe-4e02-a78b-18583908f6d8-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-4324-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-4324-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5334-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5334-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5334-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5341-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5341-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5341-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5342-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5342-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5342-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5357-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5357-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5357-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5375-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5375-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5375-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5388-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5388-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5388-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5389-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5389-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5389-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5414-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5414-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5414-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5424-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5424-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5424-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5430-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5430-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5430-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5448-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5448-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5448-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5513-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5513-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5513-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5522-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5522-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5522-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5532-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5532-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5532-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5532-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5549-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5549-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5628-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5628-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5628-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5645-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5645-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5645-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5651-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5651-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5651-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5651-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5653-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-0.5.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5653-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-initial-1.0.webm
# 44e54afd-19c0-4342-b753-fb4ab123aaad-5653-mad-at-disney-tutorial-blurred-44e54afd-19c0-4342-b753-fb4ab123aaad-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5341-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5341-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5368-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5368-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5388-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5388-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5389-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5389-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5420-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5420-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5430-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5430-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5435-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5435-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5446-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5446-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5474-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5474-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5485-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5493-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5493-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5513-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5513-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5522-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5522-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5640-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-initial.webm
# 917fe4e1-9590-44eb-a541-1cef13e4f1ea-5640-pajamaparty-tutorial-917fe4e1-9590-44eb-a541-1cef13e4f1ea-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-4751-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-4751-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-4751-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5369-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5369-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5369-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5377-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5377-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5377-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5387-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5387-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5387-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5398-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5398-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5398-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5435-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5435-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5435-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5446-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5446-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5446-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5456-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5456-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5456-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5474-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5474-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5474-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5493-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5493-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5493-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5531-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5531-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5531-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5533-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5533-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5533-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5555-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5555-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5555-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5566-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5566-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5566-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5640-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-0.5.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5640-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-initial-1.0.webm
# d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-5640-mad-at-disney-tutorial-blurred-d6ad5749-50d4-4cc7-99b5-6b9ddecebbf4-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5340-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5340-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5351-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5351-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5376-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5376-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5381-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5381-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5396-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5396-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5404-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5404-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5406-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5406-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5410-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5410-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5413-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5413-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5434-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5434-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5443-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5443-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5452-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5452-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5479-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5489-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5489-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5562-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5562-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5647-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-initial.webm
# e525302b-2740-4e73-aa37-170bd8ceb8d1-5647-mad-at-disney-tutorial-e525302b-2740-4e73-aa37-170bd8ceb8d1-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5340-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5340-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5340-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5341-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5341-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5341-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5342-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5342-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5342-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5368-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5368-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5368-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5381-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5381-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5381-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5388-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5388-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5388-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5389-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5389-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5389-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5396-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5396-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5396-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5404-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5404-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5404-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5410-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5410-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5410-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5427-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5427-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5427-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5430-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5430-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5430-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5489-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5489-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5489-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5513-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5513-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5513-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5522-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5522-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5522-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5628-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-0.5.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5628-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-initial-1.0.webm
# ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-5628-last-christmas-blurred-ec8fbc4c-bf9d-404d-a4ab-c626e23a4d2e-performance.webm
# """ 

# segmentations_map = {
#     'e525302b-2740-4e73-aa37-170bd8ceb8d1'
# }
# # %%
# from io import StringIO
# ls_out = StringIO(ls_output)

# def get_file_info(filename: str) -> str:
#     workflow_id = filename[:36]
#     user_id = filename[37:41]
#     workflow_name = filename[42:-55]
#     return workflow_id, user_id, workflow_name

# workflows = {}
# workflows_count = {}
# user_ids = set()

# for line in ls_out:
#     workflow_id, user_id, workflow_name = get_file_info(line)
#     if workflow_id != '' and user_id != '' and workflow_name != '' and user_id.isnumeric():
#         workflows[workflow_id] = workflow_name
#         if workflow_id in workflows_count:
#             workflows_count[workflow_id] += 1
#         else:
#             workflows_count[workflow_id] = 1

#         if user_id not in user_ids:
#             user_ids.add(user_id)


# # %%

# print("Workflow                             Count Name")
# #      00388bd7-d313-4ce1-89e5-c88091f25357       pajama-party-tutorial-blurred-
# for workflow_id, workflow_name in workflows.items():
#     print(workflow_id, f"{workflows_count[workflow_id]: 5}", workflow_name)
# # print(f"{workflows=}")
# print()
# print(f"{user_ids=}")