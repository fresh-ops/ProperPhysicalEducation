## Класс для детектирования landmarks позы с помощью MediaPipe.
## Управляет инициализацией модели и обработкой кадров от камеры.
class_name LandmarksProvider
extends Node

## Посылается, когда landmarks успешно обнаружены.[br]
## [param camera_feed] - идентификатор видеопотока.[br]
## [param result] - результат детектирования с информацией о landmarks.[br]
## [param image] - обработанное изображение.[br]
## [param timestamp_ms] - метка времени в миллисекундах.
signal landmarks_detected(camera_feed: CameraFeed, result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, timestamp_ms: int)


var __camera_controller: CameraController
var __landmarker: MediaPipePoseLandmarker
  
  
func initialize(camera_controller: CameraController) -> void:
	__camera_controller = camera_controller
	if not _initialize_landmarker():
		push_error("LandmarksProvider: Failed to initialize landmarker model")
		return


## Инициализирует модель MediaPipe для детектирования landmarks.
## Возвращает [code]true[/code], если модель успешно загружена.
func _initialize_landmarker() -> bool:
	__landmarker = ModelProvider.setup_model()
	if __landmarker == null:
		push_error("LandmarksProvider: Failed to setup MediaPipe model")
		return false

	__landmarker.result_callback.connect(self.__on_landmarks_detected)
	return true


## Получает идентификатор текущего видеопотока.
## Возвращает -1, если контроллер камеры не установлен.
func get_camera_feed_id() -> int:
	if __camera_controller == null:
		return -1
	return __camera_controller.get_feed_id()


## Активирует камеру и начинает обработку кадров для детектирования landmarks.
func activate() -> void:
	if __camera_controller == null:
		push_error("LandmarksProvider: Cannot activate, CameraController is null")
		return
	
	if not __camera_controller.frame_changed.is_connected(self.__mark_image):
		__camera_controller.frame_changed.connect(self.__mark_image, ConnectFlags.CONNECT_DEFERRED)
	
	if not __camera_controller.start():
		push_error("LandmarksProvider: Failed to start camera controller")
		return


## Деактивирует камеру и прекращает обработку кадров.
func deactivate() -> void:
	if __camera_controller == null:
		return
	
	if __camera_controller.frame_changed.is_connected(self.__mark_image):
		__camera_controller.frame_changed.disconnect(self.__mark_image)
	
	__camera_controller.stop()


## Обрабатывает изображение с помощью MediaPipe для детектирования landmarks.
## Преобразует изображение в RGB8 формат и отправляет на асинхронную обработку.
func __mark_image(base_image: Image) -> void:
	if base_image == null:
		push_error("LandmarksProvider: Received null image for processing")
		return
	
	base_image.convert(Image.FORMAT_RGB8)
	var image := MediaPipeImage.new()
	image.set_image(base_image)
	if image.is_gpu_image():
		image.convert_to_cpu()
	__landmarker.detect_async(image, Time.get_ticks_msec())


## Обработчик события завершения детектирования landmarks.
## Излучает сигнал landmarks_detected с результатом обработки.
func __on_landmarks_detected(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, timestamp_ms: int) -> void:
	if result == null:
		push_warning("LandmarksProvider: Received null result from landmarker")
		return
	
	if image == null:
		push_warning("LandmarksProvider: Received null image from landmarker")
		return
	
	landmarks_detected.emit.call_deferred(get_camera_feed_id(), result, image, timestamp_ms)
