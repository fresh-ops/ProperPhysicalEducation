extends Control

var tasks := {
	"Vision Task": "res://vision/VisionTask.tscn",
}

func _ready() -> void:
	call_deferred("_select_task")

func _select_task() -> void:
	get_tree().change_scene_to_file(tasks["Vision Task"])
