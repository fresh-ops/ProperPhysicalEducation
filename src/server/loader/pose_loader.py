from typing import List
from model.pose import Pose
from pathlib import Path
import json


class PoseLoader:
    """
    Загрузчик поз из JSON файлов
    """
    

    def __init__(self, directory_path: str = '.'):
        """
        Инициализация загрузчика поз
        
        Args:
            directory_path (str): путь к директории с позами
        """
        self.directory_path = Path(directory_path)
        if not self.directory_path.is_dir():
            raise ValueError(f"'{directory_path}' is not a valid directory.")
    

    def load_poses(self) -> List[Pose]:
        """
        Загружает все позы в формате JSON из директории и десериализует их. 
        Если поза не может быть загружена, файл игнорируется
        
        Returns:
            List[Pose]: список считанных поз
        """
        poses = []
        
        for json_file in self.directory_path.glob("*.json"):
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
    