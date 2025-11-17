extends Node

var main_scene := preload("res://Main.tscn")
var enable_download_files: bool = true

func _get_external_file(
	result: int,
	response_code: int,
	_headers: PackedStringArray,
	body: PackedByteArray,
	path: String,
	callback: Callable) -> void:
	if result != HTTPRequest.RESULT_SUCCESS:
		return
	if response_code != HTTPClient.RESPONSE_OK:
		return
	if body.is_empty():
		return
	if DirAccess.make_dir_recursive_absolute(path.get_base_dir()) != OK:
		return
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return
	file.store_buffer(body)
	file.close()
	callback.call()
