class_name VisionTask
extends Control


const CAMERA_VIEW_SCENE = preload("res://vision/camera_view/CameraView.tscn")
const PUBLISHER_SCENE = preload("res://vision/Publisher.tscn")

var _camera_manager: CameraManager
var _landmarks_receiver: LandmarksReceiver
var _publisher: Publisher


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
	add_child(_camera_manager)
	_landmarks_receiver = LandmarksReceiver.new()
	_landmarks_receiver.init()
	_publisher = PUBLISHER_SCENE.instantiate()
	_publisher.setup(_landmarks_receiver)
	_publisher.visible = false
	add_child(_publisher)
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
	_camera_manager.start_monitoring()
	if _camera_manager.is_monitoring():
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
	var id := opt_camera_feed.get_selected_id()
	var camera_feed := _camera_manager.get_feed_by_id(id)
	if camera_feed == null:
		push_error("VisionTask: Cannot load formats, CameraFeed is null")
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
func __on_format_selected(index: int) -> void:
	select_camera_dialog.get_ok_button().disabled = index < 0


## Запускает камеру
func __start_camera() -> void:
	var camera_feed_id := opt_camera_feed.get_selected_id()
	var camera_feed := _camera_manager.get_feed_by_id(camera_feed_id)
	if camera_feed == null:
		push_error("VisionTask: Cannot start camera, CameraFeed is null")
		return
	var format_index := opt_camera_format.selected
	var controller := _camera_manager.create_controller_for(camera_feed)
	if not controller.set_format(format_index):
		push_error("VisionTask: Cannot set format index %d for CameraFeed id %d".format([format_index, camera_feed_id]))
		_camera_manager.remove_controller(controller)
		return

	var provider := LandmarksProvider.new()
	provider.initialize(controller)

	var camera_view := CAMERA_VIEW_SCENE.instantiate()
	cameras_container.add_child.call_deferred(camera_view)
	if cameras_container.get_child_count() >= cameras_container.columns ** 2:
		cameras_container.columns += 1
	cameras_container.queue_sort()

	camera_view.initialize(provider)
	camera_view.start_camera()
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
