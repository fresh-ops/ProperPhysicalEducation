from analyzer.pose.pose_matcher import PoseMatcher
from model.pose import Pose
from model.exercise import Exercise


class ExerciseAnalyzer:
    def __init__(self, exercise: Exercise):
        self.poses = exercise.poses
        self.current_pose_index = 0
        self.pose_detector = PoseMatcher(self.poses)

    def analyze(self, current_pose: Pose) -> int:
        current_reference_pose: Pose = self.poses[self.current_pose_index]
        next_pose_index: int = (self.current_pose_index + 1) % len(self.poses)

        match_result = self.pose_detector.match(current_pose)
        closest_reference_pose = match_result.reference_pose
        if closest_reference_pose.id == current_reference_pose.id:
            if current_pose == current_reference_pose:
                self.current_pose_index = next_pose_index
                print("Correct pose!")
                return 0
            else:
                print("Almost correct pose. Try to adjust your position.")
                return 1
        else:
            print("Incorrect pose. Try again.")
            return 1
