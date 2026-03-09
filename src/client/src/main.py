import sys

from PySide6 import QtWidgets

from src.ui import MainWindow


def main() -> None:
    app = QtWidgets.QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
