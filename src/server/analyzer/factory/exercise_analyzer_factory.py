from analyzer.exercise.exercise_analyzer import ExerciseAnalyzer
from analyzer.exercise.exercise_state_machine import ExerciseStateMachine
from analyzer.feedback.feedback_generator import FeedbackGenerator
from analyzer.feedback.rule_evaluator import RuleEvaluator
from analyzer.pose.pose_matcher.pose_matcher import PoseMatcher
from analyzer.pose.pose_matcher.strategy.penalty_strategy import PenaltyStrategy
from analyzer.pose.pose_matcher.strategy.pose_matcher_strategy import (
    PoseMatcherStrategy,
)
from loader.exercise_loader import ExerciseLoader
from config import settings


class ExerciseAnalyzerFactory:
    def __init__(
        self,
        exercise_loader: ExerciseLoader,
        match_strategy: PoseMatcherStrategy = PenaltyStrategy(),
    ) -> None:
        self.exercise_loader = exercise_loader
        self.match_strategy = match_strategy

    def create(self, exercise_id: int) -> ExerciseAnalyzer:
        exercise = self.exercise_loader.load_exercise(exercise_id)
        pose_matcher = PoseMatcher(exercise.poses, self.match_strategy)
        return ExerciseAnalyzer(
            exercise=exercise,
            pose_matcher=pose_matcher,
            exercise_state_machine=ExerciseStateMachine(
                exercise.poses, settings.frame_tolerance
            ),
            feedback_generator=FeedbackGenerator(RuleEvaluator(exercise.rules)),
        )
