from domain.model.angle import Angle
from domain.model.pose import Pose
from domain.model.pose_id import PoseId
from domain.model.pose_match_result import PoseMatchResult
from domain.model.pose_rule import PoseRule
from domain.service.rule.strategy.pose_rule_strategy import PoseRuleStrategy


def _make_pose(pose_id: str) -> Pose:
    return Pose(
        id=PoseId(id=pose_id),
        name="pose",
        threshold=10.0,
        left_shoulder_angle=90.0,
        right_shoulder_angle=90.0,
        left_elbow_angle=180.0,
        right_elbow_angle=180.0,
        left_knee_angle=180.0,
        right_knee_angle=180.0,
        left_hip_angle=180.0,
        right_hip_angle=180.0,
    )


def test_validate_returns_false_when_pose_id_does_not_match_rule() -> None:
    strategy = PoseRuleStrategy()
    rule = PoseRule(
        id=PoseId(id="pose-2"),
        feature=Angle.LEFT_SHOULDER_ANGLE,
        operator=">",
        value=15.0,
        message="left shoulder too high",
    )
    result = PoseMatchResult(
        pose=_make_pose("pose-1"),
        deviations={Angle.LEFT_SHOULDER_ANGLE: 20.0},
    )

    assert strategy.validate(rule, result) is False


def test_validate_returns_true_for_matching_pose_when_gt_condition_is_met() -> None:
    strategy = PoseRuleStrategy()
    rule = PoseRule(
        id=PoseId(id="pose-1"),
        feature=Angle.LEFT_SHOULDER_ANGLE,
        operator=">",
        value=15.0,
        message="left shoulder too high",
    )
    result = PoseMatchResult(
        pose=_make_pose("pose-1"),
        deviations={Angle.LEFT_SHOULDER_ANGLE: 20.0},
    )

    assert strategy.validate(rule, result) is True


def test_validate_returns_false_for_matching_pose_when_condition_is_not_met() -> None:
    strategy = PoseRuleStrategy()
    rule = PoseRule(
        id=PoseId(id="pose-1"),
        feature=Angle.LEFT_SHOULDER_ANGLE,
        operator=">",
        value=15.0,
        message="left shoulder too high",
    )
    result = PoseMatchResult(
        pose=_make_pose("pose-1"),
        deviations={Angle.LEFT_SHOULDER_ANGLE: 14.9},
    )

    assert strategy.validate(rule, result) is False


def test_validate_uses_zero_deviation_when_feature_missing_for_lt_rule() -> None:
    strategy = PoseRuleStrategy()
    rule = PoseRule(
        id=PoseId(id="pose-1"),
        feature=Angle.RIGHT_ELBOW_ANGLE,
        operator="<",
        value=1.0,
        message="right elbow too low",
    )
    result = PoseMatchResult(
        pose=_make_pose("pose-1"),
        deviations={Angle.LEFT_SHOULDER_ANGLE: 20.0},
    )

    assert strategy.validate(rule, result) is True


def test_validate_uses_zero_deviation_when_feature_missing_for_gt_rule() -> None:
    strategy = PoseRuleStrategy()
    rule = PoseRule(
        id=PoseId(id="pose-1"),
        feature=Angle.RIGHT_ELBOW_ANGLE,
        operator=">",
        value=0.0,
        message="right elbow too high",
    )
    result = PoseMatchResult(
        pose=_make_pose("pose-1"),
        deviations={Angle.LEFT_SHOULDER_ANGLE: 20.0},
    )

    assert strategy.validate(rule, result) is False
