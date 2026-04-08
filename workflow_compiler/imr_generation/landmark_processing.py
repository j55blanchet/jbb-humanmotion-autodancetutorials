
"""Landmark processing and normalization for pose estimation data.

This module handles parsing and normalizing motion capture pose landmarks from two distinct
file formats, both representing MediaPipe Holistic Pose estimates (33 joints per frame).

SCHEMA REFERENCE: .pose.csv (Normalized Coordinates)
====================================================
Source:     web-frontend video annotation (SvelteKit app)
Coordinates: Normalized [0, 1] range (relative to video frame dimensions)
Columns:    3 columns per landmark: <jointName>_x, <jointName>_y, <jointName>_vis

Example header:
  Frame, <timestamp columns...>, 
  nose_x, nose_y, nose_vis,
  leftEyeInner_x, leftEyeInner_y, leftEyeInner_vis,
  ...
  rightFootIndex_x, rightFootIndex_y, rightFootIndex_vis

Column naming: camelCase with lowercase first character (e.g., leftShoulder, rightHip)
Values (x, y): Float [0, 1], where (0, 0) = top-left, (1, 1) = bottom-right
Visibility:    Float [0, 1], where 1 = high confidence landmark

Processing:    Parsed by get_pixel_landmarks() -> scaled by video width/height


SCHEMA REFERENCE: .pose2d.csv (Pixel Coordinates)
==================================================
Source:     genderdance motion capture pipeline (pose2d tracked data)
Coordinates: Direct pixel coordinates in original video frame
Columns:    4 columns per landmark: <JOINT>_x, <JOINT>_y, <JOINT>_distance, <JOINT>_vis

Example header:
  Frame,
  NOSE_x, NOSE_y, NOSE_distance, NOSE_vis,
  LEFT_SHOULDER_x, LEFT_SHOULDER_y, LEFT_SHOULDER_distance, LEFT_SHOULDER_vis,
  ...
  RIGHT_FOOT_INDEX_x, RIGHT_FOOT_INDEX_y, RIGHT_FOOT_INDEX_distance, RIGHT_FOOT_INDEX_vis

Column naming: UPPERCASE_UNDERSCORE (e.g., LEFT_SHOULDER, RIGHT_HIP)
Values (x, y):  Integer/float, direct pixel positions (e.g., 120, 450 in 1920x1080 frame)
Distance:      Float, confidence metric or distance from tracker (coordinate-space dependent)
Visibility:    Float [0, 1], detection confidence

Processing:    Parsed by get_pose2d_pixel_landmarks() -> no scaling applied (already pixel)
                Column names canonicalized to camelCase to match standard schema


COORDINATE SPACE SEMANTICS
===========================
1. Raw Normalized [0, 1]: Values from .pose.csv before any scaling
2. Pixel Coordinates: Raw integer/float positions in video frame space
    - .pose2d.csv files are already in this space
    - .pose.csv files are converted via: x *= width, y *= height
3. Normalized Relative: Optional derived space for specialized transforms
    - Centered on reference joint pair midpoint (typically torso)
    - Scaled by distance between reference joints
    - Result range: typically [-5, +5] for full-body motion

Current downstream analysis is pixel-first and computes speed/extension/symmetry
in pixel space (often after subtracting a local reference such as shoulders).


LANDMARK ENUMERATION (MediaPipe Holistic)
==========================================
MediaPipe Pose Estimation defines 33 landmarks (0-indexed):
- Face region: 0 (nose), 1-10 (eyes, ears)
- Upper body: 11-16 (shoulders, elbows, wrists)
- Hands: 17-22 (pinky, index, thumb on each side)
- Lower body: 23-32 (hips, knees, ankles, feet)

See PoseLandmark enum below for full joint names and indices.
"""

from pathlib import Path
import pandas as pd
from pandas import DataFrame
import numpy as np
from typing import List, Optional
import re

from enum import IntEnum

from pandas.core.series import Series

class Landmark(IntEnum):
    pass

