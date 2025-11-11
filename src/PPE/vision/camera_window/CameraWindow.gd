class_name CameraWindow
extends Control

var camera_feed: CameraFeed
var landmarks_provider: LandmarksProvider
var renderer: MediaPipePoseRenderer

@onready var camera_viewport: SubViewport = $SubViewportContainer/CameraViewport
@onready var image_view: TextureRect = $SubViewportContainer/CameraViewport/Image
@onready var camera_viewport_container: SubViewportContainer = $SubViewportContainer


func init_camera(feed: CameraFeed) -> void:
	camera_feed = feed
	landmarks_provider = LandmarksProvider.new()
	renderer = MediaPipePoseRenderer.new()
	landmarks_provider.init(feed)
	landmarks_provider.set_texture.connect(_set_texture)
	landmarks_provider.landmarks_provided.connect(_show_landmarks)
	
func _set_texture(view: TextureRect, size_rotated: Vector2):
	image_view.flip_h = view.flip_h
	image_view.rotation = view.rotation
	image_view.position = view.position
	camera_viewport.size = view.size
	#image_view.material = view.material
	self.custom_minimum_size = Vector2(abs(size_rotated.x), abs(size_rotated.y))
	get_parent().queue_sort()

func _show_landmarks(landmarks: MediaPipePoseLandmarkerResult, image: MediaPipeImage, _timestamp_ms: int):
	var output_image := renderer.render(image, landmarks.pose_landmarks)
	_update_texture.call_deferred(output_image.image)
	
func _update_texture(image: Image) -> void:
	image.convert(Image.FORMAT_RGBA8)
	var new_texture := ImageTexture.create_from_image(image)
	image_view.set_deferred("texture", new_texture)
