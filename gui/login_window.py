# Doctor Login Window Screen
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

import database
from gui.dialogs.forgot_password_dialog import ForgotPasswordDialog
from gui.styles import get_theme_stylesheet, load_theme_setting


class LoginWindow(QDialog):
    """Application authentication login window."""

    def __init__(self, default_username="", default_password=""):
        super().__init__()
        self.setWindowTitle("Doctor Login")
        self.setFixedSize(380, 240)
        theme_name = load_theme_setting()
        self.setStyleSheet(get_theme_stylesheet(theme_name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)

        title = QLabel("DentaLink Access")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #0371bb; margin-bottom: 10px;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)

        self.username_input = QLineEdit(default_username or "dr_admin")
        self.username_input.setPlaceholderText("Doctor Username")
        form_layout.addRow("Username:", self.username_input)

        self.password_input = QLineEdit(default_password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        btn_row = QHBoxLayout()
        self.btn_login = QPushButton("Login")
        self.btn_login.setObjectName("PrimaryBtn")
        self.btn_login.clicked.connect(self.attempt_login)

        self.btn_forgot_password = QPushButton("Forgot Password?")
        self.btn_forgot_password.setStyleSheet("color: #0371bb; text-decoration: underline; background: transparent; border: none; font-size: 11px;")
        self.btn_forgot_password.clicked.connect(self.open_forgot_password)

        btn_row.addWidget(self.btn_login)
        btn_row.addWidget(self.btn_forgot_password)
        layout.addLayout(btn_row)

        self.password_input.setFocus()

    def open_forgot_password(self):
        dlg = ForgotPasswordDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.password_input.clear()
            self.password_input.setFocus()

    def attempt_login(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text()

        session = database.verify_password(user, pwd)
        if session:
            database.unlock_database_with_login(user, pwd)
            self.logged_in_session = session
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()
