
import itertools
from ..datatypes import CustomSerializable, MiniLesson as Lesson
from pathlib import Path
from typing import *
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from pandas import DataFrame
from pandas.core import frame

from . import pose_identifier
from ..utils import audio_analysis
from .landmark_processing import PoseLandmark, get_pixel_landmarks, normalize_landmarks, choose_landmarks
from .postprocessing import insert_prune_keyframes
from ..datatypes import Workflow, IMR

from . import imr_generation

# IMR_GENERATION_METHOD_NAME = 'julien_v2_TemporalSdmMinima_KeyframeExtension'

plt.ioff()

def _load_landmark_files(landmark_base_dir: Path):
    landmark_files: Dict[str, Dict[Literal['pose', 'rightHand', 'leftHand', 'face'], Path]] = {}

    def load_landmark(scope: str):
        # print(f"Finding {scope} files")
        matching_files = list(landmark_base_dir.rglob(f'*.{scope}.[c][s][v]'))
        keys_values = [
            (p.stem.replace(f'.{scope}', ''), p) for p in matching_files
        ]
        for key, value in keys_values:
            # print(f"   FOUND {scope} file: {key}: {value}")
            if not key in landmark_files:
                landmark_files[key] = {}
            landmark_files[key][scope] = value
    
    load_landmark('pose')
    load_landmark('rightHand')
    load_landmark('leftHand')
    load_landmark('face')
    
    return landmark_files

