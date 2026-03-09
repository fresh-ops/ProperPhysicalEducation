import pytest

from analyzer.exercise.exercise_analyzer import ExerciseAnalyzer
from loader.exercise_loader import ExerciseLoader
from loader.pose_loader import PoseLoader
from model.exercise import Exercise
from model.pose import Pose
from test.util.pose_factory import create_pose_from_points

arms_down_pose = create_pose_from_points("arms_down_points")
t_pose = create_pose_from_points("t_pose_points")
incorrect_t_pose = create_pose_from_points("incorrect_t_pose_points")

exercise_loader = ExerciseLoader(PoseLoader(directory_path='data/pose'), directory_path='data/exercise')
lateral_raises_exercise = exercise_loader.load_exercise(1)

test_data = [
    (lateral_raises_exercise,
    [arms_down_pose, t_pose, arms_down_pose],
    [0, 0, 0]),

    (lateral_raises_exercise,
    [arms_down_pose, incorrect_t_pose, arms_down_pose],
    [0, 1, 1]),

    (lateral_raises_exercise,
    [t_pose, arms_down_pose, t_pose],
    [1, 0, 0])
]

@pytest.mark.parametrize("exercise, pose_sequence, expected_results", test_data)
def test_analyze(exercise: Exercise, pose_sequence: list[Pose], expected_results: list[int]):
    analyzer = ExerciseAnalyzer(exercise=exercise)

    for pose, expected in zip(pose_sequence, expected_results):
        assert analyzer.analyze(pose) == expected
   