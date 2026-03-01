from PySide6 import QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Proper Physical Education")

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.label = QtWidgets.QLabel(
            "Hello World", alignment=QtCore.Qt.AlignmentFlag.AlignCenter
        )

        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.addWidget(self.label)

        self.setLayout(layout)
