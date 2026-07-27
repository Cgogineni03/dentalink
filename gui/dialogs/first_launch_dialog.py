# First Launch Clinic & Doctor Setup Wizard Dialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import database
from gui.dialogs.universal_key_dialog import UniversalKeyDisplayDialog
from gui.styles import get_theme_stylesheet, load_theme_setting


class FirstLaunchSetupDialog(QDialog):
    """Wizard dialog for initial clinic configuration and doctor onboarding."""

    def __init__(self, start_step=1, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setup Wizard" if start_step == 1 else "Add Doctor Account")
        self.setFixedSize(460, 560)
        self.start_step = start_step
        theme_name = load_theme_setting()
        self.setStyleSheet(get_theme_stylesheet(theme_name))

        self.saved_admin_username = None
        self.saved_admin_password = None
        self.saved_doctor_username = None
        self.saved_doctor_password = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        self.lbl_header_title = QLabel("DentaLink Setup Wizard")
        self.lbl_header_title.setFont(QFont("Ubuntu", 15, QFont.Weight.Bold))
        self.lbl_header_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_header_title.setStyleSheet("color: #0371bb; margin-bottom: 2px;")
        main_layout.addWidget(self.lbl_header_title)

        self.step_indicator_widget = QWidget()
        step_ind_layout = QHBoxLayout(self.step_indicator_widget)
        step_ind_layout.setContentsMargins(0, 0, 0, 8)

        self.lbl_step1_ind = QLabel("Step 1: Clinic Setup")
        self.lbl_step1_ind.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_step1_ind.setFont(QFont("Ubuntu", 10, QFont.Weight.Bold))

        lbl_arrow = QLabel("➔")
        lbl_arrow.setStyleSheet("color: #64748B; font-weight: bold;")

        self.lbl_step2_ind = QLabel("Step 2: Doctor Setup")
        self.lbl_step2_ind.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_step2_ind.setFont(QFont("Ubuntu", 10, QFont.Weight.Bold))

        step_ind_layout.addWidget(self.lbl_step1_ind)
        step_ind_layout.addWidget(lbl_arrow)
        step_ind_layout.addWidget(self.lbl_step2_ind)

        if self.start_step == 2:
            self.step_indicator_widget.hide()

        main_layout.addWidget(self.step_indicator_widget)

        self.stack = QStackedWidget()

        # --- PAGE 1: STEP 1 (Clinic Profile & Admin Account) ---
        page1 = QWidget()
        page1_layout = QVBoxLayout(page1)
        page1_layout.setContentsMargins(0, 0, 0, 0)
        page1_layout.setSpacing(10)

        lbl_p1_subtitle = QLabel("Step 1 of 2: Clinic Profile & Admin Account Details")
        lbl_p1_subtitle.setWordWrap(True)
        lbl_p1_subtitle.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 11px;")
        page1_layout.addWidget(lbl_p1_subtitle)

        form_p1 = QFormLayout()
        form_p1.setVerticalSpacing(10)

        existing_clinic = database.get_clinic_details()
        default_clinic_name = existing_clinic.get('name', '') if existing_clinic else ''
        if default_clinic_name == "Dental Care & Specialty Clinic":
            default_clinic_name = ""

        self.clinic_name_input = QLineEdit(default_clinic_name)
        self.clinic_name_input.setPlaceholderText("Clinic Display Name (e.g. Apollo Dental)")
        form_p1.addRow("Clinic Name:", self.clinic_name_input)

        self.clinic_user_input = QLineEdit("admin")
        self.clinic_user_input.setPlaceholderText("Clinic Login Username")
        form_p1.addRow("Admin Username:", self.clinic_user_input)

        self.clinic_pwd_input = QLineEdit()
        self.clinic_pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.clinic_pwd_input.setPlaceholderText("Admin Password")
        form_p1.addRow("Admin Password:", self.clinic_pwd_input)

        self.clinic_pwd_confirm = QLineEdit()
        self.clinic_pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.clinic_pwd_confirm.setPlaceholderText("Confirm Admin Password")
        form_p1.addRow("Confirm Password:", self.clinic_pwd_confirm)

        page1_layout.addLayout(form_p1)

        self.error_p1 = QLabel("")
        self.error_p1.setStyleSheet("color: #EF4444; font-size: 11px;")
        self.error_p1.setWordWrap(True)
        page1_layout.addWidget(self.error_p1)
        page1_layout.addStretch()

        btn_next = QPushButton("Next: Doctor Account Setup ➔")
        btn_next.setObjectName("PrimaryBtn")
        btn_next.clicked.connect(self.submit_step_1)
        page1_layout.addWidget(btn_next)

        self.stack.addWidget(page1)

        # --- PAGE 2: STEP 2 (Doctor Account & Recovery) ---
        page2 = QWidget()
        page2_layout = QVBoxLayout(page2)
        page2_layout.setContentsMargins(0, 0, 0, 0)
        page2_layout.setSpacing(8)

        lbl_p2_subtitle = QLabel("Step 2: Doctor Profile & Emergency Security Questions")
        lbl_p2_subtitle.setWordWrap(True)
        lbl_p2_subtitle.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 11px;")
        page2_layout.addWidget(lbl_p2_subtitle)

        form_p2 = QFormLayout()
        form_p2.setVerticalSpacing(8)

        default_doc_user = "dr_admin" if self.start_step == 1 else ""
        self.doctor_name_input = QLineEdit()
        self.doctor_name_input.setPlaceholderText("Doctor Full Name (e.g. Dr. John Smith)")
        form_p2.addRow("Doctor Name:", self.doctor_name_input)

        self.doctor_user_input = QLineEdit(default_doc_user)
        self.doctor_user_input.setPlaceholderText("Doctor Login Username")
        form_p2.addRow("Doctor Username:", self.doctor_user_input)

        self.doctor_pwd_input = QLineEdit()
        self.doctor_pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.doctor_pwd_input.setPlaceholderText("Doctor Password")
        form_p2.addRow("Doctor Password:", self.doctor_pwd_input)

        self.doctor_pwd_confirm = QLineEdit()
        self.doctor_pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.doctor_pwd_confirm.setPlaceholderText("Confirm Doctor Password")
        form_p2.addRow("Confirm Password:", self.doctor_pwd_confirm)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        form_p2.addRow(separator2)

        self.q1_input = QLineEdit("What was the name of your first school/college?")
        form_p2.addRow("Security Q1:", self.q1_input)
        self.a1_input = QLineEdit()
        self.a1_input.setPlaceholderText("Answer 1 (Case-insensitive)")
        form_p2.addRow("Answer Q1:", self.a1_input)

        self.q2_input = QLineEdit("What city were you born in?")
        form_p2.addRow("Security Q2:", self.q2_input)
        self.a2_input = QLineEdit()
        self.a2_input.setPlaceholderText("Answer Q2 (Case-insensitive)")
        form_p2.addRow("Answer Q2:", self.a2_input)

        page2_layout.addLayout(form_p2)

        self.error_p2 = QLabel("")
        self.error_p2.setStyleSheet("color: #EF4444; font-size: 11px;")
        self.error_p2.setWordWrap(True)
        page2_layout.addWidget(self.error_p2)

        p2_btn_layout = QHBoxLayout()
        self.btn_back = QPushButton("⬅ Back to Step 1")
        self.btn_back.clicked.connect(self.go_to_step_1)
        if self.start_step == 2:
            self.btn_back.hide()

        self.btn_complete_step2 = QPushButton("Complete Setup & Create Doctor" if self.start_step == 1 else "Create Doctor Account")
        self.btn_complete_step2.setObjectName("PrimaryBtn")
        self.btn_complete_step2.clicked.connect(self.submit_step_2)

        p2_btn_layout.addWidget(self.btn_back)
        p2_btn_layout.addWidget(self.btn_complete_step2)
        page2_layout.addLayout(p2_btn_layout)

        self.stack.addWidget(page2)
        main_layout.addWidget(self.stack)

        self.setModal(True)

        if self.start_step == 2:
            self.switch_page(1)
        else:
            self.switch_page(0)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.lbl_step1_ind.setStyleSheet("color: #38BDF8; background-color: #0F172A; border-radius: 4px; padding: 4px 8px;")
            self.lbl_step2_ind.setStyleSheet("color: #64748B; padding: 4px 8px;")
        else:
            self.lbl_step1_ind.setStyleSheet("color: #10B981; padding: 4px 8px;")
            self.lbl_step2_ind.setStyleSheet("color: #38BDF8; background-color: #0F172A; border-radius: 4px; padding: 4px 8px;")

    def submit_step_1(self):
        clinic_name = self.clinic_name_input.text().strip()
        clinic_user = self.clinic_user_input.text().strip()
        clinic_pwd = self.clinic_pwd_input.text()
        clinic_pwd_confirm = self.clinic_pwd_confirm.text()

        if not clinic_name or not clinic_user or not clinic_pwd:
            self.error_p1.setText("Clinic name, username, and password are required.")
            return
        if clinic_pwd != clinic_pwd_confirm:
            self.error_p1.setText("Admin passwords do not match.")
            return

        if not database.has_clinics():
            if not database.create_clinic(clinic_name, clinic_user, clinic_pwd):
                self.error_p1.setText("Clinic username already exists. Choose a different username.")
                return
        else:
            database.update_clinic_profile('admin', clinic_name, clinic_user, clinic_pwd)

        database.unlock_database_with_login(clinic_user, clinic_pwd)
        self.saved_admin_username = clinic_user
        self.saved_admin_password = clinic_pwd
        self.error_p1.setText("")
        self.switch_page(1)

    def go_to_step_1(self):
        self.switch_page(0)

    def submit_step_2(self):
        doctor_name = self.doctor_name_input.text().strip()
        doctor_user = self.doctor_user_input.text().strip()
        doctor_pwd = self.doctor_pwd_input.text()
        doctor_pwd_confirm = self.doctor_pwd_confirm.text()

        q1 = self.q1_input.text().strip() or "What was the name of your first school/college?"
        a1 = self.a1_input.text().strip()
        q2 = self.q2_input.text().strip() or "What city were you born in?"
        a2 = self.a2_input.text().strip()

        if not doctor_name or not doctor_user or not doctor_pwd:
            self.error_p2.setText("Doctor name, username, and password are required.")
            return
        if doctor_pwd != doctor_pwd_confirm:
            self.error_p2.setText("Doctor passwords do not match.")
            return
        if not a1 or not a2:
            self.error_p2.setText("Please provide answers to both security questions for emergency password recovery.")
            return

        if not database.create_doctor(doctor_name, doctor_user, doctor_pwd, 0.0):
            self.error_p2.setText("Doctor username already exists. Choose a different username.")
            return

        universal_key = database.generate_universal_recovery_key()
        database.unlock_database_with_login(doctor_user, doctor_pwd)
        database.setup_doctor_security_and_recovery(
            doctor_user,
            q1, a1,
            q2, a2,
            universal_key
        )

        self.saved_doctor_username = doctor_user
        self.saved_doctor_password = doctor_pwd

        key_dlg = UniversalKeyDisplayDialog(universal_key, self)
        key_dlg.exec()

        self.accept()
