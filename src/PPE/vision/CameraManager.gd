class_name CameraManager
extends Node


signal update_camera_feeds
signal camera_added
signal camera_removed(id)
signal camera_permission_result
signal select_camera


var camera_extension: CameraServerExtension
var camera_feed


func init() -> void:
	CameraServer.camera_feed_added.connect(self._camera_added)
	CameraServer.camera_feed_removed.connect(self._camera_removed)
	if CameraServer.monitoring_feeds:
		_initialize_camera_extension()
		_update_camera_feeds()


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


func _camera_permission_result():
	camera_permission_result.emit()


func _camera_added(_index: int):
	camera_added.emit(_index)


func _get_feeds():
	return CameraServer.feeds()


func _camera_removed(id):
	## Сбрасываем CameraFeed, если он был удалён
	if camera_feed != null and camera_feed.get_id() == id:
		camera_feed = null
	camera_removed.emit(id)


func _update_camera_feeds() -> void:
	update_camera_feeds.emit()


func get_formats(id) -> Array:
	if camera_feed:
		camera_feed = null
	for feed in CameraServer.feeds():
		if feed.get_id() == id:
			camera_feed = feed
			break
	if camera_feed == null:
		return []
	var formats = camera_feed.get_formats()
	for format in formats:
		if format.has("frame_numerator") and format.has("frame_denominator"):
			format["fps"] = round(format["frame_denominator"] / format["frame_numerator"])
		if format.has("framerate_numerator") and format.has("framerate_denominator"):
			format["fps"] = round(format["framerate_numerator"] / format["framerate_denominator"])
	return formats


## Выставляет формат выбранный пользователем
func format_setted(index: int) -> bool:
	if camera_feed == null:
		return false
	if camera_feed.set_format(index, {}):
		return true
	return false


func _select_camera():
	select_camera.emit()


func is_monitoring() -> bool:
	if not CameraServer.monitoring_feeds:
		if not CameraServer.camera_feeds_updated.is_connected(self._select_camera):
				CameraServer.camera_feeds_updated.connect(self._select_camera, CONNECT_ONE_SHOT | CONNECT_DEFERRED)
		CameraServer.monitoring_feeds = true
	return true
