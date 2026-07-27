# Universal Recovery Key Safeguard Dialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from gui.styles import get_theme_stylesheet, load_theme_setting


class UniversalKeyDisplayDialog(QDialog):
    """Dialog presenting the generated Universal Emergency Recovery Key."""

    def __init__(self, universal_key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CRITICAL: Universal Emergency Recovery Key")
        self.setFixedSize(460, 370)
        self.universal_key = universal_key
        theme_name = load_theme_setting()
        self.setStyleSheet(get_theme_stylesheet(theme_name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        lbl_warn = QLabel("⚠️ UNIVERSAL RECOVERY KEY SAFEGUARD")
        lbl_warn.setFont(QFont("Ubuntu", 14, QFont.Weight.Bold))
        lbl_warn.setStyleSheet("color: #f59e0b; margin-bottom: 5px;")
        layout.addWidget(lbl_warn)

        lbl_desc = QLabel(
            "This is your clinic's Master Universal Emergency Key. "
            "If a doctor forgets their password, this key combined with security answers "
            "is the ONLY way to recover access without losing encrypted patient data.\n\n"
            "Please copy or save this key in a secure location (e.g. printed in a vault or password manager):"
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #cbd5e1; font-size: 11px;")
        layout.addWidget(lbl_desc)

        key_box = QLineEdit(universal_key)
        key_box.setReadOnly(True)
        key_box.setFont(QFont("Courier", 16, QFont.Weight.Bold))
        key_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_box.setStyleSheet("background-color: #0f172a; color: #38bdf8; border: 2px solid #0284c7; border-radius: 8px; padding: 8px;")
        layout.addWidget(key_box)

        btn_layout = QHBoxLayout()
        btn_copy = QPushButton("Copy to Clipboard")
        btn_copy.clicked.connect(self.copy_to_clipboard)
        btn_save = QPushButton("Save to File")
        btn_save.clicked.connect(self.save_to_file)
        btn_layout.addWidget(btn_copy)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        self.chk_confirm = QCheckBox("I have copied and saved this Emergency Key in a safe place.")
        self.chk_confirm.setStyleSheet("color: #f43f5e; font-weight: bold; font-size: 11px;")
        self.chk_confirm.toggled.connect(self.on_toggle_confirm)
        layout.addWidget(self.chk_confirm)

        self.btn_finish = QPushButton("Complete Setup")
        self.btn_finish.setObjectName("SuccessBtn")
        self.btn_finish.setEnabled(False)
        self.btn_finish.clicked.connect(self.accept)
        layout.addWidget(self.btn_finish)

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.universal_key)
        QMessageBox.information(self, "Copied", "Universal Recovery Key copied to clipboard.")

    def save_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Universal Recovery Key", "UNIVERSAL_RECOVERY_KEY.txt", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "w") as f:
                    f.write(f"DENTALINK UNIVERSAL RECOVERY KEY\nKey: {self.universal_key}\nKeep this file strictly confidential.\n")
                QMessageBox.information(self, "Saved", f"Universal Recovery Key saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def on_toggle_confirm(self, checked):
        self.btn_finish.setEnabled(checked)
