## Класс-обёртка над [CameraFeed], предоставляющий удобный интерфейс для
## управления камерой и получения кадров. 
class_name CameraController
extends Node

## Посылается, когда поток запущен.
signal feed_started
## Посылается, когда поток остановлен.
signal feed_stopped
## Посылается, когда доступен новый кадр.[br]
## [param image] - Изображение полученного кадра.
signal frame_changed(image: Image)
## Посылается, когда изменён формат.
signal format_changed


var __camera_feed: CameraFeed = null
var __viewport: SubViewport
var __texture: TextureRect


# =====================================================================
# ЖИЗНЕННЫЙ ЦИКЛ
# =====================================================================

func _ready() -> void:
	__viewport = SubViewport.new()
	__viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	__texture = TextureRect.new()
	__viewport.add_child(__texture)
	add_child(__viewport)


func _exit_tree() -> void:
	__free_resources()

# =====================================================================
# ПУБЛИЧНЫЕ МЕТОДЫ
# =====================================================================

## Устанавливает [CameraFeed]. Если до этого был установлен другой [CameraFeed],
## то он останавливается независимо от состояния.
func set_camera_feed(camera_feed: CameraFeed) -> void:
	print("CameraController: Setting new CameraFeed")
	__free_resources()
	__camera_feed = camera_feed
	__connect_signals()


## Запускает поток от [CameraFeed]. При вызове данного метода посылается сигнал
## [signal CameraController.feed_started]. Возвращает [code]true[/code], если запуск прошёл успешно.
func start() -> bool:
	if __camera_feed == null:
		push_error("CameraController: CameraFeed must be set before start")
		return false
	__camera_feed.feed_is_active = true
	__setup_feed_display()
	feed_started.emit()
	return true


## Останавливает поток от [CameraFeed]. При вызове данного метода посылается
## [signal CameraController.feed_stopped].
func stop() -> void:
	if __camera_feed:
		__camera_feed.feed_is_active = false
	feed_stopped.emit()


## Извлекает доступные форматы для управляемого [CameraFeed].
func get_formats() -> Array:
	if __camera_feed == null:
		push_error("CameraController: CameraFeed must be set before getting formats")
		return []
	return __camera_feed.get_formats()


## Выставляет формат под индексом [code]index[/code]. Возвращает [code]true[/code], если формат успешно установлен.
func set_format(index: int) -> bool:
	if __camera_feed == null:
		push_error("CameraController: CameraFeed must be set before setting format")
		return false
	return __camera_feed.set_format(index, {})


## Возвращает положение камеры на устройстве.[br]
func get_position() -> CameraFeed.FeedPosition:
	return __camera_feed.get_position()


## Возвращает идентификатор управляемого [CameraFeed].
func get_feed_id() -> int:
	if __camera_feed == null:
		return -1
	return __camera_feed.get_id()

# =====================================================================
# ВНУТРЕННИЕ РЕСУРСЫ
# =====================================================================

## Освобождает ресурсы связанные с управляемым [CameraFeed].
func __free_resources() -> void:
	if __camera_feed:
		stop()
		__disconnect_signals()


## Привязывает обработчики сигналов к управляемому [CameraFeed].
func __connect_signals() -> void:
	__camera_feed.frame_changed.connect(__on_frame_changed)
	__camera_feed.format_changed.connect(__on_format_changed)


## Отвязывает все сигналы от управляемого [CameraFeed].
func __disconnect_signals() -> void:
	__camera_feed.frame_changed.disconnect(__on_frame_changed)
	__camera_feed.format_changed.disconnect(__on_format_changed)

# =====================================================================
# ОБРАБОТЧИКИ СИГНАЛОВ
# =====================================================================

## Обработчик получения нового кадра от управляемого [CameraFeed].
func __on_frame_changed() -> void:
	print("CameraController: New frame received from CameraFeed")
	var image := await __read_image_from_feed()
	frame_changed.emit(image)


## Обработчик изменения формата у управляемого [CameraFeed].
func __on_format_changed() -> void:
	__setup_feed_display()
	format_changed.emit()

# =====================================================================
# РАБОТА С ИЗОБРАЖЕНИЕМ
# =====================================================================