class PoseLandmark(Landmark):
    nose = 0
    leftEyeInner = 1
    leftEye = 2
    leftEyeOuter = 3
    rightEyeInner = 4
    rightEye = 5
    rightEyeOuter = 6
    leftEar = 7
    rightEar = 8
    mouthLeft = 9
    mouthRight = 10
    leftShoulder = 11
    rightShoulder = 12
    leftElbow = 13
    rightElbow = 14
    leftWrist = 15
    rightWrist = 16
    leftPinky = 17
    rightPinky = 18
    leftIndex = 19
    rightIndex = 20
    leftThumb = 21
    rightThumb = 22
    leftHip = 23
    rightHip = 24
    leftKnee = 25
    rightKnee = 26
    leftAnkle = 27
    rightAnkle = 28
    leftHeel = 29
    rightHeel = 30
    leftFootIndex = 31
    rightFootIndex = 32

class HandLandmarks(Landmark):
    wrist = 0
    thumbCMC = 1
    thumbMCP = 2
    thumbIP = 3
    thumbTIP = 4
    indexMCP = 5
    indexPIP = 6
    indexDIP = 7
    indexTIP = 8
    middleMCP = 9
    middlePIP = 10
    middleDIP = 11
    middleTIP = 12
    ringMCP = 13
    ringPIP = 14
    ringDIP = 15
    ringTIP = 16
    pinkyMCP = 17
    pinkyPIP = 18
    pinkyDIP = 19
    pinkyTIP = 20


POSE_LANDMARK_NAMES = [landmark.name for landmark in PoseLandmark]
POSE_LANDMARK_NAME_SET = set(POSE_LANDMARK_NAMES)
POSE_LANDMARK_PREFIX_MAP = {
    re.sub(r'(?<!^)(?=[A-Z])', '_', landmark.name).upper(): landmark.name
    for landmark in PoseLandmark
}


def _canonicalize_pose_landmark_prefix(prefix: str) -> str:
    if prefix in POSE_LANDMARK_NAME_SET:
        return prefix

    canonical_prefix = POSE_LANDMARK_PREFIX_MAP.get(prefix.upper())
    if canonical_prefix is not None:
        return canonical_prefix

    raise KeyError(f'Unknown pose landmark prefix: {prefix}')


def _canonicalize_landmark_columns(landmarks: DataFrame) -> DataFrame:
    renamed_columns: list[str] = []

    for column in landmarks.columns:
        if not isinstance(column, str):
            renamed_columns.append(column)
            continue

        canonical_column = column
        for suffix in ('_x', '_y', '_vis', '_distance'):
            if column.endswith(suffix):
                column_prefix = column[: -len(suffix)]
                canonical_column = _canonicalize_pose_landmark_prefix(column_prefix) + suffix
                break

        renamed_columns.append(canonical_column)

    canonical = landmarks.copy()
    canonical.columns = renamed_columns
    return canonical

def get_pixel_landmarks(filepath: Path, width: int, height: int) -> DataFrame:
    """Parse .pose.csv (normalized coordinates) and return pixel coordinates.

    INPUT SCHEMA (.pose.csv):
    - Coordinates: normalized [0, 1] range
    - Columns: <jointName>_x, <jointName>_y, <jointName>_vis (3 per joint)
    - Naming: camelCase (e.g., leftShoulder_x, rightHip_y)

    PROCESSING:
    1. Canonicalize column names (already lowercase camelCase)
    2. Drop visibility columns
    3. Scale x values by width, y values by height

    OUTPUT: DataFrame with pixel coordinates [0, width] x [0, height], x/y pairs only

    Args:
        filepath: Path to .pose.csv file
        width: Video frame width in pixels
        height: Video frame height in pixels

    Returns:
        DataFrame indexed by frame number, columns are <jointName>_x, <jointName>_y
    """
    landmarks = _canonicalize_landmark_columns(pd.read_csv(str(filepath), header=0, index_col=0))

    visibility_cols = [column for column in landmarks.columns if isinstance(column, str) and column.endswith('_vis')]
    if visibility_cols:
        landmarks = landmarks.drop(columns=visibility_cols)

    pixel_landmarks = landmarks.copy()
    pixel_landmarks.iloc[:, 0::2] *= width
    pixel_landmarks.iloc[:, 1::2] *= height

    return pixel_landmarks


