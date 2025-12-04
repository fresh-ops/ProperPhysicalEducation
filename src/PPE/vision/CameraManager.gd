class_name CameraManager
extends Node


signal camera_feeds_updated
signal camera_added
signal camera_removed(id)
signal camera_permission_result_asked
signal monitoring_feeds_set


var __camera_extension: CameraServerExtension
var _camera_feed


## Инициализирует менеджер камер
func init() -> void:
	CameraServer.camera_feed_added.connect(func(_index): camera_added.emit(_index))
	CameraServer.camera_feed_removed.connect(self.__on_camera_removed)
	if CameraServer.monitoring_feeds:
		_initialize_camera_extension()
		camera_feeds_updated.emit()


## Извлекает доступные камеры из CameraServer
func get_feeds():
	return CameraServer.feeds()


## Извлекает доступные форматы для определенной камеры
func get_formats(id) -> Array:
	if _camera_feed:
		_camera_feed = null
	for feed in CameraServer.feeds():
		if feed.get_id() == id:
			_camera_feed = feed
			break
	if _camera_feed == null:
		return []
	var formats = _camera_feed.get_formats()
	for format in formats:
		if format.has("frame_numerator") and format.has("frame_denominator"):
			format["fps"] = round(format["frame_denominator"] / format["frame_numerator"])
		if format.has("framerate_numerator") and format.has("framerate_denominator"):
			format["fps"] = round(format["framerate_numerator"] / format["framerate_denominator"])
	return formats


## Выставляет формат выбранный пользователем
func is_format_set(index: int) -> bool:
	if _camera_feed == null:
		return false
	if _camera_feed.set_format(index, {}):
		return true
	return false


## Подключает monitoring feeds 
func is_monitoring() -> bool:
	if not CameraServer.monitoring_feeds:
		if not CameraServer.camera_feeds_updated.is_connected(func(): monitoring_feeds_set.emit()):
				CameraServer.camera_feeds_updated.connect(func(): monitoring_feeds_set.emit(), CONNECT_ONE_SHOT | CONNECT_DEFERRED)
		CameraServer.monitoring_feeds = true
	return true


func _initialize_camera_extension() -> void:
	if __camera_extension:
		return
	if not CameraServer.monitoring_feeds:
		return
	if OS.get_name() in ["Windows", "iOS", "macOS"]:
		__camera_extension = CameraServerExtension.new()
		__camera_extension.permission_result.connect(func(): camera_permission_result_asked.emit())
		if not __camera_extension.permission_granted():
			__camera_extension.request_permission()


func __on_camera_removed(id):
	## Сбрасываем CameraFeed, если он был удалён
	if _camera_feed != null and _camera_feed.get_id() == id:
		_camera_feed = null
	camera_removed.emit(id)
