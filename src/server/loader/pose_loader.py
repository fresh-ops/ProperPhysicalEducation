from model.pose import Pose
from pathlib import Path
import json


class PoseLoader:
    """
    Загрузчик поз из JSON файлов
    """


    def __init__(self, directory_path: str = '.'):
        """
        Инициализирует загрузчик поз.

        Args:
            directory_path (str): путь к директории с позами

        Raises:
            ValueError: если путь не является валидной директорией
        """
        self.directory = Path(directory_path)
        if not self.directory.is_dir():
            raise ValueError(f"'{directory_path}' is not a valid directory.")


    def load_pose(self, pose_id: int) -> Pose:
        """
        Загружает позу в формате JSON из директории и десериализует её.

        Args:
            pose_id (int): ID позы для загрузки.

        Returns:
            Pose: загруженная поза
        """

        for json_file in self.directory.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    serialized_pose = json.load(f)
                    if serialized_pose["id"] == pose_id:
                        return Pose(**serialized_pose)

            except TypeError as e:
                print(f"Field mismatch in {json_file}: {e}")
            except json.JSONDecodeError as e:
                print(f"Invalid JSON in {json_file}: {e}")
            except Exception as e:
                print(f"Error reading {json_file}: {e}")

        raise ValueError(f"Pose with id {pose_id} not found in directory '{self.directory}'")