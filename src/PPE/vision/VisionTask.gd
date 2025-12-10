class_name VisionTask
extends Control


const CAMERA_VIEW_SCENE = preload("res://vision/camera_view/CameraView.tscn")


var _camera_manager: CameraManager
var _landmarks_receiver: LandmarksReceiver


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


func _ready():
	_camera_manager = CameraManager.new()
	_camera_manager.init()
	_landmarks_receiver = LandmarksReceiver.new()
	_landmarks_receiver.init()
	btn_open_camera.pressed.connect(self.__on_open_camera_button_pressed)
	_camera_manager.camera_permission_result_asked.connect(self.__on_camera_permission_result_asked)
	_camera_manager.monitoring_feeds_set.connect(self.__show_camera_selection_dialog)
	_camera_manager.camera_added.connect(self.__on_camera_added)
	_camera_manager.camera_removed.connect(self.__on_camera_removed)
	_camera_manager.camera_feeds_updated.connect(self.__on_camera_feeds_updated)
	opt_camera_feed.item_selected.connect(self.__on_camera_feed_selected)
	opt_camera_format.item_selected.connect(self.__on_format_selected)
	select_camera_dialog.confirmed.connect(self.__start_camera)
	select_camera_dialog.get_ok_button().disabled = true
	btn_open_camera.disabled = false


## Обработчик нажатия на кнопку OpenCamera
func __on_open_camera_button_pressed()-> void:
	if _camera_manager.is_monitoring():
		_camera_manager._initialize_camera_extension()
		__show_camera_selection_dialog()
	

## Реакция на наличие разрешения на камеру
func __on_camera_permission_result_asked(granted: bool) -> void:
	if granted:
		__show_camera_selection_dialog()
	else:
		permission_dialog.call_deferred("popup_centered")


## Заносит все фиды в список для выбора
func __on_camera_feeds_updated() -> void:
	var feeds = _camera_manager.get_feeds()
	opt_camera_feed.clear()
	for feed in feeds:
		opt_camera_feed.add_item(feed.get_name(), feed.get_id())
		opt_camera_feed.selected = -1


## Открывает диалог с выбором камеры
func __show_camera_selection_dialog() -> void:
	select_camera_dialog.popup_centered_ratio()


## Подставляет доступные форматы в поле выбора
func __on_camera_feed_selected(_index: int) -> void:
	opt_camera_format.clear()
	select_camera_dialog.get_ok_button().disabled = false
	var id := opt_camera_feed.get_selected_id()
	var formats = _camera_manager.get_formats(id)
	for format in formats:
		opt_camera_format.add_item(String("{width}x{height}@{fps}({format})").format(format))
		opt_camera_format.selected = -1


## Выставляет формат выбранный пользователем
func __on_format_selected(index: int) -> void:
	if _camera_manager.is_format_set(index):
		select_camera_dialog.get_ok_button().disabled = false
	else:
		select_camera_dialog.get_ok_button().disabled = true


## Запускает камеру
func __start_camera() -> void:
	var camera_view = CAMERA_VIEW_SCENE.instantiate()
	var provider = LandmarksProvider.new()
	cameras_container.add_child.call_deferred(camera_view)
	if cameras_container.get_child_count() >= cameras_container.columns ** 2:
		cameras_container.columns += 1
	cameras_container.queue_sort()
	camera_view.initialize.call_deferred(_camera_manager._camera_feed, provider)
	camera_view.start_camera.call_deferred()
	_landmarks_receiver.add_provider.call_deferred(provider);


## Обрабатывает добавление камеры
func __on_camera_added(id: int):
	# Проверяем, есть ли данный CameraFeed в списке
	for i in range(opt_camera_feed.item_count):
		if opt_camera_feed.get_item_id(i) == id:
			return # Если да, то ничего не делаем
	# Иначе выбираем добавленный CameraFeed
	var feeds = _camera_manager.get_feeds()
	for feed in feeds:
		if feed.get_id() == id:
			# И добавляем его в список, при этом не изменяя последний выбранный элемент
			var idx := opt_camera_feed.selected
			opt_camera_feed.add_item.call_deferred(feed.get_name(), id)
			opt_camera_feed.select.call_deferred(idx)


## Обрабатывает удаление камеры
func __on_camera_removed(id: int):
	# Если удаляем выбранный, то очищаем форматы
	if opt_camera_feed.get_selected_id() == id:
		opt_camera_format.clear.call_deferred()
	# Удаляем из камеру из списка и снимаем выбранную камеру
	for i in range(opt_camera_feed.item_count):
		if opt_camera_feed.get_item_id(i) == id:
			opt_camera_feed.remove_item.call_deferred(i)
			opt_camera_feed.select.call_deferred(-1)
