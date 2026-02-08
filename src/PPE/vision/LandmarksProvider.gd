class_name LandmarksProvider
extends Node


signal landmarks_detected(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, timestamp_ms: int)
signal landmarks_sended(camera_feed: CameraFeed, result: MediaPipePoseLandmarkerResult, timestamp_ms: int)


var __camera_controller: CameraController


var __landmarker: MediaPipePoseLandmarker
  
  
func initialize(camera_controller: CameraController) -> void:
	__camera_controller = camera_controller
	_initialize_landmarker()


func _initialize_landmarker():
	__landmarker = ModelProvider.setup_model()
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
