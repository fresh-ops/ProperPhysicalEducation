from dataclasses import dataclass
from typing import Any, override

from PySide6 import QtCore, QtWidgets

from ui.routing import Payload, Route, Screen


@dataclass
class MyScreenPayload(Payload):
    label: str


class MyScreen(Screen[MyScreenPayload]):
    def __init__(self, **knargs: Any) -> None:
        super().__init__(**knargs)

        self.label = QtWidgets.QLabel("")
        self.button = QtWidgets.QPushButton("Click me")
        self.button.clicked.connect(self._on_click)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)

    @override
    def on_enter(self, payload: MyScreenPayload | None = None) -> None:
        if payload is not None:
            self.label.setText(payload.label)

    @QtCore.Slot()
    def _on_click(self) -> None:
        self.request_navigation(Route.HOME, MyScreenPayload(label="Salute!"))
