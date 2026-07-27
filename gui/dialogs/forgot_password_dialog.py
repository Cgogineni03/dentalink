# Forgot Password Recovery Dialog
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

import database
from gui.styles import get_theme_stylesheet, load_theme_setting


class ForgotPasswordDialog(QDialog):
    """Dialog allowing doctors to recover account access using security answers + Universal Key."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Doctor Account Password Recovery")
        self.setFixedSize(430, 420)
        theme_name = load_theme_setting()
        self.setStyleSheet(get_theme_stylesheet(theme_name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("2-Factor Password Recovery")
        title.setFont(QFont("Ubuntu", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #0371bb;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)

        self.txt_username = QLineEdit("dr_admin")
        self.txt_username.editingFinished.connect(self.on_username_changed)
        form_layout.addRow("Doctor Username:", self.txt_username)

        self.lbl_q1 = QLabel("Question 1: First school/college?")
        self.lbl_q1.setWordWrap(True)
        self.lbl_q1.setStyleSheet("color: #94a3b8; font-size: 11px;")
        form_layout.addRow(self.lbl_q1)
        self.txt_a1 = QLineEdit()
        self.txt_a1.setPlaceholderText("Answer 1 (Case-insensitive)")
        form_layout.addRow("Answer 1:", self.txt_a1)

        self.lbl_q2 = QLabel("Question 2: City born in?")
        self.lbl_q2.setWordWrap(True)
        self.lbl_q2.setStyleSheet("color: #94a3b8; font-size: 11px;")
        form_layout.addRow(self.lbl_q2)
        self.txt_a2 = QLineEdit()
        self.txt_a2.setPlaceholderText("Answer 2 (Case-insensitive)")
        form_layout.addRow("Answer 2:", self.txt_a2)

        self.txt_universal_key = QLineEdit()
        self.txt_universal_key.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        form_layout.addRow("Universal Key:", self.txt_universal_key)

        self.txt_new_pwd = QLineEdit()
        self.txt_new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_pwd.setPlaceholderText("New Password")
        form_layout.addRow("New Password:", self.txt_new_pwd)

        layout.addLayout(form_layout)

        self.btn_reset = QPushButton("Reset Password & Restore Access")
        self.btn_reset.setObjectName("SuccessBtn")
        self.btn_reset.clicked.connect(self.attempt_recovery)
        layout.addWidget(self.btn_reset)

        self.on_username_changed()

    def on_username_changed(self):
        user = self.txt_username.text().strip()
        if user:
            q1, q2 = database.get_doctor_security_questions(user)
            self.lbl_q1.setText(f"Question 1: {q1}")
            self.lbl_q2.setText(f"Question 2: {q2}")

    def attempt_recovery(self):
        user = self.txt_username.text().strip()
        a1 = self.txt_a1.text()
        a2 = self.txt_a2.text()
        ukey = self.txt_universal_key.text().strip()
        new_pwd = self.txt_new_pwd.text()

        if not user or not a1 or not a2 or not ukey or not new_pwd:
            QMessageBox.warning(self, "Incomplete", "Please complete all recovery fields.")
            return

        if database.reset_password_with_recovery(user, a1, a2, ukey, new_pwd):
            QMessageBox.information(self, "Success", "Password reset successfully!\nYour Master Key and patient records have been restored.")
            self.accept()
        else:
            QMessageBox.critical(self, "Recovery Failed", "Invalid Security Answers or Universal Recovery Key.\nPlease check your inputs and try again.")
