class_name Publisher
extends Control


@onready var __mqtt = $MQTT


var __config 
var __reciever: LandmarksReceiver
var __mqtt_host: String = ""
var __mqtt_topic: String = ""


## IMPORTANT! 
## Fill config.cfg with information of mqtt host and topic
func setup(reciever: LandmarksReceiver) -> void:
	__reciever = reciever
	__config = ConfigFile.new()
	var err = __config.load("res://config.cfg")
	if err == OK:
		__mqtt_host = __config.get_value("mqtt", "host")
		__mqtt_topic = __config.get_value("mqtt", "topic")
	else:
		push_error("Failed to load config.cfg, using defaults")
		__mqtt_host = "tcp://localhost:1883"
		__mqtt_topic = "landmarks"


func _ready() -> void:
	__mqtt.connect_to_broker(__mqtt_host)


func __send_data(data: Array) -> void:
	var json_string = JSON.stringify(data)
	__mqtt.publish(__mqtt_topic, json_string)


func _on_mqtt_broker_connected() -> void:
	print("Connected to broker")
	__reciever.data_sended.connect(__send_data)


func _on_mqtt_broker_connection_failed() -> void:
	print("Connecting to broker failed!")


func _on_mqtt_broker_disconnected() -> void:
	print("Disconnected from broker")
	if __reciever.data_sended.is_connected(__send_data):
		__reciever.data_sended.disconnect(__send_data)
