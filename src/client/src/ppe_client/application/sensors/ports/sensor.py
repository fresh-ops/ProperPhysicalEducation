from typing import Protocol

from ppe_client.domain import SensorDescriptor

from ..calibration.calibration_data import CalibrationData
from ..sensor_value import SensorValue


class Sensor(Protocol):
    """Protocol describing an EMG public interface"""

    async def connect(self) -> None:
        """Establish a connection with this sensor"""
        ...

    async def disconnect(self) -> None:
        """Terminate a connection with this sensor"""
        ...

    @property
    def descriptor(self) -> SensorDescriptor:
        """Returns a binded descriptor

        Returns:
            SensorDescriptor: a descriptor of this sensor
        """
        ...

    def is_connected(self) -> bool:
        """Checks for a connection to this sensor

        Returns:
            bool: True if connected, False otherwise
        """
        ...

    async def read(self) -> SensorValue:
        """Reads a floating-point value of muscle tension"""
        ...

    def apply_calibration(self, data: CalibrationData) -> None:
        """Apply calibration thresholds/state to this sensor instance."""
        ...

    @property
    def calibration_data(self) -> CalibrationData | None:
        """Return applied calibration data, or None if not calibrated."""
        ...
