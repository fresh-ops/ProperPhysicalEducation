import json
from pathlib import Path

from analyzer.pose.skeleton_transformer import skeleton_transformer

DATA_DIR = Path(__file__).parent.parent / "data" / "points"


def create_pose_from_points(name: str):
    with open(DATA_DIR / f"{name}.json") as f:
        points = json.load(f)["points"]

    return skeleton_transformer.landmarks_to_pose(points)