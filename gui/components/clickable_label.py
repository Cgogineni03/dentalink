# Clickable QLabel Widget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel


class ClickableLabel(QLabel):
    """QLabel subclass that emits a clicked signal on mouse press."""

    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
