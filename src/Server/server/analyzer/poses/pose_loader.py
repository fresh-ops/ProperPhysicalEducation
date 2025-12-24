from typing import List
from analyzer.poses.pose import Pose
from pathlib import Path
import json


def load_poses(directory_path = '.') -> List[Pose]:
    """
        Загружает все позы в формате JSON в данной директории и десериализует их. Если поза не может быть загружена файл игнорируется

        Args:
            directory_path (str): путь к директории с позами

        Returns:
            List[Pose]: список считанных поз
    """
    poses = []
    directory = Path(directory_path)
    if not directory.is_dir():
        raise ValueError(f"'{directory_path}' is not a valid directory.")

    for json_file in directory.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                serialized_pose = json.load(f)
                pose = Pose(**serialized_pose)

                poses.append(pose)
        except TypeError as e:
            print(f"Field mismatch in {json_file}: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in {json_file}: {e}")
        except Exception as e:
            print(f"Error reading {json_file}: {e}")

    return poses

