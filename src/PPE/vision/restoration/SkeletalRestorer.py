from py4godot.classes.core import Array, Dictionary
from py4godot.classes import gdclass, CameraFeed
from py4godot.classes.Node import Node

import numpy as np
from vision.restoration.translater import BasisTranslator


def array_to_ndarray(array: Array, depth: int) -> np.ndarray:
	"""
	Translates the godot Array to NumPy ndarray with at most the depth level.

	Args:
		array (py4godot.classes.core.Array): the translating array
		depth (int): the depth of translating. If the element on the level <= depth is not an Array, it will not be translated

	Returns:
		np.ndarray: the translated array
	"""
	if depth == 1:
		return np.array(array.to_list())
	
	def convert_rec(array, depth):
		if depth == 1:
			return array.to_list()
		
		result = []
		for item in array:
			if isinstance(item, type(array)) and hasattr(item, 'to_list'):
				result.append(convert_rec(item, depth - 1))
			else:
				result.append(item)
		return result

	return np.array(convert_rec(array, depth))


def ndarray_to_array(ndarray: np.ndarray, depth: int) -> Array:
	"""
	Translates NumPy ndarray to godot Array with at most the depth level.

	Args:
		ndarray (np.ndarray): the translating ndarray
		depth (int): the depth of translating. If the element on the level <= depth is not an ndarray, it will not be translated

	Returns:
		py4godot.classes.core.Array: the translated array
	"""
	array = ndarray.tolist()

	def convert_rec(array: list, depth: int):
		if depth == 1:
			return Array.from_list(array)
		
		for i in range(len(array)):
			array[i] = convert_rec(array[i], depth - 1)
		return Array.from_list(array)

	return convert_rec(array, depth)



@gdclass
class SkeletalRestorer(Node):
	"""
	A SkeletalRestorer class is an agregator of skeletal landmarks that restores the whole digital skeleton averaging the passed points.
	"""
	def init(self, base_feed_id: int):
		"""
		Initialize SkeletalRestorer. Sets a base CameraFeed and prepares
		the translation table. Can be used as a restore function to reuse one
		instance of this class.
		
		Args:
			base_feed_id (int): a base CameraFeed id
		
		Returns:
			SkeletalRestorer: This initialized node.
		"""
		self.__base_feed_id: int = base_feed_id
		self.__translators: dict[int, BasisTranslator] = dict()
		
		return self

	def add_camera(self, camera_feed_id: int, base: Array, translating: Array) -> None:
		"""
		Adds a new camera source of landmarks.

		Args:
			camera_feed (int): The id of the feed from which the landmarks are provided
			base (py4godot.classes.core.Array): The set of points in the basis of the base CameraFeed. Should be a 2d n-by-m matrix. Every element should be a float value
			translating (py4godot.classes.core.Array): The set of points in the basis of a new CameraFeed. Should have the same shape as a base. Every its point should correspond to the basee one. Every element should be a float value
		"""
		base = array_to_ndarray(base, 2).astype(np.float64)
		translating = array_to_ndarray(translating, 2).astype(np.float64)

		self.__translators[camera_feed_id] = BasisTranslator(base, translating)

	def restore(self, landmarks: Dictionary) -> np.ndarray:
		"""
		Restores the full digital skeleton using the passed landmarks.

		Args:
			landmarks (py4godot.classes.core.Dictionary): A dictionary with CameraFeed ids as a keys and godot Array matrices as a values. Every key CameraFeed id should have a translator added with add_camera() method. Every matrix should have the same shape: n points of format [x, y, z, visibility, presence]. Every value of a point should be float

		Returns:
			np.ndarray: A set of digital skeleton points 
		"""
		all_points = []
		for key in landmarks.keys():
			points = array_to_ndarray(landmarks[key], 2).astype(np.float64)
			points[:, :3] = self.__translators[key].translate(points[:, :3])
			all_points.append(points)
		return ndarray_to_array(self.mean_points(np.array(all_points)), 2)

	def mean_points(self, all_points: np.ndarray):
		coords = all_points[:, :, :3]
		weights = np.prod(all_points[:, :, 3:], axis=2)
		total_weights = np.sum(weights, axis=0)
		mask = total_weights > 0

		result = np.zeros(coords.shape[1:])

		if np.any(mask):
			weighted = np.sum(coords[:, mask] * weights[:, mask, np.newaxis], axis=0)
			result[mask] = weighted / total_weights[mask, np.newaxis]
		if np.any(~mask):
			result[~mask] = np.mean(coords[:, ~mask], axis=0)
		
		return result

	def get_base_feed_id(self) -> CameraFeed:
		return self.__base_feed_id
	
	def test(self, data):
		print(dict(data))
