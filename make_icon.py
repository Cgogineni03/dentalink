import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter, QColor, QLinearGradient, QPainterPath, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF
from PIL import Image

def generate_app_icon():
    app = QApplication(sys.argv)
    
    size = 256
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 1. Background Rounded Square Badge (Modern App Icon)
    rect = QRectF(12, 12, size - 24, size - 24)
    bg_gradient = QLinearGradient(0, 0, size, size)
    bg_gradient.setColorAt(0.0, QColor("#0f172a")) # Dark slate
    bg_gradient.setColorAt(0.5, QColor("#0369a1")) # Deep medical blue
    bg_gradient.setColorAt(1.0, QColor("#0284c7")) # Bright cyan-blue
    
    painter.setBrush(QBrush(bg_gradient))
    painter.setPen(QPen(QColor("#38bdf8"), 3)) # Cyan border glow
    painter.drawRoundedRect(rect, 48, 48)
    
    # 2. Draw Tooth Silhouette Path
    tooth_path = QPainterPath()
    # Top crown curves of molar tooth
    tooth_path.moveTo(80, 85)
    tooth_path.cubicTo(80, 60, 115, 60, 128, 75)  # Left cusp
    tooth_path.cubicTo(141, 60, 176, 60, 176, 85)  # Right cusp
    # Outer right body curve
    tooth_path.cubicTo(185, 110, 180, 145, 168, 175)
    # Right root curve
    tooth_path.cubicTo(160, 200, 148, 215, 142, 215)
    tooth_path.cubicTo(138, 215, 134, 190, 128, 150) # Root bifurcation notch
    # Left root curve
    tooth_path.cubicTo(122, 190, 118, 215, 114, 215)
    tooth_path.cubicTo(108, 215, 96, 200, 88, 175)
    # Outer left body curve
    tooth_path.cubicTo(76, 145, 71, 110, 80, 85)
    
    # Fill Tooth with pristine white / light cyan gradient
    tooth_grad = QLinearGradient(128, 60, 128, 215)
    tooth_grad.setColorAt(0.0, QColor("#FFFFFF"))
    tooth_grad.setColorAt(1.0, QColor("#E0F2FE"))
    
    painter.setBrush(QBrush(tooth_grad))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPath(tooth_path)
    
    # 3. Medical Cross / Link Badge on Tooth Center
    cx, cy = 128, 110
    cross_path = QPainterPath()
    w, h = 8, 24
    # Horizontal arm
    cross_path.addRoundedRect(QRectF(cx - h/2, cy - w/2, h, w), 3, 3)
    # Vertical arm
    cross_path.addRoundedRect(QRectF(cx - w/2, cy - h/2, w, h), 3, 3)
    
    painter.setBrush(QBrush(QColor("#0284c7")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPath(cross_path)
    
    # 4. Subtle Shading Sparkle
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    painter.drawEllipse(155, 80, 8, 8)
    
    painter.end()
    
    # Save PNG
    img.save("app_icon.png", "PNG")
    print("  Saved app_icon.png (256x256)")
    
    # Convert PNG to multi-resolution ICO using Pillow
    pil_img = Image.open("app_icon.png")
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    pil_img.save("app_icon.ico", format="ICO", sizes=icon_sizes)
    print("  Saved app_icon.ico (Multi-size: 16x16 to 256x256)")

if __name__ == "__main__":
    generate_app_icon()
