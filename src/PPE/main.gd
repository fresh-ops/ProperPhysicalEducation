extends Control


var tasks_vision := {
	"Vision Task": "res://vision/vision_task.tscn",
}


func _ready() -> void:
	call_deferred("_select_task")


func _select_task() -> void:
	get_tree().change_scene_to_file(tasks_vision["Vision Task"])
