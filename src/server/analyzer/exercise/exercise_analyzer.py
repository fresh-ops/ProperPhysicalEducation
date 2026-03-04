from model.pose import Pose
from model.exercise import Exercise
from analyzer.pose.pose_detector import PoseDetector


class ExerciseAnalyzer:
    def __init__(self, exercise: Exercise):
        self.poses = exercise.poses
        self.current_pose_index = 0
        self.pose_detector = PoseDetector(self.poses)

    
    def analyze(self, current_pose: Pose):
        current_reference_pose: Pose = self.poses[self.current_pose_index]
        next_pose_index: int = (self.current_pose_index + 1) % len(self.poses)

        closest_reference_pose: Pose = self.pose_detector.detect_closest_reference_pose(current_pose)
        if closest_reference_pose.id == current_reference_pose.id:
            if current_pose == current_reference_pose:
                self.current_pose_index = next_pose_index
                print("Correct pose!")
            else:
                print("Almost correct pose. Try to adjust your position.")
        else:
            print("Incorrect pose. Try again.")
