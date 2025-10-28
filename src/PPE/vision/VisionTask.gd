class_name VisionTask
extends Control

var request: HTTPRequest
var running_mode := MediaPipeVisionTask.RUNNING_MODE_IMAGE
var delegate := MediaPipeTaskBaseOptions.DELEGATE_CPU
var camera_extension: CameraServerExtension
var camera_feed

@onready var progress_bar: ProgressBar = $VBoxContainer/ProgressBar
@onready var image_view: TextureRect = $VBoxContainer/Image
@onready var btn_open_camera: Button = $VBoxContainer/Buttons/OpenCamera
@onready var select_camera_dialog: ConfirmationDialog = $SelectCamera
@onready var opt_camera_feed: OptionButton = $SelectCamera/VBoxContainer/SelectFeed
@onready var opt_camera_format: OptionButton = $SelectCamera/VBoxContainer/SelectFormat
@onready var camera_viewport: SubViewport = $CameraViewport
@onready var camera_texture: TextureRect = $CameraViewport/TextureRect
@onready var permission_dialog: AcceptDialog = $PermissionDialog

func _exit_tree() -> void:
	if request:
		request.cancel_request()
		request = null
	camera_extension = null

func _ready():
	btn_open_camera.pressed.connect(self._open_camera)
	CameraServer.camera_feed_added.connect(self._camera_added)
	CameraServer.camera_feed_removed.connect(self._camera_removed)
	CameraServer.camera_feeds_updated.connect(self._camera_feeds_updated)
	if CameraServer.monitoring_feeds:
		_initialize_camera_extension()
		_update_camera_feeds()
	select_camera_dialog.get_ok_button().disabled = true
	opt_camera_feed.item_selected.connect(self._camera_selected)
	opt_camera_format.item_selected.connect(self._format_selected)
	select_camera_dialog.confirmed.connect(self._start_camera)
	_init_task()

func _process(_delta: float) -> void:
	if request:
		var max_size := request.get_body_size()
		var cur_size := request.get_downloaded_bytes()
		progress_bar.value = round(float(cur_size) / float(max_size) * 100)

func _reset() -> void:
	if camera_feed == null:
		return
	camera_feed.feed_is_active = false
	if camera_feed.format_changed.is_connected(self._camera_format_changed):
		camera_feed.format_changed.disconnect(self._camera_format_changed)
	if camera_feed.frame_changed.is_connected(self._camera_frame_changed):
		camera_feed.frame_changed.disconnect(self._camera_frame_changed)

func _back() -> void:
	_reset()
	Global.go_to_main_scene()

func _delegate_selected(index: int) -> void:
	_reset()
	delegate = index as MediaPipeTaskBaseOptions.Delegate
	_init_task()

func _get_external_file() -> void:
	progress_bar.hide()
	image_view.show()
	request = null
	_init_task()

func _init_task() -> void:
	btn_open_camera.disabled = false

func _load_image(path: String) -> void:
	if not running_mode == MediaPipeVisionTask.RUNNING_MODE_IMAGE:
		running_mode = MediaPipeVisionTask.RUNNING_MODE_IMAGE
		_init_task()
	var image := Image.load_from_file(path)
	if delegate == MediaPipeTaskBaseOptions.DELEGATE_GPU:
		image.convert(Image.FORMAT_RGBA8)
	else:
		image.convert(Image.FORMAT_RGB8)
	_process_image(image)


func _open_camera() -> void:
	_reset()
	if CameraServer.monitoring_feeds:
		_select_camera()
	else:
		if not CameraServer.camera_feeds_updated.is_connected(self._select_camera):
			CameraServer.camera_feeds_updated.connect(self._select_camera, CONNECT_ONE_SHOT | CONNECT_DEFERRED)
		CameraServer.monitoring_feeds = true

func _initialize_camera_extension() -> void:
	if camera_extension:
		return
	if not CameraServer.monitoring_feeds:
		return
	if OS.get_name() in ["Windows", "iOS", "macOS"]:
		camera_extension = CameraServerExtension.new()
		camera_extension.permission_result.connect(self._camera_permission_result)
		if not camera_extension.permission_granted():
			camera_extension.request_permission()

func _camera_permission_result(granted: bool) -> void:
	if granted:
		_select_camera()
	else:
		permission_dialog.call_deferred("popup_centered")

func _camera_feeds_updated() -> void:
	_initialize_camera_extension()

func _update_camera_feeds() -> void:
	var feeds = CameraServer.feeds()
	opt_camera_feed.clear()
	for feed in feeds:
		opt_camera_feed.add_item(feed.get_name(), feed.get_id())
		opt_camera_feed.selected = -1

func _select_camera() -> void:
	select_camera_dialog.popup_centered_ratio()

func _camera_selected(_index: int) -> void:
	if camera_feed:
		camera_feed = null
	opt_camera_format.clear()
	select_camera_dialog.get_ok_button().disabled = true
	var id := opt_camera_feed.get_selected_id()
	for feed in CameraServer.feeds():
		if feed.get_id() == id:
			camera_feed = feed
			break
	if camera_feed == null:
		return
	var formats = camera_feed.get_formats()
	for format in formats:
		if format.has("frame_numerator") and format.has("frame_denominator"):
			format["fps"] = round(format["frame_denominator"] / format["frame_numerator"])
		if format.has("framerate_numerator") and format.has("framerate_denominator"):
			format["fps"] = round(format["framerate_numerator"] / format["framerate_denominator"])
		opt_camera_format.add_item(String("{width}x{height}@{fps}({format})").format(format))
		opt_camera_format.selected = -1

