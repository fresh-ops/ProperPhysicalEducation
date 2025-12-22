import json
import os
from typing import List, Dict, Optional
from poses.pose import Pose
from poses.pose_loader import load_poses
from AngleAnalyzer import AngleAnalyzer

class PoseDetector:
    def __init__(self, poses_directory: str = '.'):
        """
        Инициализация детектора поз
        
        Args:
            poses_directory: Путь к директории с JSON файлами эталонных поз
        """
        self.poses = load_poses(poses_directory)
        self.last_detected_pose = None

        self.POSE_IDS = {
            "UNKNOWN": -1,
            "T_POSE": 0,
            "ARMS_DOWN": 1
        }

    def calculate_deviations(self, current_angles: List[float], target_angles: List[float]) -> List[float]:
        """
        Вычисляет абсолютные отклонения текущих углов от целевых
        
        Args:
            current_angles: Текущие углы [6 значений]
            target_angles: Целевые углы [6 значений]
            
        Returns:
            List[float]: Абсолютные отклонения
        """
        if len(current_angles) != 6 or len(target_angles) != 6:
            return [0.0] * 6
            
        deviations = []
        for curr, target in zip(current_angles, target_angles):
            deviations.append(abs(curr - target))
        return deviations

    def calculate_adjustments(self, current_angles: List[float], target_angles: List[float]) -> List[float]:
        """
        Вычисляет необходимые корректировки со знаками
        
        Args:
            current_angles: Текущие углы [6 значений]
            target_angles: Целевые углы [6 значений]
            
        Returns:
            List[float]: Корректировки (положительные - увеличить, отрицательные - уменьшить)
        """
        if len(current_angles) != 6 or len(target_angles) != 6:
            return [0.0] * 6
            
        adjustments = []
        for curr, target in zip(current_angles, target_angles):
            adjustments.append(target - curr)
        return adjustments

    def check_pose(self, current_angles: List[float], pose: Pose) -> Dict:
        """
        Проверяет, соответствует ли текущая поза эталонной
        
        Args:
            current_angles: Текущие углы [левое_плечо, правое_плечо, 
                                         левый_локоть, правый_локоть,
                                         левое_колено, правое_колено]
            pose: Эталонная поза для сравнения
            
        Returns:
            Dict: Результат проверки
        """
        if len(current_angles) != 6:
            return {
                'is_correct': False,
                'reason': 'Неверное количество углов',
                'deviations': [0.0] * 6,
                'adjustments': [0.0] * 6
            }
        
        target_angles = [
            pose.left_shoulder_angle,
            pose.right_shoulder_angle,
            pose.left_elbow_angle,
            pose.right_elbow_angle,
            pose.left_knee_angle,
            pose.right_knee_angle
        ]
        
        deviations = self.calculate_deviations(current_angles, target_angles)
        adjustments = self.calculate_adjustments(current_angles, target_angles)
        
        is_correct = True
        failed_joints = []
        
        joint_names = [
            "левое плечо", "правое плечо",
            "левый локоть", "правый локоть",
            "левое колено", "правое колено"
        ]
        
        for i, deviation in enumerate(deviations):
            if deviation > pose.threshold:
                is_correct = False
                failed_joints.append(joint_names[i])
        
        reason = ""
        if not is_correct and failed_joints:
            reason = f"Не выполнено: {', '.join(failed_joints)}"
        
        return {
            'is_correct': is_correct,
            'reason': reason,
            'deviations': deviations,
            'adjustments': adjustments,
            'target_angles': target_angles
        }

    def detect_pose(self, angle_analyzer) -> Dict:
        """
        Определяет текущую позу на основе углов из AngleAnalyzer
        
        Args:
            angle_analyzer: Экземпляр AngleAnalyzer с вычисленными углами
            
        Returns:
            Dict: Данные позы в формате массива
        """
        specific_angles = angle_analyzer.get_specific_angles()
        
        if not specific_angles:
            return {
                'pose_id': self.POSE_IDS["UNKNOWN"],
                'pose_name': 'Неопределённая поза',
                'angles': [0.0] * 6,
                'deviations': [0.0] * 6,
                'log': {
                    'is_correct': False,
                    'needed_correction': []
                }
            }
        
        current_angles = [
            specific_angles.get('left_shoulder', {}).get('angle', 0),
            specific_angles.get('right_shoulder', {}).get('angle', 0),
            specific_angles.get('left_elbow', {}).get('angle', 0),
            specific_angles.get('right_elbow', {}).get('angle', 0),
            specific_angles.get('left_knee', {}).get('angle', 0),
            specific_angles.get('right_knee', {}).get('angle', 0)
        ]
        
        detected_pose = None
        best_match = None
        min_total_deviation = float('inf')
        
        for pose in self.poses:
            result = self.check_pose(current_angles, pose)
            
            if result['is_correct']:
                total_deviation = sum(result['deviations'])
                
                if total_deviation < min_total_deviation:
                    min_total_deviation = total_deviation
                    detected_pose = pose
                    best_match = result
        
        if detected_pose:
            pose_id = self.POSE_IDS["UNKNOWN"]
            if detected_pose.name.lower() == "t_pose":
                pose_id = self.POSE_IDS["T_POSE"]
            elif detected_pose.name.lower() == "arms_down":
                pose_id = self.POSE_IDS["ARMS_DOWN"]
            
            adjustments = best_match['adjustments']
            needed_correction = []
            for adj in adjustments:
                if abs(adj) > 0.1:
                    needed_correction.append(round(adj, 1))
                else:
                    needed_correction.append(0.0)
            
            pose_data = {
                'pose_id': pose_id,
                'pose_name': detected_pose.name,
                'angles': current_angles,
                'deviations': best_match['deviations'],
                'log': {
                    'is_correct': True,
                    'needed_correction': needed_correction
                }
            }
            
            self.last_detected_pose = detected_pose.name
            return pose_data
        
        adjustment_array = []
        for i in range(6):
            adjustment_array.append(0.0)
        
        return {
            'pose_id': self.POSE_IDS["UNKNOWN"],
            'pose_name': 'Неопределённая поза',
            'angles': current_angles,
            'deviations': [0.0] * 6,
            'log': {
                'is_correct': False,
                'needed_correction': adjustment_array
            }
        }

    def get_pose_name_by_id(self, pose_id: int) -> str:
        """
        Возвращает название позы по ID для обратной совместимости
        
        Args:
            pose_id: ID позы
            
        Returns:
            str: Название позы
        """
        for name, pid in self.POSE_IDS.items():
            if pid == pose_id:
                if name == "T_POSE":
                    return "Т-поза"
                elif name == "ARMS_DOWN":
                    return "Руки по швам"
        return "Неопределённая поза"