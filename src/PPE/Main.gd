extends Control

var tasks_vision := {
	"Pose Landmarker": "res://vision/pose_landmarker/PoseLandmarker.tscn",
}

func _ready() -> void:
	call_deferred("_select_task")

func _select_task() -> void:
	get_tree().change_scene_to_file(tasks_vision["Pose Landmarker"])
