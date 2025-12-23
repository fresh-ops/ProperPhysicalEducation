class_name LandmarksProvider
extends Node


signal landmarks_detected(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, timestamp_ms: int)
signal landmarks_sended(camera_feed: CameraFeed, result: MediaPipePoseLandmarkerResult, timestamp_ms: int)

const TASK_FILEPATH := "pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"


var __camera_feed: CameraFeed
var __camera_viewport: SubViewport
var __camera_texture: TextureRect

var __landmarker: MediaPipePoseLandmarker
var __model_provider: ModelProvider
var __running_mode := MediaPipeVisionTask.RUNNING_MODE_LIVE_STREAM
var __delegate := MediaPipeTaskBaseOptions.DELEGATE_CPU


func _ready() -> void:
	__camera_viewport = SubViewport.new()
	__camera_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(__camera_viewport)
	__camera_texture = TextureRect.new()
	__camera_viewport.add_child(__camera_texture)


func initialize(camera_feed: CameraFeed) -> void:
	__camera_feed = camera_feed
	_initialize_task()


func _initialize_task():
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
	return __camera_feed.get_id()


## Активирует камеру и настраивает формат
func activate() -> void:
	if __camera_feed == null:
		return
	if __camera_feed.get_position() == CameraFeed.FEED_BACK:
		__camera_texture.flip_h = false
	else:
		__camera_texture.flip_h = true
	__camera_feed.format_changed.connect(self._on_format_changed, ConnectFlags.CONNECT_DEFERRED)
	__camera_feed.frame_changed.connect(self._on_frame_changed, ConnectFlags.CONNECT_DEFERRED)
	__camera_feed.feed_is_active = true
	_on_format_changed()


## Останавливает камеру 
func deactivate() -> void:
	if __camera_feed == null:
		return
	__camera_feed.feed_is_active = false
	if __camera_feed.format_changed.is_connected(self._on_format_changed):
		__camera_feed.format_changed.disconnect(self._on_format_changed)
	if __camera_feed.frame_changed.is_connected(self._on_frame_changed):
		__camera_feed.frame_changed.disconnect(self._on_frame_changed)


## Настраивает формат камеры и шейдеры
func _on_format_changed() -> void:
	if __camera_feed == null:
		return
	var frame_size := Vector2i.ZERO
	match __camera_feed.get_datatype():
		CameraFeed.FEED_RGB:
			var texture_rgb := CameraTexture.new()
			texture_rgb.camera_feed_id = __camera_feed.get_id()
			texture_rgb.which_feed = CameraServer.FEED_RGBA_IMAGE
			frame_size = texture_rgb.get_size()
			__camera_texture.material = null
			__camera_texture.texture = texture_rgb
		CameraFeed.FEED_YCBCR:
			var texture_yuy2 := CameraTexture.new()
			texture_yuy2.camera_feed_id = __camera_feed.get_id()
			texture_yuy2.which_feed = CameraServer.FEED_YCBCR_IMAGE
			frame_size = texture_yuy2.get_size()
			var mat := ShaderMaterial.new()
			mat.shader = load("res://vision/yuy2_to_rgb.gdshader")
			mat.set_shader_parameter("texture_yuy2", texture_yuy2)
			__camera_texture.material = mat
			var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
			var image_texture := ImageTexture.new()
			image_texture.set_image(image)
			__camera_texture.texture = image_texture
		CameraFeed.FEED_YCBCR_SEP:
			var texture_y := CameraTexture.new()
			var texture_uv := CameraTexture.new()
			texture_y.camera_feed_id = __camera_feed.get_id()
			texture_uv.camera_feed_id = __camera_feed.get_id()
			texture_y.which_feed = CameraServer.FEED_Y_IMAGE
			texture_uv.which_feed = CameraServer.FEED_CBCR_IMAGE
			var mat := ShaderMaterial.new()
			mat.shader = load("res://vision/yuv420_to_rgb.gdshader")
			mat.set_shader_parameter("texture_y", texture_y)
			mat.set_shader_parameter("texture_uv", texture_uv)
			__camera_texture.material = mat
			frame_size = texture_y.get_size()
			var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
			var image_texture := ImageTexture.new()
			image_texture.set_image(image)
			__camera_texture.texture = image_texture
		_:
			return
	var feed_rotation: float = __camera_feed.feed_transform.get_rotation()
	if __camera_texture.flip_h:
		feed_rotation *= -1
	var size_rotated := Vector2(frame_size).rotated(feed_rotation)
	var offset := Vector2(min(size_rotated.x, 0), min(size_rotated.y, 0))
	__camera_texture.rotation = feed_rotation
	__camera_texture.position = offset * -1
	__camera_viewport.size = frame_size


## Обрабатывает кадр с камеры 
func _on_frame_changed() -> void:
	if __camera_texture == null:
		return
	await RenderingServer.frame_post_draw
	if __camera_viewport == null:
		return
	var texture := __camera_viewport.get_texture()
	if texture == null:
		return
	var image = texture.get_image()
	if image == null:
		return
	__mark_image(image)


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
	landmarks_sended.emit.call_deferred(__camera_feed.get_id(), result, timestamp_ms)
	landmarks_detected.emit.call_deferred(result, image, timestamp_ms)
