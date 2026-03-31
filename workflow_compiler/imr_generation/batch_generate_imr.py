
import itertools
from ..datatypes import CustomSerializable, MiniLesson as Lesson
from pathlib import Path
from typing import *
import numpy as np
import pandas as pd
from pandas import DataFrame
from pandas.core import frame

from . import pose_identifier
from ..utils import audio_analysis
from .landmark_processing import PoseLandmark, get_pixel_landmarks, normalize_landmarks, choose_landmarks
from .postprocessing import insert_prune_keyframes
from ..datatypes import Workflow, IMR

from . import imr_generation
from . import analysis_pipeline
from . import gendered_movement_analysis

# IMR_GENERATION_METHOD_NAME = 'julien_v2_TemporalSdmMinima_KeyframeExtension'

def _nearest_index(index: pd.Index, value: float) -> int:
    nearest = index.get_indexer([value], method='nearest')[0]
    if nearest < 0:
        raise ValueError(f'Unable to find nearest index for value: {value}')
    return int(nearest)

if __name__ == '__main__':
    import sys
    import json
    import matplotlib
    import argparse
    
    matplotlib.use('pdf')
    parser = argparse.ArgumentParser()

    parser.add_argument('database_filepath', type=Path, help='Path to the database file')
    parser.add_argument('landmark_dir', type=Path, help='Path to the directory containing the landmark files')
    parser.add_argument('audio_dir', type=Path, help='Path to the directory containing the audio files')
    parser.add_argument('output_dir', type=Path, help='Path to the directory where the generated IMRs will be saved')
    parser.add_argument('analysis_dir', type=Path, help='Path to the directory where the generated analysis files will be saved')
    parser.add_argument('--skip-existing', '-s', dest="skip_existing", action='store_true', help='Skip songs that already have an IMR')
    parser.add_argument(
        '--segmentation-method',
        '--segmentation_method',
        dest='segmentation_method',
        choices=['speed-minima', 'tempo'],
        default='speed-minima',
        help='Segmentation strategy: speed-minima (default) or tempo-based segmentation.',
    )
    args = parser.parse_args()

    database_filepath = args.database_filepath
    landmark_dir = args.landmark_dir
    audio_dir = args.audio_dir
    output_dir = args.output_dir
    analysis_dir = args.analysis_dir

    skip_existing_imr = args.skip_existing

    analysis_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    landmark_files = analysis_pipeline.load_landmark_files(landmark_dir)

    db = []
    with open(database_filepath, 'r', encoding='utf-8') as db_file:
        db = json.load(db_file)

    import math
    num_songs = math.inf
    done = 0

    for motion_entry in db:
        title = motion_entry['title']
        clipName = motion_entry['clipName']
        clipPath = motion_entry['clipPath']
        fps = motion_entry['fps']
        startTime = motion_entry['startTime']
        endTime = motion_entry['endTime']
        width = motion_entry['width']
        height = motion_entry['height']
        poseUpperBody = motion_entry['poseUpperBodyOnly']
        landmarkScope = motion_entry['landmarkScope']
        audioSrc = motion_entry.get('audioSrc', None)
        thumbnailSrc = motion_entry['thumbnailSrc']
        bpm = motion_entry.get('bpm', 0)
        
        if len(landmarkScope) != 1 or landmarkScope[0] != 'pose':
            continue

        imr_file_out = output_dir / (clipName + '.imr.json')
        imr_file_out.parent.mkdir(parents=True, exist_ok=True)
        if skip_existing_imr and imr_file_out.exists():
            print(f"Skipping {clipName} because IMR already exists")
            continue

        pose_landmark_path: Path = landmark_files.get(clipName, {}).get('pose')
        lefthand_landmark_path: Path = landmark_files.get(clipName, {}).get('leftHand')
        righthand_landmark_path: Path = landmark_files.get(clipName, {}).get('rightHand')
        face_landmark_path: Path = landmark_files.get(clipName, {}).get('face')

        done += 1
        if (done > num_songs):
            break

        print(f"Processing #{done: 2d} {clipName}")

        extrema_window = int(fps // 3)
        smooth_window = int(fps // 3)
        if (smooth_window < 3): smooth_window = 3
        if smooth_window % 2 == 0: smooth_window += 1

        pixel_landmarks = get_pixel_landmarks(pose_landmark_path, width, height)

        if len(pixel_landmarks) == 0:
            print(f"   Invalid landmark file for {clipName} @ '{pose_landmark_path}'", file=sys.stderr)
            continue

        norm_landmarks = normalize_landmarks(pixel_landmarks, [PoseLandmark.leftShoulder, PoseLandmark.rightShoulder], [PoseLandmark.leftHip, PoseLandmark.rightHip])

        start_frame = int(startTime * fps)
        end_frame = int(endTime * fps)
        clipped_landmarks = norm_landmarks[start_frame:end_frame]
        
        shoulders = choose_landmarks(clipped_landmarks, [PoseLandmark.leftShoulder, PoseLandmark.rightShoulder])
        hands = choose_landmarks(clipped_landmarks, [PoseLandmark.leftWrist, PoseLandmark.rightWrist], relative_to=shoulders)

        times = pose_identifier.get_times(hands, fps)

        hands_extension = pose_identifier.get_extension(hands, smooth_window)
        _, _, hands_extension_extrema = pose_identifier.get_extrema(hands_extension, frame_window = extrema_window)
        extension_keyframes = times.iloc[hands_extension_extrema].values[:,0].tolist()

        min_kf_dist = 0.06
        max_kf_dist = 0.24
        # inserted_pruned_extension_kfs = list(insert_prune_keyframes(startTime, endTime, extension_keyframes, max_kf_dist, min_kf_dist))
        
        hands_spd_minima = pose_identifier.get_spd_minima(hands, smooth_window, extrema_window)
        # spd_minima_keyframes = times.iloc[hands_spd_minima].values[:,0].tolist()
        # inserted_pruned_spdminima_kfs = list(insert_prune_keyframes(startTime, endTime, spd_minima_keyframes, max_kf_dist, min_kf_dist))
        
        #target roughly every two seconds
        hands_spd_minima_temporal_segments = pose_identifier.get_spd_minima(hands, smooth_window, int(fps * 2))
        hands_spd_minima_temporal_segments = times.iloc[hands_spd_minima_temporal_segments].values[:,0].tolist()

        # remove the first and last keyframes if they are too close to the start and end
        if hands_spd_minima_temporal_segments[0] - startTime < 0.5:
            hands_spd_minima_temporal_segments = hands_spd_minima_temporal_segments[1:]
        if hands_spd_minima_temporal_segments[-1] - endTime > -0.5:
            hands_spd_minima_temporal_segments = hands_spd_minima_temporal_segments[:-1]
        
        segmentationTimes = list(itertools.chain([startTime], hands_spd_minima_temporal_segments, [endTime]))
        keyframesIndices = hands_extension_extrema
        generationMethod = "Speed-Minima Segmentation with Retraction/Extension Keyframes"

        effective_tempo_bpm = bpm
        if bpm > 0 and args.segmentation_method == 'tempo':
            tempo_keyframe_bpm_min = 50
            tempo_keyframe_bpm_max = 100
            effective_tempo_bpm = bpm
            while effective_tempo_bpm > tempo_keyframe_bpm_max:
                effective_tempo_bpm /= 2
            while effective_tempo_bpm < tempo_keyframe_bpm_min:
                effective_tempo_bpm *= 2
            
            secs_per_beat = 60 / effective_tempo_bpm
            beat_timestamps = np.arange(startTime, endTime, secs_per_beat)
            keyframesIndices = np.array([int(round(ts * fps)) for ts in beat_timestamps])

            beats_per_segment = 4
            segmentationTimes = np.arange(startTime, endTime, secs_per_beat * beats_per_segment)
            if endTime - segmentationTimes[-1] < 0.5:
                segmentationTimes = segmentationTimes[:-1]
            segmentationTimes = np.append(segmentationTimes, endTime)
            
            generationMethod = "4-Beat Tempo-Based Segmentation"

        keyframes = [
            IMR.Keyframe(
                timestamp=times.iloc[_nearest_index(times.index, kf_i), 0],
                significance=pose_identifier.get_net_movement(hands[kf_i:kf_i_next])
            )
            for kf_i, kf_i_next in zip(
                keyframesIndices,
                itertools.chain(keyframesIndices[1:], [end_frame])
            )
        ]
        # keyframeMethod += "-filtered"

        if analysis_dir is not None:
            analysis_pipeline.write_clip_analysis(
                clip_name=clipName,
                hands=hands,
                fps=fps,
                smooth_window=smooth_window,
                extrema_window=extrema_window,
                analysis_dir=analysis_dir,
                pose_landmarks=clipped_landmarks,
                segmentation_times=list(segmentationTimes),
            )
        
        imr = imr_generation.create_imr(
            clipName=clipName,
            clipPath=clipPath,
            clipTitle=title,
            fps=fps,
            landmarkScope=landmarkScope,
            tempoBPM=None if bpm <= 0 else effective_tempo_bpm,
            thumbnailSrc=thumbnailSrc,
            segmentation=segmentationTimes,
            genMethod=generationMethod,
            keyframes=keyframes,
        )

        def create_motion_trails(startTime: float, endTime: float, label: str):
        # times.iloc[times.index.get_loc(kf_i, method='nearest')][0]
            startFrame = startTime * fps
            endFrame = endTime * fps
            
            leftLandmarks = pixel_landmarks[['leftWrist_x', 'leftWrist_y']]
            rightLandmarks = pixel_landmarks[['rightWrist_x', 'rightWrist_y']]

            motion_trails: List[IMR.MotionTrail] = []

            for landmarks, landmark_id in [(leftLandmarks, PoseLandmark.leftWrist), (rightLandmarks, PoseLandmark.rightWrist)]:
                startFrame = _nearest_index(landmarks.index, startFrame)
                endFrame = _nearest_index(landmarks.index, endFrame)
                landmarks_trimmed = landmarks.iloc[startFrame:endFrame]

                trailTimes = times.loc[startFrame:endFrame].iloc[:,0].to_numpy().tolist()
                x = list(landmarks_trimmed.iloc[:,0])
                y = list(landmarks_trimmed.iloc[:,1])
                minlen = min(len(x), len(y), len(trailTimes))
                trailTimes = trailTimes[:minlen]
                x = x[:minlen]
                y = y[:minlen]
                
                # axs[chart_handmotion].plot(x, y, label=f'{label}-{landmark_id}')
                motion_trails.append(
                    IMR.MotionTrail(
                        landmark=landmark_id,
                        times=trailTimes,
                        x=list(x),
                        y=list(y)
                    )
                )

                # try:
                #     from scipy.interpolate import make_interp_spline
                #     spl = make_interp_spline(landmarks_trimmed.index, landmarks_trimmed, k=3)
                #     fitted_motiontrail = spl(np.arange(startFrame, endFrame))
                #     # axs[chart_handmotion].plot(fitted_motiontrail.T[0], fitted_motiontrail.T[1], label=f'{label}-{landmark_id}-fitted')
                # except Exception as e:
                #     pass
            return motion_trails
        
        for i, seg in enumerate(imr.temporalSegments):
            seg.motionTrails = create_motion_trails(seg.startTime, seg.endTime, f'Segment {i}')

        gendered_metrics, _ = gendered_movement_analysis.compute_gendered_movement_metrics(
            pose_landmarks=clipped_landmarks,
            fps=fps,
            smooth_window=smooth_window,
        )
        segmentation_share_summary = gendered_movement_analysis.segmentation_share_summary(
            gendered_metrics,
            list(segmentationTimes),
        )
        for seg, share_summary in zip(imr.temporalSegments, segmentation_share_summary):
            seg.hipShoulderShare = share_summary['hip_shoulder_share']
        
        # if analysis_dir is not None:
            # axs[chart_handmotion].legend()
            # fig.suptitle(f'{clipName} Motion Analysis (Hands)')
            # fig.savefig(str(analysis_dir / f'{clipName}_handanalysis.pdf'))

        # imr = IMR.IMR(
        #     clipName, 
        #     clipPath,
        #     genMethod=IMR_GENERATION_METHOD_NAME,
        #     startTime=startTime,
        #     endTime=endTime,
        #     segments=[
        #         IMR.TemporalSegment(
        #             startTime=tempSegStart,
        #             endTime=tempSegEnd,
        #             motions=[],
        #             keyframes=[],
        #         )
        #         for (tempSegStart, tempSegEnd) in zip(
        #             itertools.chain([startTime], hands_spd_minima_temporal_segments),
        #             itertools.chain(hands_spd_minima_temporal_segments, [endTime])
        #         )
        #     ],
        #     fps=fps,
        #     landmarkScope=landmarkScope,
        #     tempoBPM=bpm if bpm > 0 else None,
        #     keyframes=extension_keyframes,
        # )

        with imr_file_out.open('w') as f:
            imr.write_json(f, indent=2)
