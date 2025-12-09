class_name CameraView
extends Control


signal frame_updated(image: Image)


var __landmarksProvider: LandmarksProvider
var __renderer: MediaPipePoseRenderer


@onready var __frame_view: TextureRect = $FrameView


func initialize(camera_feed: CameraFeed, landmarks_provider: LandmarksProvider) -> void:
	__landmarksProvider = landmarks_provider
	add_child(__landmarksProvider)
	__landmarksProvider.initialize(camera_feed)
	__landmarksProvider.landmarks_detected.connect(self._draw_landmarks)
	__renderer = MediaPipePoseRenderer.new()


func _exit_tree() -> void:
	stop_camera()


func start_camera() -> void:
	__landmarksProvider.activate.call_deferred()


func stop_camera() -> void:
	__landmarksProvider.deactivate()


## Отрисовывает landmarks на кадре
func _draw_landmarks(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, _timestamp_ms: int) -> void:
	var output_image := __renderer.render(image, result.pose_landmarks)
	_update_frame(output_image.image)


## Обновляет текстуру изображением с landmarks
func _update_frame(image: Image) -> void:
	image.convert(Image.FORMAT_RGB8)
	if Vector2i(__frame_view.texture.get_size()) == image.get_size():
		__frame_view.texture.call_deferred("update", image)
	else:
		var new_texture := ImageTexture.create_from_image(image)
		__frame_view.set_deferred("texture", new_texture)
	frame_updated.emit(image)