## Считывает изображение из текущего видеопотока.
func __read_image_from_feed() -> Image:
	if not __validate_read_components():
		push_error("CameraController: Cannot read image from feed due to invalid components")
		return null
	await RenderingServer.frame_post_draw
	var texture := __get_viewport_texture()
	if texture == null:
		push_error("CameraController: Cannot read image from a null texture")
		return null
	return texture.get_image()


## Проверяет готовность компонентов для чтения изображения.
func __validate_read_components() -> bool:
	if __texture == null:
		push_error("CameraController: TextureRect is null")
		return false
	if __viewport == null:
		push_error("CameraController: SubViewport is null")
		return false
	return true


## Извлекает текстуру из [SubViewport].
func __get_viewport_texture() -> Texture2D:
	var texture := __viewport.get_texture()
	if texture == null:
		push_error("CameraController: Viewport texture is null")
	return texture


## Настраивает отображение потока в зависимости от типа видеопотока.
func __setup_feed_display() -> void:
	if __camera_feed == null:
		push_error("CameraController: CameraFeed must be set before setting up display")
		return
	var frame_size := Vector2i.ZERO
	match __camera_feed.get_datatype():
		CameraFeed.FEED_RGB:
			frame_size = __setup_rgb_feed()
		CameraFeed.FEED_YCBCR:
			frame_size = __setup_ycbcr_feed()
		CameraFeed.FEED_YCBCR_SEP:
			frame_size = __setup_ycbcr_sep_feed()
		_:
			push_warning("CameraController: Unsupported camera feed datatype")
			__texture.texture = null
			__texture.material = null
			return
	__apply_feed_rotation(frame_size)


## Настраивает отображение RGB потока.
func __setup_rgb_feed() -> Vector2i:
	var texture_rgb := CameraTexture.new()
	texture_rgb.camera_feed_id = __camera_feed.get_id()
	texture_rgb.which_feed = CameraServer.FEED_RGBA_IMAGE
	var frame_size : Vector2i = texture_rgb.get_size()
	__texture.material = null
	__texture.texture = texture_rgb
	return frame_size


## Настраивает отображение YCBCR потока.
func __setup_ycbcr_feed() -> Vector2i:
	var texture_yuy2 := CameraTexture.new()
	texture_yuy2.camera_feed_id = __camera_feed.get_id()
	texture_yuy2.which_feed = CameraServer.FEED_YCBCR_IMAGE
	var frame_size : Vector2i = texture_yuy2.get_size()
	var mat := ShaderMaterial.new()
	mat.shader = load("res://vision/yuy2_to_rgb.gdshader")
	mat.set_shader_parameter("texture_yuy2", texture_yuy2)
	__texture.material = mat
	var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
	var image_texture := ImageTexture.new()
	image_texture.set_image(image)
	__texture.texture = image_texture
	return frame_size


## Настраивает отображение YCBCR_SEP потока.
func __setup_ycbcr_sep_feed() -> Vector2i:
	var texture_y := CameraTexture.new()
	var texture_uv := CameraTexture.new()
	texture_y.camera_feed_id = __camera_feed.get_id()
	texture_uv.camera_feed_id = __camera_feed.get_id()
	texture_y.which_feed = CameraServer.FEED_Y_IMAGE
	texture_uv.which_feed = CameraServer.FEED_CBCR_IMAGE
	var mat := ShaderMaterial.new()
	mat.shader = load("res://vision/yuv420_to_rgb.gdshader")
	mat.set_shader_parameter("texture_y", texture_y)
	mat.set_shader_parameter("texture_uv", texture_uv)
	__texture.material = mat
	var frame_size : Vector2i = texture_y.get_size()
	var image := Image.create_empty(frame_size.x, frame_size.y, false, Image.FORMAT_RGB8)
	var image_texture := ImageTexture.new()
	image_texture.set_image(image)
	__texture.texture = image_texture
	return frame_size


## Применяет поворот к отображаемому потоку в зависимости от положения камеры.
func __apply_feed_rotation(frame_size: Vector2i) -> void:
	var feed_rotation: float = __camera_feed.feed_transform.get_rotation()
	if __texture.flip_h:
		feed_rotation *= -1
	var size_rotated := Vector2(frame_size).rotated(feed_rotation)
	var offset := Vector2(min(size_rotated.x, 0), min(size_rotated.y, 0))
	__texture.rotation = feed_rotation
	__texture.position = offset * -1
	__viewport.size = frame_size

	__texture.flip_h = __camera_feed.get_position() != CameraFeed.FEED_FRONT
