class_name CameraView
extends Control


signal frame_updated(image: Image)

var _landmarksProvider: LandmarksProvider
var renderer: MediaPipePoseRenderer


@onready var _frame_view: TextureRect = $FrameView


func _ready() -> void:
	_landmarksProvider = LandmarksProvider.new()
	add_child(_landmarksProvider)


func initialize(camera_feed: CameraFeed) -> void:
	_landmarksProvider.initialize(camera_feed)
	_landmarksProvider.landmarks_detected.connect(self._draw_landmarks)
	renderer = MediaPipePoseRenderer.new()


func _exit_tree() -> void:
	stop_camera()


func start_camera() -> void:
	_landmarksProvider.activate.call_deferred()


func stop_camera() -> void:
	_landmarksProvider.deactivate()


func _draw_landmarks(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, _timestamp_ms: int) -> void:
	var output_image := renderer.render(image, result.pose_landmarks)
	_update_frame(output_image.image)


func _update_frame(image: Image) -> void:
	image.convert(Image.FORMAT_RGB8)
	if Vector2i(_frame_view.texture.get_size()) == image.get_size():
		_frame_view.texture.call_deferred("update", image)
	else:
		var new_texture := ImageTexture.create_from_image(image)
		_frame_view.set_deferred("texture", new_texture)
	frame_updated.emit(image)
