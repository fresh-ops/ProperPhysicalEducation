import asyncio

from PySide6 import QtWidgets
from qasync import QEventLoop

from ppe_client.presentation import MainWindow


def main() -> None:
    app = QtWidgets.QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