func _format_selected(index: int) -> void:
	if camera_feed == null:
		return
	if camera_feed.set_format(index, {}):
		select_camera_dialog.get_ok_button().disabled = false
	else:
		select_camera_dialog.get_ok_button().disabled = true

func _start_camera() -> void:
	if camera_feed == null:
		return
	if camera_feed.get_position() == CameraFeed.FEED_BACK:
		camera_texture.flip_h = false
	else:
		camera_texture.flip_h = true
	camera_feed.format_changed.connect(self._camera_format_changed, ConnectFlags.CONNECT_DEFERRED)
	camera_feed.frame_changed.connect(self._camera_frame_changed, ConnectFlags.CONNECT_DEFERRED)
	camera_feed.feed_is_active = true
	_camera_format_changed()

func _camera_added(id: int):
	for i in range(opt_camera_feed.item_count):
		if opt_camera_feed.get_item_id(i) == id:
			return
	var feeds = CameraServer.feeds()
	for feed in feeds:
		if feed.get_id() == id:
			var idx := opt_camera_feed.selected
			opt_camera_feed.add_item.call_deferred(feed.get_name(), id)
			opt_camera_feed.select.call_deferred(idx)

func _camera_removed(id: int):
	if opt_camera_feed.get_selected_id() == id:
		opt_camera_format.clear.call_deferred()
	for i in range(opt_camera_feed.item_count):
		if opt_camera_feed.get_item_id(i) == id:
			opt_camera_feed.remove_item.call_deferred(i)
			opt_camera_feed.select.call_deferred(-1)
	if camera_feed != null and camera_feed.get_id() == id:
		camera_feed = null

func _camera_format_changed() -> void:
	if camera_feed == null:
		return
	var frame_size := Vector2i.ZERO
	match camera_feed.get_datatype():
		CameraFeed.FEED_RGB:
			var texture_rgb := CameraTexture.new()
			texture_rgb.camera_feed_id = camera_feed.get_id()
			texture_rgb.which_feed = CameraServer.FEED_RGBA_IMAGE
			frame_size = texture_rgb.get_size()
			camera_texture.material = null
			camera_texture.texture = texture_rgb
		CameraFeed.FEED_YCBCR:
			var texture_yuy2 := CameraTexture.new()
			texture_yuy2.camera_feed_id = camera_feed.get_id()
			texture_yuy2.which_feed = CameraServer.FEED_YCBCR_IMAGE
			frame_size = texture_yuy2.get_size()
			var mat := ShaderMaterial.new()
			mat.shader = load("res://vision/yuy2_to_rgb.gdshader")
			mat.set_shader_parameter("texture_yuy2", texture_yuy2)
			camera_texture.material = mat
			var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
			var image_texture := ImageTexture.new()
			image_texture.set_image(image)
			camera_texture.texture = image_texture
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
			camera_texture.material = mat
			frame_size = texture_y.get_size()
			var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
			var image_texture := ImageTexture.new()
			image_texture.set_image(image)
			camera_texture.texture = image_texture
		_:
			return
	var feed_rotation: float = camera_feed.feed_transform.get_rotation()
	if camera_texture.flip_h:
		feed_rotation *= -1
	var size_rotated := Vector2(frame_size).rotated(feed_rotation)
	var offset := Vector2(min(size_rotated.x, 0), min(size_rotated.y, 0))
	camera_texture.rotation = feed_rotation
	camera_texture.position = offset * -1
	camera_viewport.size = frame_size

func _camera_frame_changed() -> void:
	if camera_texture == null:
		return
	await RenderingServer.frame_post_draw
	if camera_viewport == null:
		return
	var texture := camera_viewport.get_texture()
	if texture == null:
		return
	var image = texture.get_image()
	if image == null:
		return
	if delegate == MediaPipeTaskBaseOptions.DELEGATE_GPU:
		image.convert(Image.FORMAT_RGBA8)
	else:
		image.convert(Image.FORMAT_RGB8)
	var img := MediaPipeImage.new()
	img.set_image(image)
	_camera_frame(img)

func _camera_frame(image: MediaPipeImage) -> void:
	if not running_mode == MediaPipeVisionTask.RUNNING_MODE_LIVE_STREAM:
		running_mode = MediaPipeVisionTask.RUNNING_MODE_LIVE_STREAM
		_init_task()
	if delegate == MediaPipeTaskBaseOptions.DELEGATE_CPU and image.is_gpu_image():
		image.convert_to_cpu()
	_process_camera(image, Time.get_ticks_msec())

func _process_image(_image: Image) -> void:
	pass

func _process_video(_image: Image, _timestamp_ms: int) -> void:
	pass

func _process_camera(_image: MediaPipeImage, _timestamp_ms: int) -> void:
	pass

func get_external_model(path: String) -> FileAccess:
	var file := Global.get_model(path)
	if file != null:
		return file
	image_view.hide()
	request = Global.get_external_model(path, _get_external_file)
	if request != null:
		progress_bar.show()
	return null

func update_image(image: Image) -> void:
	image.convert(Image.FORMAT_RGB8)
	if Vector2i(image_view.texture.get_size()) == image.get_size():
		image_view.texture.call_deferred("update", image)
	else:
		image_view.texture.call_deferred("set_image", image)
