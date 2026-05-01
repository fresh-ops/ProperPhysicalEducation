from typing import Protocol

from ppe_client.domain import SensorDescriptor

from .calibration_data import CalibrationData, ValueZone


class Sensor(Protocol):
    """Protocol describing an EMG public interface"""

    async def connect(self) -> None:
        """Establish a connection with this sensor"""
        ...

    async def disconnect(self) -> None:
        """Terminate a connection with this sensor"""
        ...

    def descriptor(self) -> SensorDescriptor:
        """Returns a binded descriptor

        Returns:
            SensorDescriptor: a descriptor of this sensor
        """
        ...

    def has_connections(self) -> bool:
        """Checks for a connection to this sensor

        Returns:
            bool: True if connected, False otherwise
        """
        ...

    async def read(self) -> float:
        """Reads a floating-point value of muscle tension"""
        ...

    async def read_with_zone(self) -> tuple[float, ValueZone]:
        """Read one value and return it together with a tension zone.

        Returns:
            tuple: (value, zone)
        """
        ...

    def apply_calibration(self, data: CalibrationData) -> None:
        """Apply calibration thresholds/state to this sensor instance."""
        ...

    def get_calibration_data(self) -> CalibrationData | None:
        """Return applied calibration data, or None if not calibrated."""
        ...
