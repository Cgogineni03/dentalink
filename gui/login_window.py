# Doctor Login Window Screen
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import database
from gui.dialogs.forgot_password_dialog import ForgotPasswordDialog
from gui.styles import get_theme_stylesheet, load_theme_setting


class LoginWindow(QDialog):
    """Application authentication login window."""

    def __init__(self, default_username="", default_password=""):
        super().__init__()
        self.setWindowTitle("Doctor Login")
        self.setFixedSize(480, 360)
        theme_name = load_theme_setting()
        self.setStyleSheet(get_theme_stylesheet(theme_name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(20)

        title = QLabel("DentaLink Access")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #0371bb; margin-bottom: 10px;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(18)

        # User Selection Container
        user_container = QWidget()
        user_vbox = QVBoxLayout(user_container)
        user_vbox.setContentsMargins(0, 0, 0, 0)
        user_vbox.setSpacing(8)

        self.user_combo = QComboBox()
        self.user_combo.setStyleSheet("font-size: 14px; padding: 8px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username or Admin Account")
        self.username_input.setStyleSheet("font-size: 14px; padding: 8px;")

        user_vbox.addWidget(self.user_combo)
        user_vbox.addWidget(self.username_input)

        lbl_user = QLabel("User:")
        lbl_user.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))

        form_layout.addRow(lbl_user, user_container)

        self.password_input = QLineEdit(default_password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("font-size: 14px; padding: 8px;")

        lbl_pwd = QLabel("Password:")
        lbl_pwd.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))

        form_layout.addRow(lbl_pwd, self.password_input)

        layout.addLayout(form_layout)

        # Populate users dropdown
        self._populate_user_dropdown(default_username)

        self.user_combo.currentIndexChanged.connect(self._on_user_changed)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)

        self.btn_login = QPushButton("Login")
        self.btn_login.setObjectName("PrimaryBtn")
        self.btn_login.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px 20px; min-height: 38px;")
        self.btn_login.clicked.connect(self.attempt_login)

        self.btn_forgot_password = QPushButton("Forgot Password?")
        self.btn_forgot_password.setStyleSheet("color: #0371bb; text-decoration: underline; background: transparent; border: none; font-size: 13px;")
        self.btn_forgot_password.clicked.connect(self.open_forgot_password)

        btn_row.addWidget(self.btn_login)
        btn_row.addWidget(self.btn_forgot_password)
        layout.addLayout(btn_row)

        if self.username_input.isVisible() and not self.username_input.text():
            self.username_input.setFocus()
        else:
            self.password_input.setFocus()

    def _populate_user_dropdown(self, default_username=""):
        self.user_combo.blockSignals(True)
        self.user_combo.clear()

        # Fetch doctors from database
        doctors = database.get_doctors()
        admin_usernames = {"dr_admin", "admin"}
        try:
            clinic_profile = database.get_clinic_profile("admin")
            if clinic_profile and clinic_profile.get("username"):
                admin_usernames.add(clinic_profile.get("username").lower())
        except Exception:
            pass

        added_doctors = False
        default_index = -1

        for doc in doctors:
            uname = doc.get("username", "")
            if uname.lower() in admin_usernames:
                continue
            name = doc.get("name", uname)
            display_text = f"{name} ({uname})" if name != uname else uname
            idx = self.user_combo.count()
            self.user_combo.addItem(display_text, uname)
            added_doctors = True

            if default_username and uname.lower() == default_username.lower():
                default_index = idx

        # Add Others option
        others_idx = self.user_combo.count()
        self.user_combo.addItem("Others...", "__others__")

        if default_username:
            if default_index != -1:
                self.user_combo.setCurrentIndex(default_index)
                self.username_input.hide()
            else:
                self.user_combo.setCurrentIndex(others_idx)
                self.username_input.setText(default_username)
                self.username_input.show()
        else:
            if added_doctors:
                self.user_combo.setCurrentIndex(0)
                self.username_input.hide()
            else:
                self.user_combo.setCurrentIndex(others_idx)
                self.username_input.show()

        self.user_combo.blockSignals(False)

    def _on_user_changed(self, index):
        data = self.user_combo.itemData(index)
        if data == "__others__":
            self.username_input.show()
            self.username_input.setFocus()
        else:
            self.username_input.hide()
            self.password_input.setFocus()

    def open_forgot_password(self):
        dlg = ForgotPasswordDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.password_input.clear()
            self.password_input.setFocus()

    def attempt_login(self):
        selected_data = self.user_combo.currentData()
        if selected_data == "__others__":
            user = self.username_input.text().strip()
        else:
            user = selected_data or self.user_combo.currentText().strip()

        pwd = self.password_input.text()

        if not user:
            QMessageBox.warning(self, "Login Failed", "Please enter or select a username.")
            return

        session = database.verify_password(user, pwd)
        if session:
            database.unlock_database_with_login(user, pwd)
            self.logged_in_session = session
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()

