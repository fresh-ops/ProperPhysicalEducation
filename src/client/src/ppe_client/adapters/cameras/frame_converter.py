import numpy as np
from PySide6 import QtGui

from ppe_client.application.cameras import Frame


class FrameConverter:
    @classmethod
    def to_pixel_map(cls, frame: Frame) -> QtGui.QPixmap:
        height, width, channels = frame.shape
        image = QtGui.QImage(
            frame.raw,
            width,
            height,
            channels * width,
            QtGui.QImage.Format.Format_BGR888,
        )

        return QtGui.QPixmap.fromImage(image)

    @classmethod
    def to_ndarray(cls, frame: Frame) -> np.ndarray:
        return np.frombuffer(frame.raw, np.uint8).reshape(frame.shape)
