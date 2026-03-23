import json
from pathlib import Path
from typing import TypedDict, cast
from analyzer.pose.skeleton_transformer.skeleton import Angle
from loader.pose_loader import PoseLoader
from model.exercise import Exercise
from model.rule import Rule


class SerializedRule(TypedDict):
    pose_name: str
    feature: str
    operator: str
    value: float
    message: str


class SerializedExercise(TypedDict):
    id: int
    name: str
    poses: list[int]
    rules: list[SerializedRule]


class ExerciseLoader:
    """
    Загрузчик упражнений из JSON файлов
    """

    def __init__(self, pose_loader: PoseLoader, directory_path: str = "."):
        """
        Инициализирует загрузчик упражнений.

        Args:
            pose_loader (PoseLoader): загрузчик поз для получения поз по ID
            directory_path (str): путь к директории с упражнениями

        Raises:
            ValueError: если путь не является валидной директорией
        """
        self.pose_loader = pose_loader
        self.directory = Path(directory_path)
        if not self.directory.is_dir():
            raise ValueError(f"'{directory_path}' is not a valid directory.")

    def load_exercise(self, exercise_id: int) -> Exercise:
        """
        Загружает упражнение в формате JSON из директории и десериализует его.

        Args:
            exercise_id (int): ID упражнения для загрузки.

        Returns:
            Exercise: загруженное упражнение
        """

        for json_file in self.directory.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    serialized_exercise = cast(SerializedExercise, json.load(f))
                    if serialized_exercise["id"] == exercise_id:
                        return self.__deserialize_exercise(serialized_exercise)

            except TypeError as e:
                print(f"Field mismatch in {json_file}: {e}")
            except json.JSONDecodeError as e:
                print(f"Invalid JSON in {json_file}: {e}")
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
        raise ValueError(
            f"Exercise with id {exercise_id} not found in directory '{self.directory}'"
        )

    def __deserialize_exercise(
        self, serialized_exercise: SerializedExercise
    ) -> Exercise:
        """
        Десериализует упражнение из словаря, загруженного из JSON.

        Args:
            serialized_exercise (dict): словарь с данными упражнения

        Returns:
            Exercise: десериализованное упражнение
        """
        loaded_poses = [
            self.pose_loader.load_pose(id) for id in serialized_exercise["poses"]
        ]

        rules = self.__deserialize_rules(serialized_exercise["rules"])

        return Exercise(
            id=serialized_exercise["id"],
            name=serialized_exercise["name"],
            poses=loaded_poses,
            rules=rules,
        )

    def __deserialize_rules(self, serialized_rules: list[SerializedRule]) -> list[Rule]:
        rules = []

        for rule in serialized_rules:
            rules.append(
                Rule(
                    pose_name=rule["pose_name"],
                    feature=Angle[rule["feature"]],
                    operator=rule["operator"],
                    value=rule["value"],
                    message=rule["message"],
                )
            )

        return rules
