## Класс-обертка над [CameraServer].
class_name CameraManager
extends Node


## Посылается при обновлении списка [CameraFeed].
signal camera_feeds_updated()
## Посылается при добавлении новой камеры к списку [CameraFeed]. 
signal camera_added
## Посылается при удалении камеры из списка доступных [CameraFeed]. 
## [param id] - Идентификатор удалённой камеры.
signal camera_removed(id: int)
## Посылается при запросе разрешения доступа к камере.
signal camera_permission_result_asked
## Посылается, когда мониторинг [CameraFeed] установлен.
signal monitoring_feeds_set()


var __camera_extension: CameraServerExtension


## Инициализирует менеджер камер.
func init() -> void:
	CameraServer.camera_feed_added.connect(self.__on_camera_added)
	CameraServer.camera_feed_removed.connect(self.__on_camera_removed)
	print("Start monitoring")
	if CameraServer.monitoring_feeds:
		__initialize_camera_extension()
		camera_feeds_updated.emit()


## Извлекает список доступных [CameraFeed] из CameraServer.
func get_feeds() -> Array[CameraFeed]:
	return CameraServer.feeds()


## Возвращает, включён ли мониторинг [CameraFeed].
## Возвращает [code]true[/code], если мониторинг включён.
func is_monitoring() -> bool:
	return CameraServer.monitoring_feeds 


## Подключает monitoring feeds и устанавливает расширение камеры.
func start_monitoring() -> void:
	if not CameraServer.camera_feeds_updated.is_connected(func(): monitoring_feeds_set.emit()):
		CameraServer.camera_feeds_updated.connect(func(): monitoring_feeds_set.emit(), CONNECT_ONE_SHOT | CONNECT_DEFERRED)
	CameraServer.monitoring_feeds = true
	__initialize_camera_extension()


## Инициализирует расширение камеры.
func __initialize_camera_extension() -> void:
	if __camera_extension != null:
		return

	if not CameraServer.monitoring_feeds:
		push_error("CameraManager: Cannot initialize camera extension while monitoring_feeds is disabled.")
		return

	if OS.get_name() in ["Windows", "iOS", "macOS"]:
		__camera_extension = CameraServerExtension.new()
		__camera_extension.permission_result.connect(func(): camera_permission_result_asked.emit())
		if not __camera_extension.permission_granted():
			__camera_extension.request_permission()


## Обработчик добавления камеры в список доступных [CameraFeed].
func __on_camera_added(id) -> void:
	camera_added.emit.call_deferred(id)


## Обработчик удаления камеры из списка доступных [CameraFeed].
func __on_camera_removed(id):
	camera_removed.emit(id)


func create_controller() -> CameraController:
	var controller := CameraController.new()
	controller.set_camera_feed(_camera_feed)
	add_child(controller)
	return controller
