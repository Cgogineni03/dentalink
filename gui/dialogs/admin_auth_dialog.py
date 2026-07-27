# Admin Account Authentication Dialog
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

import database
from gui.styles import get_theme_stylesheet, load_theme_setting


class AdminAuthDialog(QDialog):
    """Dialog prompting for clinic admin password authentication."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Account Authentication")
        self.setFixedSize(380, 240)
        theme_name = load_theme_setting()
        self.setStyleSheet(get_theme_stylesheet(theme_name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        lbl_title = QLabel("🔒 Admin Authentication Required")
        lbl_title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #0371bb;")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel("Please enter the Clinic Admin password to proceed with adding a new doctor.")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(lbl_desc)

        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Admin Password")
        layout.addWidget(self.pwd_input)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #EF4444; font-size: 11px;")
        layout.addWidget(self.lbl_error)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_confirm = QPushButton("Authenticate")
        btn_confirm.setObjectName("PrimaryBtn")
        btn_confirm.clicked.connect(self.attempt_auth)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)
        layout.addLayout(btn_layout)

        self.pwd_input.returnPressed.connect(self.attempt_auth)

    def attempt_auth(self):
        pwd = self.pwd_input.text()
        if not pwd:
            self.lbl_error.setText("Password is required.")
            return
        if database.verify_admin_password(pwd):
            self.accept()
        else:
            self.lbl_error.setText("Invalid Admin Password. Access denied.")
