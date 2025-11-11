class_name ModelProvider
extends Node

signal download_started(request: HTTPRequest)
signal download_ended

func get_external_model(path: String) -> FileAccess:
	var file := Global.get_model(path)
	if file != null:
		return file
	var request = Global.get_external_model(path, _downloaded)
	if request != null:
		download_started.emit(request)
	return null

func _downloaded():
	download_ended.emit()
