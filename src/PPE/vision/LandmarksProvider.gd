class_name LandmarksProvider
extends Node

signal landmarks_provided(landmarks: MediaPipePoseLandmarkerResult, image: MediaPipeImage, _timestamp_ms: int)
signal set_texture(image_view: TextureRect, size_rotated: Vector2)

var task: MediaPipePoseLandmarker
var task_file := "pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
var running_mode := MediaPipeVisionTask.RUNNING_MODE_LIVE_STREAM
var delegate := MediaPipeTaskBaseOptions.DELEGATE_CPU
var model_provider: ModelProvider
var camera_feed: CameraFeed

var image_view: TextureRect 
var camera_viewport: SubViewport

func init(feed: CameraFeed):
	camera_feed = feed
	if OS.get_name() not in "MacOS":
		camera_feed.set_format(0, {})
		
	model_provider = ModelProvider.new()
	var file := model_provider.get_external_model(task_file)
	if file == null:
		return
	var base_options := MediaPipeTaskBaseOptions.new()
	base_options.delegate = delegate
	base_options.model_asset_buffer = file.get_buffer(file.get_length())
	task = MediaPipePoseLandmarker.new()
	task.initialize(base_options, running_mode)
	task.result_callback.connect(self._result_callback)
	camera_feed.feed_is_active = true
	camera_feed.format_changed.connect(self._camera_format_changed, ConnectFlags.CONNECT_DEFERRED)
	camera_feed.frame_changed.connect(self._camera_frame_changed, ConnectFlags.CONNECT_DEFERRED)

func _camera_format_changed() -> void:
	if camera_feed == null:
		return
	if camera_viewport:
		camera_viewport.queue_free()
	if image_view:
		image_view.queue_free()
	image_view = TextureRect.new()
	#camera_viewport = SubViewport.new()
	#camera_viewport.add_child(image_view)
	#add_child(camera_viewport)
	image_view.flip_h = camera_feed.get_position() != CameraFeed.FEED_BACK
	var frame_size := Vector2i.ZERO
	match camera_feed.get_datatype():
		CameraFeed.FEED_RGB:
			var texture_rgb := CameraTexture.new()
			texture_rgb.camera_feed_id = camera_feed.get_id()
			texture_rgb.which_feed = CameraServer.FEED_RGBA_IMAGE
			frame_size = texture_rgb.get_size()
			image_view.material = null
			image_view.texture = texture_rgb
		CameraFeed.FEED_YCBCR:
			var texture_yuy2 := CameraTexture.new()
			texture_yuy2.camera_feed_id = camera_feed.get_id()
			texture_yuy2.which_feed = CameraServer.FEED_YCBCR_IMAGE
			frame_size = texture_yuy2.get_size()
			var mat := ShaderMaterial.new()
			mat.shader = load("res://vision/yuy2_to_rgb.gdshader")
			mat.set_shader_parameter("texture_yuy2", texture_yuy2)
			image_view.material = mat
			var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
			var image_texture := ImageTexture.new()
			image_texture.set_image(image)
			image_view.texture = image_texture
		CameraFeed.FEED_YCBCR_SEP:
			var texture_y := CameraTexture.new()
			var texture_uv := CameraTexture.new()
			texture_y.camera_feed_id = camera_feed.get_id()
			texture_uv.camera_feed_id = camera_feed.get_id()
			texture_y.which_feed = CameraServer.FEED_Y_IMAGE
			texture_uv.which_feed = CameraServer.FEED_CBCR_IMAGE
			var mat := ShaderMaterial.new()
			mat.shader = load("res://vision/yuv420_to_rgb.gdshader")
			mat.set_shader_parameter("texture_y", texture_y)
			mat.set_shader_parameter("texture_uv", texture_uv)
			image_view.material = mat
			frame_size = texture_y.get_size()
			var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
			var image_texture := ImageTexture.new()
			image_texture.set_image(image)
			image_view.texture = image_texture
		_:
			return
	var feed_rotation: float = camera_feed.feed_transform.get_rotation()
	if image_view.flip_h:
		feed_rotation *= -1
	var size_rotated := Vector2(frame_size).rotated(feed_rotation)
	var offset := Vector2(min(size_rotated.x, 0), min(size_rotated.y, 0))
	
	image_view.rotation = feed_rotation
	image_view.position = offset * -1
	#camera_viewport.size = frame_size
	#camera_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	#camera_viewport.transparent_bg = true
	set_texture.emit(image_view, size_rotated)
	
func _camera_frame_changed() -> void:
	if image_view == null:
		return
	await RenderingServer.frame_post_draw
	#if camera_viewport == null:
		#return
	#var texture := camera_viewport.get_texture()
	#if texture == null:
		#return
	var image = image_view.texture.get_image()
	if image == null:
		return
	image.convert(Image.FORMAT_RGB8)
	var img: = MediaPipeImage.new()
	img.set_image(image)
	if delegate == MediaPipeTaskBaseOptions.DELEGATE_CPU and img.is_gpu_image():
		img.convert_to_cpu()
	_process_camera(img, Time.get_ticks_msec())

func _result_callback(result: MediaPipePoseLandmarkerResult, image: MediaPipeImage, _timestamp_ms: int) -> void:
	landmarks_provided.emit(result, image, _timestamp_ms)

var last_timestamp: int = 0

func _process_camera(image: MediaPipeImage, timestamp_ms: int) -> void:
	if timestamp_ms <= last_timestamp:
		timestamp_ms = last_timestamp + 1 
	last_timestamp = timestamp_ms
	task.detect_async(image, timestamp_ms)
