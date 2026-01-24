class_name CameraManager
extends Node


signal camera_feeds_updated
signal camera_added
signal camera_removed(id)
signal camera_permission_result_asked
signal monitoring_feeds_set


var __camera_extension: CameraServerExtension


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


## Проверяет, ведется ли мониторинг камер
func is_monitoring() -> bool:
	return true if CameraServer.monitoring_feeds else false


## Подключает monitoring feeds 
func connect_monitoring_feeds() -> void:
	if not CameraServer.camera_feeds_updated.is_connected(func(): monitoring_feeds_set.emit()):
		CameraServer.camera_feeds_updated.connect(func(): monitoring_feeds_set.emit(), CONNECT_ONE_SHOT | CONNECT_DEFERRED)
	CameraServer.monitoring_feeds = true


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
	camera_removed.emit(id)
