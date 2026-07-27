# Vector Icon Generators for PyQt6 UI
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap


def create_sidebar_toggle_icon(size=24, color=None):
    """Generates a dynamic vector sidebar toggle icon pixmap."""
    if color is None:
        color = QColor("#94A3B8")
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(color, 2)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    margin = 3
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    painter.drawRoundedRect(rect, 3.5, 3.5)

    split_x = margin + (size - 2 * margin) * 0.62
    painter.drawLine(QPointF(split_x, margin + 1.5), QPointF(split_x, size - margin - 1.5))

    painter.end()
    return QIcon(pixmap)