if __name__ == '__main__':
    import sys
    import json
    import matplotlib
    matplotlib.use('pdf')
    database_filepath = Path(sys.argv[1])
    landmark_dir = Path(sys.argv[2])
    audio_dir = Path(sys.argv[3])
    output_dir = Path(sys.argv[4])
    analysis_dir = Path(sys.argv[5])
    analysis_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.ioff()

    landmark_files = _load_landmark_files(landmark_dir)

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
        
        if len(landmarkScope) != 1 or landmarkScope[0] != 'pose':
            continue

        pose_landmark_path: Path = landmark_files.get(clipName, {}).get('pose')
        lefthand_landmark_path: Path = landmark_files.get(clipName, {}).get('leftHand')
        righthand_landmark_path: Path = landmark_files.get(clipName, {}).get('rightHand')
        face_landmark_path: Path = landmark_files.get(clipName, {}).get('face')

        done += 1
        if (done > num_songs):
            break

        print(f"Processing #{done: 2d} {clipName}")

        bpm = 0
        if audioSrc is not None:
            audioPath = Path(audioSrc)
            audioPath = audio_dir.joinpath(audioPath)
            bpm, = audio_analysis.perform_audio_analysis(audioPath)

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
        segmentationMethod = "HandsSpdMinima(Filtered)"

        keyframesIndices = hands_extension_extrema
        keyframeMethod = "HandExtensionExtrema"

        effective_tempo_bpm = bpm
        if bpm > 0:
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
            keyframeMethod = "BeatAligned"

            beats_per_segment = 4
            segmentationTimes = np.arange(startTime, endTime, secs_per_beat * beats_per_segment)
            if endTime - segmentationTimes[-1] < 0.5:
                segmentationTimes = segmentationTimes[:-1]
            segmentationTimes = np.append(segmentationTimes, endTime)
            segmentationMethod = "4BeatMeasures"

        keyframes = [
            IMR.Keyframe(
                timestamp=times.iloc[times.index.get_loc(kf_i, method='nearest')][0],
                significance=pose_identifier.get_net_movement(hands[kf_i:kf_i_next])
            )
            for kf_i, kf_i_next in zip(
                keyframesIndices,
                itertools.chain(keyframesIndices[1:], [end_frame])
            )
        ]
        keyframeMethod += "-filtered"

        chart_handspd = 0, 0
        
        chart_xyvel = 1, 0
        chart_netspd = 2, 0
        chart_handspdcorr = 0, 1
        chart_extension = 1, 1

        chart_handmotion = 2, 1

        fig, axs = plt.subplots(3, 2)
        fig.set_size_inches(18.5, 13.5)
        pose_identifier.plot_movement_extension(
            hands,
            fps,
            smooth_window=smooth_window,
            extrema_window=extrema_window,
            ax_spds=axs[chart_handspd],
            ax_spdcorrelation=axs[chart_handspdcorr],
            ax_spd_horz_vs_vertical=axs[chart_xyvel],
            ax_movement_net=axs[chart_netspd],
            ax_extension=axs[chart_extension],
        )
        
        axs[chart_handspd].yaxis.set_visible(True)
        axs[chart_handspd].yaxis.set_ticks([])
        axs[chart_handspd].set_ylabel('Speeds')
        axs[chart_handspdcorr].yaxis.set_visible(True)
        axs[chart_handspdcorr].yaxis.set_ticks([])
        axs[chart_handspdcorr].set_ylabel('Correlation')
        axs[chart_xyvel].yaxis.set_visible(True)
        axs[chart_xyvel].yaxis.set_ticks([])
        axs[chart_xyvel].set_ylabel('Horz vs Vert Speed')
        axs[chart_netspd].yaxis.set_visible(True)
        axs[chart_netspd].yaxis.set_ticks([])
        axs[chart_netspd].set_ylabel('Net Speed')
        axs[chart_extension].yaxis.set_visible(True)
        axs[chart_extension].yaxis.set_ticks([])
        axs[chart_extension].set_ylabel('Extension')

        fig.suptitle(f'{clipName} Motion Analysis (Hands)')
        fig.savefig(str(analysis_dir / f'{clipName}_handanalysis.pdf'))
        plt.close(fig)

        imr_file_out = output_dir / (clipName + '.imr.json')
        imr_file_out.parent.mkdir(parents=True, exist_ok=True)
        
        imr = imr_generation.create_imr(
            clipName=clipName,
            clipPath=clipPath,
            clipTitle=title,
            fps=fps,
            landmarkScope=landmarkScope,
            tempoBPM=None if bpm <= 0 else effective_tempo_bpm,
            thumbnailSrc=thumbnailSrc,
            segmentation=segmentationTimes,
            segmentationMethod=segmentationMethod,
            keyframes=keyframes,
            keyframeMethod=keyframeMethod
        )

        def create_motion_trails(startTime: float, endTime: float, label: str):
        # times.iloc[times.index.get_loc(kf_i, method='nearest')][0]
            startFrame = startTime * fps
            endFrame = endTime * fps
            
            leftLandmarks = pixel_landmarks[['leftWrist_x', 'leftWrist_y']]
            rightLandmarks = pixel_landmarks[['rightWrist_x', 'rightWrist_y']]

            motion_trails: List[IMR.MotionTrail] = []

            for landmarks, landmark_id in [(leftLandmarks, PoseLandmark.leftWrist), (rightLandmarks, PoseLandmark.rightWrist)]:
                startFrame = landmarks.index.get_loc(startFrame, method='nearest')
                endFrame = landmarks.index.get_loc(endFrame, method='nearest')
                landmarks_trimmed = landmarks.iloc[startFrame:endFrame]

                trailTimes = times.loc[startFrame:endFrame].iloc[:,0].to_numpy().tolist()
                x = list(landmarks_trimmed.iloc[:,0])
                y = list(landmarks_trimmed.iloc[:,1])
                minlen = min(len(x), len(y), len(trailTimes))
                trailTimes = trailTimes[:minlen]
                x = x[:minlen]
                y = y[:minlen]
                
                axs[chart_handmotion].plot(x, y, label=f'{label}-{landmark_id}')
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
        
        axs[chart_handmotion].legend()
        fig.suptitle(f'{clipName} Motion Analysis (Hands)')
        fig.savefig(str(analysis_dir / f'{clipName}_handanalysis.pdf'))

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