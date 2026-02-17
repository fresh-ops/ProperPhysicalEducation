extends Control


@onready var open_sensors_btn: Button = $VBoxContainer/Main/OpenSensorsButton
@onready var open_training_btn: Button = $VBoxContainer/Main/OpenTrainingButton


const SCREENS := {
	"Training Screen": "res://training/training_screen.tscn",
	"Sensors Screen": "res://sensors/sensors_screen.tscn",
}


func _ready() -> void:
	open_sensors_btn.connect("pressed", self.__on_open_sensors_pressed)
	open_training_btn.connect("pressed", self.__on_open_training_pressed)

func __on_open_sensors_pressed() -> void:
	__select_screen("Sensors Screen")


func __on_open_training_pressed() -> void:
	__select_screen("Training Screen")


func __select_screen(screen_name: String) -> void:
	if not SCREENS.has(screen_name):
		push_error("Screen '%s' not found in SCREENS dictionary." % screen_name)
		return
	get_tree().change_scene_to_file(SCREENS[screen_name])
