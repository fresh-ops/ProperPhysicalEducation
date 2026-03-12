import sys

from PySide6 import QtWidgets

from ppe_client.presentation import MainWindow


def main() -> None:
    app = QtWidgets.QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