def get_pose2d_pixel_landmarks(filepath: Path) -> DataFrame:
    """Parse .pose2d.csv (pixel coordinates) and return pixel coordinates.

    INPUT SCHEMA (.pose2d.csv):
    - Coordinates: direct pixel values (already in frame space, no scaling needed)
    - Columns: <JOINT>_x, <JOINT>_y, <JOINT>_distance, <JOINT>_vis (4 per joint)
    - Naming: UPPERCASE_UNDERSCORE (e.g., LEFT_SHOULDER_x, RIGHT_HIP_y)

    PROCESSING:
    1. Canonicalize column names: UPPERCASE_UNDERSCORE → camelCase
       (e.g., LEFT_SHOULDER_x → leftShoulder_x)
    2. Drop visibility and distance columns (metadata, not needed downstream)
    3. Return x/y pairs as-is (no scaling; already pixel coordinates)

    OUTPUT: DataFrame with pixel coordinates, x/y pairs only, canonical naming

    Args:
        filepath: Path to .pose2d.csv file

    Returns:
        DataFrame indexed by frame number, columns are <jointName>_x, <jointName>_y
    """
    landmarks = _canonicalize_landmark_columns(pd.read_csv(str(filepath), header=0, index_col=0))

    drop_cols = [
        column
        for column in landmarks.columns
        if isinstance(column, str) and (column.endswith('_vis') or column.endswith('_distance'))
    ]
    if drop_cols:
        landmarks = landmarks.drop(columns=drop_cols)

    return landmarks

def normalize_landmarks(pixel_landmarks: DataFrame, ref_a_lmarks: List[int], ref_b_lmarks: List[int]) -> DataFrame:
    """Convert pixel coordinates into torso-centered, torso-scaled relative coordinates."""

    # Calculate A & B reference positions (averages of relevant columns)
    ref_a_indices = [int(landmark) for landmark in ref_a_lmarks]
    ref_b_indices = [int(landmark) for landmark in ref_b_lmarks]
    a = pd.DataFrame()    
    a['x'] = pixel_landmarks.iloc[:, [landmark * 2 for landmark in ref_a_indices]].mean(axis=1)
    a['y'] = pixel_landmarks.iloc[:, [landmark * 2 + 1 for landmark in ref_a_indices]].mean(axis=1)
    b = pd.DataFrame()
    b['x'] = pixel_landmarks.iloc[:, [landmark * 2 for landmark in ref_b_indices]].mean(axis=1)
    b['y'] = pixel_landmarks.iloc[:, [landmark * 2 + 1 for landmark in ref_b_indices]].mean(axis=1)
    ref_xy_difference = a - b
    ref_dist = ref_xy_difference.apply(np.linalg.norm, axis=1)

    # Calculate centerpoint (midway between A and B)
    center_point = pd.DataFrame()
    center_point['x'] = (a['x'] + b['x']) / 2
    center_point['y'] = (a['y'] + b['y']) / 2

    # Transform pixel-landmarks to relative coordinates (based on centerpoint)
    pixel_relative_landmarks = pixel_landmarks.copy()
    pixel_relative_landmarks.iloc[:, 0::2] = pixel_relative_landmarks.iloc[:, 0::2].subtract(center_point['x'], axis=0)
    pixel_relative_landmarks.iloc[:, 1::2] = pixel_relative_landmarks.iloc[:, 1::2].subtract(center_point['y'], axis=0)
    
    # Normalize landmarks based on reference points distance
    normalized_landmarks = pixel_relative_landmarks.divide(ref_dist, axis=0)
    return normalized_landmarks

def choose_landmarks(normalized_landmarks: DataFrame, chosen_landmarks: List[int], relative_to: Optional[DataFrame] = None) -> DataFrame:
    """Select landmark x/y pairs while preserving the coordinate space of the input."""

    selection = DataFrame()
    for i, landmark_i in enumerate(chosen_landmarks):

        col_x = landmark_i * 2
        col_y = col_x + 1
        for j, col_i in enumerate((col_x, col_y)):
            col = normalized_landmarks.iloc[:, col_i]

            if relative_to is not None:
                relative_col = relative_to.iloc[:, i * 2 + j]
                col -= relative_col
                relative_name = '' if relative_col.name is None else str(relative_col.name)
                col.name = f'{str(col.name)}_relativeto_{relative_name}'

            selection[col.name] = col
        
    return selection