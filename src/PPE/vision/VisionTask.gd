class_name VisionTask
extends Control


var camera_extension: CameraServerExtension
var camera_feed

const CAMERA_VIEW_SCENE = preload("res://vision/camera_view/CameraView.tscn")

## Кнопка открытия [member select_camera_dialog]
@onready var btn_open_camera: Button = $VBoxContainer/Buttons/OpenCamera
## Диалог выбора камеры
@onready var select_camera_dialog: ConfirmationDialog = $SelectCamera
## Возможные варианты выбора камеры
@onready var opt_camera_feed: OptionButton = $SelectCamera/VBoxContainer/SelectFeed
## Возможные варианты выбора формата камеры
@onready var opt_camera_format: OptionButton = $SelectCamera/VBoxContainer/SelectFormat
## Диалог запроса разрешений
@onready var permission_dialog: AcceptDialog = $PermissionDialog
@onready var cameras_container: GridContainer = $VBoxContainer/CamerasContainer


func _exit_tree() -> void:
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


## Разблокирует кнопку выбора камеры
func _init_task() -> void:
	btn_open_camera.disabled = false


## Обработчик нажатия на кнопку OpenCamera
func _open_camera() -> void:
	if CameraServer.monitoring_feeds:
		_select_camera()
	else:
		if not CameraServer.camera_feeds_updated.is_connected(self._select_camera):
			CameraServer.camera_feeds_updated.connect(self._select_camera, CONNECT_ONE_SHOT | CONNECT_DEFERRED)
		CameraServer.monitoring_feeds = true


## Инициализирует камерное расширение
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


## Реакция на наличие разрешения на камеру
func _camera_permission_result(granted: bool) -> void:
	if granted:
		_select_camera()
	else:
		permission_dialog.call_deferred("popup_centered")


## Обработчик обновления фидов
func _camera_feeds_updated() -> void:
	_initialize_camera_extension()


## Заносит все фиды в список для выбора
func _update_camera_feeds() -> void:
	var feeds = CameraServer.feeds()
	opt_camera_feed.clear()
	for feed in feeds:
		opt_camera_feed.add_item(feed.get_name(), feed.get_id())
		opt_camera_feed.selected = -1


## Открывает диалог с выбором камеры
func _select_camera() -> void:
	select_camera_dialog.popup_centered_ratio()


## Подставляет доступные форматы в поле выбора
func _camera_selected(_index: int) -> void:
	if camera_feed:
		camera_feed = null
	opt_camera_format.clear()
	select_camera_dialog.get_ok_button().disabled = false
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


## Выставляет формат выбранный пользователем
func _format_selected(index: int) -> void:
	if camera_feed == null:
		return
	if camera_feed.set_format(index, {}):
		select_camera_dialog.get_ok_button().disabled = false
	else:
		select_camera_dialog.get_ok_button().disabled = true


## Запускает камеру
func _start_camera() -> void:
	var camera_view = CAMERA_VIEW_SCENE.instantiate()
	cameras_container.add_child.call_deferred(camera_view)
	if cameras_container.get_child_count() >= cameras_container.columns ** 2:
		cameras_container.columns += 1
	cameras_container.queue_sort()
	camera_view.initialize.call_deferred(camera_feed)
	camera_view.start_camera.call_deferred()


## Обрабатывает добавление камеры
func _camera_added(id: int):
	# Проверяем, есть ли данный CameraFeed в списку
	for i in range(opt_camera_feed.item_count):
		if opt_camera_feed.get_item_id(i) == id:
			return # Если да, то ничего не делаем
	var feeds = CameraServer.feeds()
	# Иначе выбираем добавленный CameraFeed
	for feed in feeds:
		if feed.get_id() == id:
			# И добавляем его в список, при этом не изменяя последний выбранный элемент
			var idx := opt_camera_feed.selected
			opt_camera_feed.add_item.call_deferred(feed.get_name(), id)
			opt_camera_feed.select.call_deferred(idx)


## Обрабатывает удаление камеры
func _camera_removed(id: int):
	# Если удаляем выбранный, то очищаем форматы
	if opt_camera_feed.get_selected_id() == id:
		opt_camera_format.clear.call_deferred()
	# Удаляем из камеру из списка и снимаем выбранную камеру
	for i in range(opt_camera_feed.item_count):
		if opt_camera_feed.get_item_id(i) == id:
			opt_camera_feed.remove_item.call_deferred(i)
			opt_camera_feed.select.call_deferred(-1)
	# Сбрасываем CameraFeed, если он был удалён
	if camera_feed != null and camera_feed.get_id() == id:
		camera_feed = null
