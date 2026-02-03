class_name LandmarksProvider
extends Node


signal landmarks_detected(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, timestamp_ms: int)
signal landmarks_sended(camera_feed: CameraFeed, result: MediaPipePoseLandmarkerResult, timestamp_ms: int)

const TASK_FILEPATH := "pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"


var __camera_controller: CameraController

var __landmarker: MediaPipePoseLandmarker
var __model_provider: ModelProvider
var __running_mode := MediaPipeVisionTask.RUNNING_MODE_LIVE_STREAM
var __delegate := MediaPipeTaskBaseOptions.DELEGATE_CPU


func initialize(camera_controller: CameraController) -> void:
	__camera_controller = camera_controller
	_initialize_task()


func _initialize_task() -> void:
	__model_provider = ModelProvider.new()
	var file := __model_provider.load_model(TASK_FILEPATH)
	if file == null:
		return
	var base_options := MediaPipeTaskBaseOptions.new()
	base_options.delegate = __delegate
	base_options.model_asset_buffer = file.get_buffer(file.get_length())
	__landmarker = MediaPipePoseLandmarker.new()
	__landmarker.initialize(base_options, __running_mode)
	__landmarker.result_callback.connect(self.__on_landmarks_detected)


func get_camera_feed_id() -> int:
	if __camera_controller == null:
		return -1
	return __camera_controller.get_feed_id()


## Активирует камеру и настраивает формат
func activate() -> void:
	if __camera_controller == null:
		push_error("LandmarksProvider: Cannot activate, CameraController is null")
		return
	__camera_controller.frame_changed.connect(self.__mark_image, ConnectFlags.CONNECT_DEFERRED)
	__camera_controller.start.call_deferred()

## Останавливает камеру 
func deactivate() -> void:
	if __camera_controller == null:
		return
	if __camera_controller.frame_changed.is_connected(self.__mark_image):
		__camera_controller.frame_changed.disconnect(self.__mark_image)
	__camera_controller.stop()


## Обрабатывает изображение используя MediaPipe (определяет landmarks)
func __mark_image(base_image: Image) -> void:
	base_image.convert(Image.FORMAT_RGB8)
	var image := MediaPipeImage.new()
	image.set_image(base_image)
	if image.is_gpu_image():
		image.convert_to_cpu()
	__landmarker.detect_async(image, Time.get_ticks_msec())


## Callback когда landmarks определены
func __on_landmarks_detected(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, timestamp_ms: int) -> void:
	landmarks_sended.emit.call_deferred(get_camera_feed_id(), result, timestamp_ms)
	landmarks_detected.emit.call_deferred(result, image, timestamp_ms)
