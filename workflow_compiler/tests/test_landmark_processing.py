from pathlib import Path
import tempfile
import unittest

import pandas as pd

from workflow_compiler.imr_generation.analysis_pipeline import discover_landmark_files, load_pose_landmarks
from workflow_compiler.imr_generation.landmark_processing import get_pixel_landmarks, get_pose2d_pixel_landmarks
from workflow_compiler.imr_generation.pose_identifier import validate_normalized_landmarks


def _write_csv(path: Path, content: str) -> None:
    path.write_text(content, encoding='utf-8')


class LandmarkProcessingTests(unittest.TestCase):
    def test_discover_landmark_files_finds_pose_and_pose2d(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / 'landmarks'
            data_dir.mkdir()
            _write_csv(
                data_dir / 'clip.pose.csv',
                'frame_index,nose_x,nose_y,nose_vis\n1,0.5,0.25,1\n',
            )
            _write_csv(
                data_dir / 'clip.pose2d.csv',
                'frame,NOSE_x,NOSE_y,NOSE_distance,NOSE_vis\n0,100,200,1,0.9\n',
            )

            landmark_files = discover_landmark_files(data_dir)

            self.assertEqual(set(landmark_files['clip'].keys()), {'pose', 'pose2d'})

    def test_get_pixel_landmarks_scales_normalized_pose_csv(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / 'clip.pose.csv'
            _write_csv(
                csv_path,
                'frame_index,nose_x,nose_y,nose_vis,leftShoulder_x,leftShoulder_y,leftShoulder_vis\n'
                '1,0.5,0.25,1,0.1,0.2,1\n',
            )

            landmarks = get_pixel_landmarks(csv_path, width=200, height=400)

            self.assertEqual(list(landmarks.columns), ['nose_x', 'nose_y', 'leftShoulder_x', 'leftShoulder_y'])
            self.assertEqual(landmarks.iloc[0].tolist(), [100.0, 100.0, 20.0, 80.0])

    def test_get_pose2d_pixel_landmarks_canonicalizes_and_drops_distance(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / 'clip.pose2d.csv'
            _write_csv(
                csv_path,
                'frame,NOSE_x,NOSE_y,NOSE_distance,NOSE_vis,LEFT_SHOULDER_x,LEFT_SHOULDER_y,LEFT_SHOULDER_distance,LEFT_SHOULDER_vis\n'
                '0,100,200,1,0.9,300,400,2,0.8\n',
            )

            landmarks = get_pose2d_pixel_landmarks(csv_path)

            self.assertEqual(list(landmarks.columns), ['nose_x', 'nose_y', 'leftShoulder_x', 'leftShoulder_y'])
            self.assertEqual(landmarks.iloc[0].tolist(), [100.0, 200.0, 300.0, 400.0])

    def test_load_pose_landmarks_routes_pose2d_without_scaling(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / 'clip.pose2d.csv'
            _write_csv(
                csv_path,
                'frame,NOSE_x,NOSE_y,NOSE_distance,NOSE_vis\n0,123,456,1,0.9\n',
            )

            landmarks = load_pose_landmarks(csv_path, width=200, height=400)

            self.assertEqual(landmarks.iloc[0].tolist(), [123.0, 456.0])

    def test_validate_normalized_landmarks_rejects_pixel_coordinates(self):
        landmarks = pd.DataFrame({'leftWrist_x': [120.0], 'leftWrist_y': [260.0]})

        with self.assertRaises(ValueError) as exc_info:
            validate_normalized_landmarks(landmarks, 'test')

        self.assertIn('pixel coordinates', str(exc_info.exception))


if __name__ == '__main__':
    unittest.main()