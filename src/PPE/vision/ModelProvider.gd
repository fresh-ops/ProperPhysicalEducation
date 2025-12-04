class_name ModelProvider
extends Node


const MODEL_DIR := "user://GDMP"


func load_model(path: String) -> FileAccess:
	var file := __get_local_model(path)
	if file != null:
		return file
	__get_external_model(path, self._initialize_task)
	return null
	
	
func __get_external_model(path: String, callback: Callable) -> HTTPRequest:
	var request = MediaPipeExternalFiles.get_model(path)
	if request != null:
		var save_path := MODEL_DIR.path_join(path)
		var request_callback = Global._get_external_file.bind(save_path, callback)
		request.request_completed.connect(request_callback)
		return request
	return null


func __get_local_model(path: String) -> FileAccess:
	var model_path := MODEL_DIR.path_join(path)
	if FileAccess.file_exists(model_path):
		return FileAccess.open(model_path, FileAccess.READ)
	return null
