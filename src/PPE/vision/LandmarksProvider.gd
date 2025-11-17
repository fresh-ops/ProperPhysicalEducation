class_name LandmarksProvider
extends Node


signal landmarks_detected(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, timestamp_ms: int)

var _camera_feed: CameraFeed
var _camera_viewport: SubViewport
var _camera_texture: TextureRect

const TASK_FILEPATH := "pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
var landmarker: MediaPipePoseLandmarker
var _model_provider: ModelProvider
var _running_mode := MediaPipeVisionTask.RUNNING_MODE_LIVE_STREAM
var _delegate := MediaPipeTaskBaseOptions.DELEGATE_CPU


func _ready() -> void:
	_camera_viewport = SubViewport.new()
	_camera_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(_camera_viewport)
	_camera_texture = TextureRect.new()
	_camera_viewport.add_child(_camera_texture)


func initialize(camera_feed: CameraFeed) -> void:
	_camera_feed = camera_feed
	_initialize_task()


func _initialize_task():
	_model_provider = ModelProvider.new()
	var file := _model_provider.load_model(TASK_FILEPATH)
	if file == null:
		return
	var base_options := MediaPipeTaskBaseOptions.new()
	base_options.delegate = _delegate
	base_options.model_asset_buffer = file.get_buffer(file.get_length())
	landmarker = MediaPipePoseLandmarker.new()
	landmarker.initialize(base_options, _running_mode)
	landmarker.result_callback.connect(self.on_landmarks_detected)


func activate() -> void:
	if _camera_feed == null:
		return
	if _camera_feed.get_position() == CameraFeed.FEED_BACK:
		_camera_texture.flip_h = false
	else:
		_camera_texture.flip_h = true
	_camera_feed.format_changed.connect(self._on_format_changed, ConnectFlags.CONNECT_DEFERRED)
	_camera_feed.frame_changed.connect(self._on_frame_changed, ConnectFlags.CONNECT_DEFERRED)
	_camera_feed.feed_is_active = true
	_on_format_changed()


func deactivate() -> void:
	if _camera_feed == null:
		return
	_camera_feed.feed_is_active = false
	if _camera_feed.format_changed.is_connected(self._on_format_changed):
		_camera_feed.format_changed.disconnect(self._on_format_changed)
	if _camera_feed.frame_changed.is_connected(self._on_frame_changed):
		_camera_feed.frame_changed.disconnect(self._on_frame_changed)


func _on_format_changed() -> void:
	if _camera_feed == null:
		return
	var frame_size := Vector2i.ZERO
	match _camera_feed.get_datatype():
		CameraFeed.FEED_RGB:
			var texture_rgb := CameraTexture.new()
			texture_rgb.camera_feed_id = _camera_feed.get_id()
			texture_rgb.which_feed = CameraServer.FEED_RGBA_IMAGE
			frame_size = texture_rgb.get_size()
			_camera_texture.material = null
			_camera_texture.texture = texture_rgb
		CameraFeed.FEED_YCBCR:
			var texture_yuy2 := CameraTexture.new()
			texture_yuy2.camera_feed_id = _camera_feed.get_id()
			texture_yuy2.which_feed = CameraServer.FEED_YCBCR_IMAGE
			frame_size = texture_yuy2.get_size()
			var mat := ShaderMaterial.new()
			mat.shader = load("res://vision/yuy2_to_rgb.gdshader")
			mat.set_shader_parameter("texture_yuy2", texture_yuy2)
			_camera_texture.material = mat
			var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
			var image_texture := ImageTexture.new()
			image_texture.set_image(image)
			_camera_texture.texture = image_texture
		CameraFeed.FEED_YCBCR_SEP:
			var texture_y := CameraTexture.new()
			var texture_uv := CameraTexture.new()
			texture_y.camera_feed_id = _camera_feed.get_id()
			texture_uv.camera_feed_id = _camera_feed.get_id()
			texture_y.which_feed = CameraServer.FEED_Y_IMAGE
			texture_uv.which_feed = CameraServer.FEED_CBCR_IMAGE
			var mat := ShaderMaterial.new()
			mat.shader = load("res://vision/yuv420_to_rgb.gdshader")
			mat.set_shader_parameter("texture_y", texture_y)
			mat.set_shader_parameter("texture_uv", texture_uv)
			_camera_texture.material = mat
			frame_size = texture_y.get_size()
			var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
			var image_texture := ImageTexture.new()
			image_texture.set_image(image)
			_camera_texture.texture = image_texture
		_:
			return
	var feed_rotation: float = _camera_feed.feed_transform.get_rotation()
	if _camera_texture.flip_h:
		feed_rotation *= -1
	var size_rotated := Vector2(frame_size).rotated(feed_rotation)
	var offset := Vector2(min(size_rotated.x, 0), min(size_rotated.y, 0))
	_camera_texture.rotation = feed_rotation
	_camera_texture.position = offset * -1
	_camera_viewport.size = frame_size


func _on_frame_changed() -> void:
	if _camera_texture == null:
		return
	await RenderingServer.frame_post_draw
	if _camera_viewport == null:
		return
	var texture := _camera_viewport.get_texture()
	if texture == null:
		return
	var image = texture.get_image()
	if image == null:
		return
	_mark_image(image)


func _mark_image(base_image: Image) -> void:
	base_image.convert(Image.FORMAT_RGB8)
	var image := MediaPipeImage.new()
	image.set_image(base_image)
	if image.is_gpu_image():
		image.convert_to_cpu()
	landmarker.detect_async(image, Time.get_ticks_msec())


func on_landmarks_detected(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, timestamp_ms: int) -> void:
	landmarks_detected.emit.call_deferred(result, image, timestamp_ms)
