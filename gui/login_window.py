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
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import database
from gui.dialogs.forgot_password_dialog import ForgotPasswordDialog
from gui.styles import get_theme_stylesheet, load_theme_setting, detect_system_accent_colors, get_effective_theme_name


class LoginWindow(QDialog):
    """Application authentication login window."""

    def __init__(self, default_username="", default_password=""):
        super().__init__()
        self.setWindowTitle("Doctor Login")
        self.setFixedSize(500, 320)
        theme_name = load_theme_setting()
        effective_theme = get_effective_theme_name(theme_name)
        primary_accent, _ = detect_system_accent_colors(effective_theme)
        self.setStyleSheet(get_theme_stylesheet(theme_name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("DentaLink Access")
        title.setFont(QFont("Ubuntu", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {primary_accent}; margin-bottom: 15px;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(18)

        # Container stack for username input (Index 0: QComboBox, Index 1: QLineEdit text input)
        self.user_stack = QStackedWidget()

        # Index 0: QComboBox for available users
        self.user_combo = QComboBox()
        self.user_combo.setStyleSheet("font-size: 14px; min-height: 38px; padding: 4px 8px;")

        # Index 1: Text Box for custom / admin username input
        self.text_container = QWidget()
        text_layout = QHBoxLayout(self.text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username (e.g. dr_admin)")
        self.username_input.setStyleSheet("font-size: 14px; min-height: 38px; padding: 4px 8px;")

        self.btn_back_to_combo = QPushButton("Users")
        self.btn_back_to_combo.setToolTip("Switch back to available users list")
        self.btn_back_to_combo.setStyleSheet("font-size: 13px; min-height: 38px; padding: 4px 10px;")
        self.btn_back_to_combo.clicked.connect(self.show_user_list)

        text_layout.addWidget(self.username_input)
        text_layout.addWidget(self.btn_back_to_combo)

        self.user_stack.addWidget(self.user_combo)
        self.user_stack.addWidget(self.text_container)

        lbl_user = QLabel("Username:")
        lbl_user.setStyleSheet("font-size: 14px; font-weight: 600;")
        form_layout.addRow(lbl_user, self.user_stack)

        self.password_input = QLineEdit(default_password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("font-size: 14px; min-height: 38px; padding: 4px 8px;")

        lbl_pass = QLabel("Password:")
        lbl_pass.setStyleSheet("font-size: 14px; font-weight: 600;")
        form_layout.addRow(lbl_pass, self.password_input)

        layout.addLayout(form_layout)

        btn_row = QHBoxLayout()
        self.btn_login = QPushButton("Login")
        self.btn_login.setObjectName("PrimaryBtn")
        self.btn_login.setStyleSheet("font-size: 15px; min-height: 40px; font-weight: bold;")
        self.btn_login.clicked.connect(self.attempt_login)

        self.btn_forgot_password = QPushButton("Forgot Password?")
        self.btn_forgot_password.setStyleSheet(
            f"color: {primary_accent}; text-decoration: underline; background: transparent; border: none; font-size: 13px;"
        )
        self.btn_forgot_password.clicked.connect(self.open_forgot_password)

        btn_row.addWidget(self.btn_login)
        btn_row.addWidget(self.btn_forgot_password)
        layout.addLayout(btn_row)

        self._populate_users(default_username)

        # Connect combo selection change signal
        self.user_combo.currentIndexChanged.connect(self.on_user_combo_changed)

        # Focus appropriate field
        if self.user_stack.currentIndex() == 1:
            if not self.username_input.text():
                self.username_input.setFocus()
            else:
                self.password_input.setFocus()
        else:
            self.password_input.setFocus()

    def _populate_users(self, default_username=""):
        """Populates the dropdown with non-admin doctors and an 'Others' entry."""
        all_doctors = database.get_doctors()

        # Filter out admin accounts so admin is not listed in dropdown
        non_admin_doctors = [
            d for d in all_doctors
            if (d.get('username') or '').lower() not in ('admin', 'dr_admin', 'dr.admin')
            and not d.get('is_admin', False)
            and (d.get('name') or '').lower() != 'dr. admin'
        ]

        has_available_doctors = len(non_admin_doctors) > 0

        for doc in non_admin_doctors:
            doc_name = doc.get('name', '')
            doc_uname = doc.get('username', '')
            display_str = f"{doc_name} ({doc_uname})" if doc_name and doc_name != doc_uname else doc_uname
            self.user_combo.addItem(display_str, userData=doc_uname)

        # Always add 'Others' option at the end
        self.user_combo.addItem("Others...", userData="__OTHERS__")

        if default_username:
            # Check if default_username matches a doctor in combo
            idx = -1
            for i in range(self.user_combo.count()):
                if self.user_combo.itemData(i) == default_username:
                    idx = i
                    break

            if idx >= 0 and self.user_combo.itemData(idx) != "__OTHERS__":
                self.user_combo.setCurrentIndex(idx)
                self.user_stack.setCurrentIndex(0)
            else:
                # Username is admin or custom, switch to text input mode
                others_idx = self.user_combo.findData("__OTHERS__")
                if others_idx >= 0:
                    self.user_combo.setCurrentIndex(others_idx)
                self.username_input.setText(default_username)
                self.user_stack.setCurrentIndex(1)
        else:
            if has_available_doctors:
                self.user_combo.setCurrentIndex(0)
                self.user_stack.setCurrentIndex(0)
            else:
                others_idx = self.user_combo.findData("__OTHERS__")
                if others_idx >= 0:
                    self.user_combo.setCurrentIndex(others_idx)
                self.user_stack.setCurrentIndex(1)

    def on_user_combo_changed(self, index):
        """Handler when user changes selection in the dropdown menu."""
        if self.user_combo.currentData() == "__OTHERS__":
            self.user_stack.setCurrentIndex(1)
            self.username_input.setFocus()
            self.username_input.selectAll()

    def show_user_list(self):
        """Switches back to the dropdown list if available doctor users exist."""
        if self.user_combo.count() > 1:
            self.user_combo.setCurrentIndex(0)
            self.user_stack.setCurrentIndex(0)
            self.user_combo.setFocus()
        else:
            self.username_input.setFocus()

    def get_selected_username(self):
        """Returns the username to be used for authentication."""
        if self.user_stack.currentIndex() == 1:
            return self.username_input.text().strip()

        current_data = self.user_combo.currentData()
        if current_data == "__OTHERS__":
            return self.username_input.text().strip()
        return (current_data or self.user_combo.currentText()).strip()

    def open_forgot_password(self):
        dlg = ForgotPasswordDialog(self)
        current_user = self.get_selected_username()
        if current_user:
            dlg.txt_username.setText(current_user)
            dlg.on_username_changed()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.password_input.clear()
            self.password_input.setFocus()

    def attempt_login(self):
        user = self.get_selected_username()
        pwd = self.password_input.text()

        if not user:
            QMessageBox.warning(self, "Login Failed", "Please select or enter a username.")
            if self.user_stack.currentIndex() == 1:
                self.username_input.setFocus()
            else:
                self.user_combo.setFocus()
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

