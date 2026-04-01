import asyncio

from PySide6 import QtWidgets
from qasync import QEventLoop

from ppe_client.presentation import MainWindow

from .di import create_container


def main() -> None:
    app = QtWidgets.QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    container = create_container()

    with container.enter_scope() as scope:
        window = MainWindow(container=scope)
        window.show()

        with loop:
            loop.run_forever()


if __name__ == "__main__":
    main()
