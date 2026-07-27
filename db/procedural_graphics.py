# DentaLink Procedural Clinical Graphics & X-Ray Mock Image Generators
from PyQt6.QtCore import QBuffer, Qt
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QApplication


def generate_procedural_xray_bytes():
    """Generates a realistic grey-level dental jaw X-ray using QImage and QPainter, returning binary bytes."""
    _app = QApplication.instance() or QApplication([])
    width, height = 400, 300
    img = QImage(width, height, QImage.Format.Format_Grayscale8)
    img.fill(QColor(15, 15, 15))

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    gradient = QRadialGradient(width / 2, height + 50, 350)
    gradient.setColorAt(0, QColor(90, 90, 90))
    gradient.setColorAt(0.6, QColor(50, 50, 50))
    gradient.setColorAt(1, QColor(15, 15, 15))
    painter.setBrush(gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(50, 80, 300, 300)

    painter.setBrush(QColor(160, 160, 160))
    painter.setPen(QPen(QColor(30, 30, 30), 1))

    teeth_x = [70, 110, 150, 190, 230, 270, 310]
    for x in teeth_x:
        painter.drawRoundedRect(x, 140, 25, 30, 5, 5)
        painter.drawEllipse(x + 5, 170, 15, 35)

    painter.setBrush(QColor(245, 245, 245))
    painter.drawRect(120, 140, 10, 12)
    painter.drawRect(235, 140, 12, 10)

    painter.setBrush(QColor(35, 35, 35))
    painter.setPen(QPen(QColor(50, 50, 50), 1))
    painter.drawEllipse(192, 148, 8, 8)

    painter.setBrush(QColor(220, 220, 220))
    painter.drawRoundedRect(270, 136, 25, 34, 3, 3)

    painter.end()

    ba = QBuffer()
    ba.open(QBuffer.OpenModeFlag.WriteOnly)
    img.save(ba, "PNG")
    return ba.data().data()


def generate_procedural_intraoral_photo_bytes(has_decay=False, has_inflamed_gums=False):
    """Generates a realistic color intraoral tooth/gum photo using QImage and QPainter, returning binary bytes."""
    width, height = 400, 300
    img = QImage(width, height, QImage.Format.Format_ARGB32)
    gum_color = QColor(230, 92, 92) if has_inflamed_gums else QColor(255, 180, 185)
    img.fill(gum_color)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QColor(40, 10, 15))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(50, 90, 300, 120)

    teeth_x = [75, 115, 155, 195, 235, 275, 315]
    for i, x in enumerate(teeth_x):
        painter.setBrush(QColor(250, 248, 235))
        painter.setPen(QPen(QColor(180, 175, 160), 1))
        painter.drawRoundedRect(x, 110, 28, 35, 6, 6)

        painter.setBrush(QColor(235, 230, 210))
        painter.drawEllipse(x + 4, 132, 20, 10)

    if has_decay:
        painter.setBrush(QColor(65, 35, 15))
        painter.setPen(QPen(QColor(40, 20, 10), 1))
        painter.drawEllipse(204, 122, 10, 12)
        painter.setBrush(QColor(10, 5, 0))
        painter.drawEllipse(206, 124, 6, 8)

    painter.end()

    ba = QBuffer()
    ba.open(QBuffer.OpenModeFlag.WriteOnly)
    img.save(ba, "PNG")
    return ba.data().data()


def generate_procedural_extraoral_photo_bytes():
    """Generates a realistic color extraoral smiling photo using QImage and QPainter, returning binary bytes."""
    width, height = 400, 300
    img = QImage(width, height, QImage.Format.Format_ARGB32)
    img.fill(QColor(240, 240, 245))

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QColor(245, 215, 190))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(80, 20, 240, 260)

    painter.setBrush(QColor(210, 60, 80))
    painter.drawEllipse(130, 150, 140, 60)

    painter.setBrush(QColor(50, 10, 15))
    painter.drawEllipse(140, 160, 120, 40)

    painter.setBrush(QColor(255, 255, 255))
    teeth_x = [152, 166, 180, 194, 208, 222, 236]
    for x in teeth_x:
        painter.drawRoundedRect(x, 160, 12, 16, 2, 2)

    painter.end()

    ba = QBuffer()
    ba.open(QBuffer.OpenModeFlag.WriteOnly)
    img.save(ba, "PNG")
    return ba.data().data()


def generate_procedural_opg_fracture_bytes():
    """Generates a realistic panoramic dental X-ray (OPG) showing a mandibular parasymphysis fracture."""
    _app = QApplication.instance() or QApplication([])
    width, height = 500, 250
    img = QImage(width, height, QImage.Format.Format_Grayscale8)
    img.fill(QColor(10, 10, 10))

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    path = QPainterPath()
    path.moveTo(60, 60)
    path.quadTo(width / 2, height + 40, width - 60, 60)

    pen = QPen(QColor(95, 95, 95), 45)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawPath(path)

    painter.setPen(QPen(QColor(10, 10, 10), 4))
    painter.drawLine(185, 120, 195, 195)

    painter.setPen(QPen(QColor(30, 30, 30), 1))

    for i in range(10):
        t_x = 70 + i * 14
        dx = (t_x - 250) / 190.0
        t_y = 175 - 110 * (1.0 - dx * dx)

        painter.setBrush(QColor(175, 175, 175))
        painter.drawRoundedRect(t_x, int(t_y), 11, 14, 2, 2)
        painter.setBrush(QColor(140, 140, 140))
        painter.drawEllipse(t_x + 2, int(t_y) + 14, 7, 18)

    for i in range(10):
        t_x = 210 + i * 14
        dx = (t_x - 250) / 190.0
        t_y = 175 - 110 * (1.0 - dx * dx) - 8

        painter.setBrush(QColor(175, 175, 175))
        painter.drawRoundedRect(t_x, int(t_y), 11, 14, 2, 2)
        painter.setBrush(QColor(140, 140, 140))
        painter.drawEllipse(t_x + 2, int(t_y) + 14, 7, 18)

    painter.setBrush(QColor(10, 10, 10))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(185, 130, 8, 25)

    painter.setPen(QColor(200, 200, 200))
    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    painter.drawText(20, 30, "L")
    painter.drawText(width - 30, 30, "R")
    painter.drawText(20, height - 20, "PANORAMIC OPG")

    painter.end()

    ba = QBuffer()
    ba.open(QBuffer.OpenModeFlag.WriteOnly)
    img.save(ba, "PNG")
    return ba.data().data()
