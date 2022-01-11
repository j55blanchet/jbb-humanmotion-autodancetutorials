from typing import Callable, List
import cv2
import numpy as np
import mediapipe as mp
from collections import namedtuple
from pathlib import Path
# import draw  # draw the skeleton with the skeleton isolation input

POSE_LANDMARKS = {
  "nose": 0,
  "leftEyeInner": 1,
  "leftEye": 2,
  "leftEyeOuter": 3,
  "rightEyeInner": 4,
  "rightEye": 5,
  "rightEyeOuter": 6,
  "leftEar": 7,
  "rightEar": 8,
  "mouthLeft": 9,
  "mouthRight": 10,
  "leftShoulder": 11,
  "rightShoulder": 12,
  "leftElbow": 13,
  "rightElbow": 14,
  "leftWrist": 15,
  "rightWrist": 16,
  "leftPinky": 17,
  "rightPinky": 18,
  "leftIndex": 19,
  "rightIndex": 20,
  "leftThumb": 21,
  "rightThumb": 22,
  "leftHip": 23,
  "rightHip": 24,
  "leftKnee": 25,
  "rightKnee": 26,
  "leftAnkle": 27,
  "rightAnkle": 28,
  "leftHeel": 29,
  "rightHeel": 30,
  "leftFootIndex": 31,
  "rightFootIndex": 32,
}

HAND_LANDMARKS = {
  "wrist": 0,
  "thumbCMC": 1,
  "thumbMCP": 2,
  "thumbIP": 3,
  "thumbTIP": 4,
  "indexMCP": 5,
  "indexPIP": 6,
  "indexDIP": 7,
  "indexTIP": 8,
  "middleMCP": 9,
  "middlePIP": 10,
  "middleDIP": 11,
  "middleTIP": 12,
  "ringMCP": 13,
  "ringPIP": 14,
  "ringDIP": 15,
  "ringTIP": 16,
  "pinkyMCP": 17,
  "pinkyPIP": 18,
  "pinkyDIP": 19,
  "pinkyTIP": 20,
}
def create_header(cols: List[str]):
    all_cols = ['frame_index']
    all_cols = sum([[f"{name}_x", f"{name}_y", f"{name}_vis"] for name in cols], all_cols)
    return ",".join(all_cols)
    

HAND_HEADER = create_header(HAND_LANDMARKS.keys())
POSE_HEADER = create_header(POSE_LANDMARKS.keys())
FACE_HEADER = create_header([f'Face{id}' for id in range(468)])

def perform_by_frame(video_path, on_frame: Callable):
    try:
        cap = cv2.VideoCapture(video_path)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_count = 1 if frame_count == 0 else frame_count
        i = 0
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                return
                # raise Exception('Error reading image from video')

            # Convert the BGR image to RGB.q
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # To improve performance, optionally mark the image as not writeable to pass by reference.
            image.flags.writeable = False
            percent_done = int(i * 100 / frame_count)
            print(f'{percent_done}% ', end='')
            on_frame(image, i)
            i += 1
    finally:
        cap.release()

"""
goal: apply the mediapipe skeleton extraction onto a video clip

input: a video clip (e.g., example.mp4)

output: a csv file contains the skeleton information per frame    (joint_x, joint_y, visibility)* 33

"""
# set the input and output path here
# input_video_path = 'trimmed.mp4'
# output_csv_path = 'test.csv'
def process_video(input_video_path, frame_count, pose_csv_path, lefthand_csv_path, righthand_csv_path, face_csv_path):

    mp_pose = mp.solutions.pose
    mp_holistic = mp.solutions.holistic

    PRESENCE_THRESHOLD = 0.5
    RGB_CHANNELS = 3
    RED_COLOR = (0, 0, 255)
    VISIBILITY_THRESHOLD = 0.5
    
    # pose = mp_pose.Pose(
    #   min_detection_confidence=0.5, 
    #   min_tracking_confidence=0.5
    # )

    HolisticSolution = mp_holistic.Holistic(static_image_mode=False)

    pose_data, lefthand_data, righthand_data, face_data = [], [], [], []
    ppose, plefthand, prighthand, pface = None, None, None, None


    
    def process_frame(image, frame_index: int):
        results = HolisticSolution.process(image)
        pose_frame, lefthand_frame, righthand_frame, face_frame = [], [], [], []

        zero_visibility = False
        i = frame_index
        
        if not results.pose_landmarks:
            pass
            # print("Cannot capture a meaningful pose - igored %d-th frame" % i)
        else:
            pose_frame.append(i)
            for data_point in results.pose_landmarks.landmark:
                pose_frame.append(data_point.x)
                pose_frame.append(data_point.y)
                pose_frame.append(0.0 if zero_visibility else data_point.visibility)
            pose_data.append(pose_frame)
        
        if not results.left_hand_landmarks:
            pass
            # print("Cannot capture a meaningful left hand pose - igored %d-th frame" % i)
        else:
            lefthand_frame.append(i)
            for data_point in results.left_hand_landmarks.landmark:
                lefthand_frame.append(data_point.x)
                lefthand_frame.append(data_point.y)
                lefthand_frame.append(0.0 if zero_visibility else data_point.visibility)
            lefthand_data.append(lefthand_frame)
    
        if not results.right_hand_landmarks:
            pass
            # print("Cannot capture a meaningful right hand pose - igored %d-th frame" % i)
        else:
            righthand_frame.append(i)
            for data_point in results.right_hand_landmarks.landmark:
                righthand_frame.append(data_point.x)
                righthand_frame.append(data_point.y)
                righthand_frame.append(0.0 if zero_visibility else data_point.visibility)
            righthand_data.append(righthand_frame)
        
        if not results.face_landmarks:
            # print("\t\tCannot capture a meaningful right hand pose - igored %d-th frame" % i)
            pass
        else:
            face_frame.append(i)
            for data_point in results.face_landmarks.landmark:
                face_frame.append(data_point.x)
                face_frame.append(data_point.y)
                face_frame.append(0.0 if zero_visibility else data_point.visibility)
            face_data.append(face_frame)        

    perform_by_frame(input_video_path, process_frame)

    for data, filepath, header in [
        (pose_data, pose_csv_path, POSE_HEADER),
        (lefthand_data, lefthand_csv_path, HAND_HEADER),
        (righthand_data, righthand_csv_path, HAND_HEADER),
        (face_data, face_csv_path, FACE_HEADER),
    ]:
        if filepath is not None:
            final_data = np.around(np.array(data), 2)
            print(final_data.shape)
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            np.savetxt(str(Path(filepath)), final_data, delimiter=',', fmt='%f', header=header)
            print(f'\t{Path(input_video_path).stem} => {filepath}')

    HolisticSolution.close()

if __name__ == "__main__":
    process_video(
        input_video_path = 'data/2d/videos/renegade.mp4',
        pose_csv_path = 'data/2d/poses/renegade.poses.csv',
        lefthand_csv_path=None,
        righthand_csv_path=None,
        face_csv_path=None,
    )