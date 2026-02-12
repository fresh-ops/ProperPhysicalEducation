extends Node


const MODEL_DIR := "user://GDMP"
const TASK_FILEPATH := "pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
const RUNNING_MODE := MediaPipeVisionTask.RUNNING_MODE_LIVE_STREAM
const DELEGATE := MediaPipeTaskBaseOptions.DELEGATE_CPU


var __base_options: MediaPipeTaskBaseOptions


func setup_model() -> MediaPipePoseLandmarker:
	__setup_base_options()
	var landmarker := MediaPipePoseLandmarker.new()
	landmarker.initialize(__base_options, RUNNING_MODE)
	return landmarker


func __setup_base_options() -> void:
	var file := __load_model(TASK_FILEPATH)
	if file == null:
		push_error("Model file could not be loaded.")
		return
	__base_options = MediaPipeTaskBaseOptions.new()
	__base_options.delegate = DELEGATE
	__base_options.model_asset_buffer = file.get_buffer(file.get_length())


func __load_model(path: String) -> FileAccess:
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
	push_error("Failed to get external model.")
	return null


func __get_local_model(path: String) -> FileAccess:
	var model_path := MODEL_DIR.path_join(path)
	if FileAccess.file_exists(model_path):
		return FileAccess.open(model_path, FileAccess.READ)
	return null
