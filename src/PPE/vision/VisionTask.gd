class_name VisionTask
extends Control

var request: HTTPRequest
var camera_extension: CameraServerExtension
var camera_windows: Array[CameraWindow] = []

@onready var camera_container: Container = $ScrollContainer/VBoxContainer/CameraContainer
@onready var progress_bar: ProgressBar = $ScrollContainer/VBoxContainer/ProgressBar
@onready var btn_open_camera: Button = $ScrollContainer/VBoxContainer/Buttons/OpenCamera
@onready var select_camera_dialog: ConfirmationDialog = $SelectCamera
@onready var opt_camera_feed: OptionButton = $SelectCamera/VBoxContainer/SelectFeed
@onready var permission_dialog: AcceptDialog = $PermissionDialog

var camera_window_scene = preload("res://vision/camera_window/CameraWindow.tscn")
var model_provider: ModelProvider

func _exit_tree() -> void:
	if request:
		request.cancel_request()
		request = null
	camera_extension = null

func _ready():
	model_provider = ModelProvider.new()
	btn_open_camera.pressed.connect(self._open_camera)	
	CameraServer.camera_feed_added.connect(self._camera_added)
	CameraServer.camera_feed_removed.connect(self._camera_removed)
	CameraServer.camera_feeds_updated.connect(self._camera_feeds_updated)
	model_provider.download_started.connect(self._show_progress_bar)
	model_provider.download_ended.connect(self._hide_progress_bar)
	if CameraServer.monitoring_feeds:
		_initialize_camera_extension()
		_update_camera_feeds()
	select_camera_dialog.get_ok_button().disabled = true
	opt_camera_feed.item_selected.connect(self._camera_selected)
	select_camera_dialog.confirmed.connect(self._start_camera)
	camera_container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_init_task()

func _show_progress_bar(req: HTTPRequest) -> void:
	request = req
	if request != null:
		progress_bar.show()
	
func _process(_delta: float) -> void:
	if request:
		var max_size := request.get_body_size()
		var cur_size := request.get_downloaded_bytes()
		progress_bar.value = round(float(cur_size) / float(max_size) * 100)

func _hide_progress_bar() -> void:
	progress_bar.hide()
	request = null
	_init_task()

func _init_task() -> void:
	btn_open_camera.disabled = false

func _update_container_layout() -> void:
	camera_container.queue_sort()
	await get_tree().process_frame
	$ScrollContainer.queue_sort()

func _open_camera() -> void:
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

func _start_camera() -> void:
	var camera_id: int = select_camera_dialog.get_meta("selected_camera_id")
	var selected_feed
	for feed in CameraServer.feeds():
		if feed.get_id() == camera_id:
			selected_feed = feed
			break
	if !selected_feed:
		return
	for window in camera_windows:
		if window.camera_feed.get_id() == camera_id:
			return
	
	var new_camera_window = camera_window_scene.instantiate()
	camera_container.add_child(new_camera_window)
	camera_windows.append(new_camera_window)
	new_camera_window.init_camera(selected_feed)
	_update_container_layout()

func _select_camera() -> void:
	select_camera_dialog.popup_centered_ratio()

func _camera_selected(_index: int) -> void:
	select_camera_dialog.get_ok_button().disabled = false
	var id := opt_camera_feed.get_selected_id()
	select_camera_dialog.set_meta("selected_camera_id", id)

func _camera_added(id: int):
	var feeds = CameraServer.feeds()
	for feed in feeds:
		if feed.get_id() == id:
			var idx := opt_camera_feed.selected
			opt_camera_feed.add_item.call_deferred(feed.get_name(), id)
			opt_camera_feed.select.call_deferred(idx)

func _camera_removed(id: int):
	for i in range(opt_camera_feed.item_count):
		if opt_camera_feed.get_item_id(i) == id:
			opt_camera_feed.remove_item.call_deferred(i)
			opt_camera_feed.select.call_deferred(-1)
	for i in range(camera_windows.size()):
		var window = camera_windows[i]
		if window.camera_feed and window.camera_feed.get_id() == id:
			window.queue_free() 
			camera_windows.remove_at(i)
			break
