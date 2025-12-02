
from py4godot.classes.core import Array
from py4godot.classes import gdclass, CameraFeed
from py4godot.classes.Node import Node

import numpy as np
from vision.restoration.translater import BasisTranslator


@gdclass
class SkeletalRestorer(Node):
	__base_feed: CameraFeed
	__translation_table: dict[CameraFeed, BasisTranslator]
	
	def init(self, base_feed: CameraFeed):
		"""
		Initialize SkeletalRestorer. Sets a base CameraFeed and prepares
		the translation table. Can be used as a restore function to reuse one
		instance of this class.
		
		Args:
			base_feed (CameraFeed): a base CameraFeed
		
		Returns:
			SkeletalRestorer: This initialized node.
		"""
		self.__base_feed = base_feed
		self.__translation_table = dict()
		
		return self

	def add_translation(self, camera_feed: CameraFeed, base: Array, translating: Array) -> None:
		base = np.array([row.to_list() for row in base])
		translating = np.array([row.to_list() for row in translating])

		self.__translation_table[camera_feed] = BasisTranslator(base, translating)

	def get_base_feed(self) -> CameraFeed:
		return self.__base_feed
	
	def test(self, data):
		print(np.array(data.to_list()))
