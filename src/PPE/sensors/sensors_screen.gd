extends VBoxContainer


@onready var connect_sensors_btn: Button = $ConnectSensorButton

func _ready() -> void:
	connect_sensors_btn.connect("pressed", self.__on_connect_sensors_pressed)


func __on_connect_sensors_pressed() -> void:
	print("Connect Sensors button pressed.")
