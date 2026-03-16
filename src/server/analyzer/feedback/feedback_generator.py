from analyzer.feedback.rule_evaluator import RuleEvaluator
from model.pose import Pose
from model.pose_match_result import PoseMatchResult


class FeedbackGenerator:
    def __init__(self, rule_evaluator: RuleEvaluator):
        self.rule_evaluator = rule_evaluator

    def generate(
        self,
        pose_match_result: PoseMatchResult,
        current_pose: Pose,
        expected_pose: Pose,
    ) -> list[str]:
        feedbacks = self.rule_evaluator.evaluate(current_pose, expected_pose)

        if pose_match_result.pose.name != expected_pose.name:
            feedbacks.append(f"Сейчас нужно перейти в позу '{expected_pose.name}'")

        if len(feedbacks) == 0:
            feedbacks.append("Отличная работа! Продолжайте в том же духе!")

        return feedbacks[:2]
