class_name LandmarksReceiver
extends Node

signal data_sended(data: Array)


const RESTORER = preload("res://vision/restoration/SkeletalRestorer.py")
const SYNC_TOLERANCE_MS = 10

var restorer


var __queues: Dictionary = {}
var __base_feed_set: bool


func init() -> void:
	restorer = ScriptedNodeFactory.create(RESTORER).init()
	__base_feed_set = false


func add_provider(provider: LandmarksProvider) -> void:
	if not __base_feed_set:
		restorer.set_base_feed_id(provider.get_camera_feed_id())
		__base_feed_set = true
	provider.landmarks_sended.connect(__add_signal_to_queue)


func __add_signal_to_queue(camera_id: int, landmarks: MediaPipePoseLandmarkerResult, timestamp_ms: int) -> void:
	if not __queues.has(camera_id):
		__queues[camera_id] = []
	__queues[camera_id].push_back({"landmarks": landmarks, "timestamp_ms": timestamp_ms})
	__sync_queues_frames()


func __sync_queues_frames() -> void:
	var oldest_timestamp = INF
	var newest_timestamp = -INF
	
	for camera_id in __queues.keys():
		var queue = __queues[camera_id]
		if not queue.is_empty():
			var first_timestamp = queue[0].timestamp_ms
			oldest_timestamp = min(oldest_timestamp, first_timestamp)
			newest_timestamp = max(newest_timestamp, first_timestamp)
		else:
			return
			
	if newest_timestamp - oldest_timestamp <= SYNC_TOLERANCE_MS:
		__prepare_and_send_data()
	else:
		__drop_oldest_frame()


func __drop_oldest_frame() -> void:
	var id = -1
	var oldest_timestamp = INF
	
	for camera_id in __queues.keys():
		var queue = __queues[camera_id]
		if not queue.is_empty():
			var timestamp = queue[0].timestamp_ms
			if timestamp < oldest_timestamp:
				oldest_timestamp = timestamp
				id = camera_id
	__queues[id].pop_front()
	__sync_queues_frames() 


func __prepare_and_send_data() -> void:
	var data: Dictionary[int, Array] = {}
	for camera_id in __queues.keys():
		var queue = __queues[camera_id]
		if not queue.is_empty():
			var element = queue.pop_front()
			var landmarks = __format_landmarks(element.landmarks)
			data[camera_id] = landmarks
	__send_data(data)


func __format_landmarks(landmarks: MediaPipePoseLandmarkerResult) -> Array:
	var formatted_landmarks: Array = []
	if landmarks.pose_landmarks.size() > 0:
		for landmark in landmarks.pose_landmarks[0].landmarks:
			formatted_landmarks.append([landmark.x, landmark.y, landmark.z, landmark.visibility, landmark.presence])
	return formatted_landmarks


func __send_data(data: Dictionary) -> void:
	var result = restorer.restore(data)
	data_sended.emit(result)
