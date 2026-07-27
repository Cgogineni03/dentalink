# DentaLink Main Application Window Architecture
import os
import shutil
import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QFrame, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLineEdit, QComboBox, QDateEdit, QTextEdit, QTabWidget, 
    QFormLayout, QMessageBox, QGroupBox, QDialog, QFileDialog, QGridLayout, 
    QCheckBox, QSplitter, QScrollArea, QListWidget, QListWidgetItem, QTextBrowser
)
from PyQt6.QtCore import Qt, QDate, pyqtSlot, QRect, QRectF, pyqtSignal, QPointF, QSize
from PyQt6.QtGui import QFont, QIcon, QPainter, QPixmap, QColor, QPen
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

import database
from gui.styles import load_theme_setting, get_theme_stylesheet, save_theme_setting
from gui.components.clickable_label import ClickableLabel
from gui.components.file_uploader import FileUploaderWidget
from gui.components.icon_helpers import create_sidebar_toggle_icon
from gui.dialogs.treatment_done_dialog import ViewTreatmentDoneDialog
from gui.dialogs.version_history_dialog import FullVersionHistoryDialog
from gui.dialogs.admin_auth_dialog import AdminAuthDialog
from gui.dialogs.first_launch_dialog import FirstLaunchSetupDialog
from gui.dialogs.universal_key_dialog import UniversalKeyDisplayDialog
from gui.dialogs.forgot_password_dialog import ForgotPasswordDialog
from widgets.dental_chart import DentalChartWidget
from widgets.xray_viewer import XrayViewerWidget

class DentaLinkMainWindow(QMainWindow):
    def __init__(self, doctor_session=None):
        super().__init__()
        # Use default Dr. Admin session if none supplied
        self.doctor_session = doctor_session or {'id': 1, 'name': 'Dr. Admin', 'username': 'dr_admin'}
        self.setWindowTitle("DentaLink - Patient Management System")
        self.setMinimumSize(1100, 700)
        
        self.current_patient_id = None
        self.init_ui()
        
        self.current_theme = load_theme_setting()
        self.apply_theme(self.current_theme)

    def init_ui(self):
        # Central widget holds the main layout (sidebar + dynamic stacked content)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar Navigation
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 10, 15, 20)
        sidebar_layout.setSpacing(8)

        # Logo/Title
        self.logo_lbl = ClickableLabel("DentaLink")
        self.logo_lbl.setObjectName("SidebarTitle")
        self.logo_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logo_lbl.clicked.connect(self.show_overview_page)
        sidebar_layout.addWidget(self.logo_lbl)

        # Sidebar Buttons Group
        self.btn_register = QPushButton("Register Patient")
        self.btn_register.setObjectName("SidebarBtn")
        self.btn_register.setCheckable(True)
        self.btn_register.setChecked(True)
        sidebar_layout.addWidget(self.btn_register)

        self.btn_new_op = QPushButton("New OP Queue")
        self.btn_new_op.setObjectName("SidebarBtn")
        self.btn_new_op.setCheckable(True)
        sidebar_layout.addWidget(self.btn_new_op)

        self.btn_patient_list = QPushButton("Patient List")
        self.btn_patient_list.setObjectName("SidebarBtn")
        self.btn_patient_list.setCheckable(True)
        sidebar_layout.addWidget(self.btn_patient_list)

        # Spacer to push setting/status to bottom
        sidebar_layout.addStretch()

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setObjectName("SidebarBtn")
        self.btn_settings.setCheckable(True)
        sidebar_layout.addWidget(self.btn_settings)

        # Group button check logic
        self.sidebar_group = [self.btn_register, self.btn_new_op, self.btn_patient_list, self.btn_settings]
        for btn in self.sidebar_group:
            btn.clicked.connect(self.on_sidebar_click)

        main_layout.addWidget(sidebar)

        # 2. Central Content Panel (QStackedWidget)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Initialize Views inside Stack
        self.init_register_view()
        self.init_new_op_view()
        self.init_patient_list_view()
        self.init_case_file_view()
        self.init_settings_view()
        self.init_overview_view()

        # Add Views to Stack
        self.content_stack.addWidget(self.register_widget)
        self.content_stack.addWidget(self.new_op_widget)
        self.content_stack.addWidget(self.patient_list_widget)
        self.content_stack.addWidget(self.case_file_widget)
        self.content_stack.addWidget(self.settings_widget)
        self.content_stack.addWidget(self.overview_widget)

        # Populate Doctor Comboboxes
        self.refresh_doctor_dropdowns()

        # Load initial logo
        self.update_clinic_logo()

        # Set default view to Overview Page
        self.show_overview_page()

    def on_sidebar_click(self):
        sender = self.sender()
        for btn in self.sidebar_group:
            btn.setChecked(btn == sender)

        if sender == self.btn_register:
            self.content_stack.setCurrentIndex(0)
        elif sender == self.btn_new_op:
            self.refresh_new_op_table()
            self.content_stack.setCurrentIndex(1)
        elif sender == self.btn_patient_list:
            self.refresh_patient_list_table()
            self.content_stack.setCurrentIndex(2)
        elif sender == self.btn_settings:
            self.content_stack.setCurrentIndex(4)

    def show_overview_page(self):
        for btn in self.sidebar_group:
            btn.setChecked(False)
        self.refresh_overview_pending_table()
        self.refresh_overview_appointments_table()
        self.content_stack.setCurrentIndex(5)

    def update_clinic_logo(self):
        logo_path = database.get_clinic_logo_path()
        self.logo_lbl.setStyleSheet("")
        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = px_scaled = pixmap.scaled(190, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_lbl.setPixmap(px_scaled)
            self.logo_lbl.setText("")
        else:
            self.logo_lbl.setPixmap(QPixmap())
            self.logo_lbl.setText("DentaLink")
            self.logo_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))

    def init_overview_view(self):
        self.overview_widget = QWidget()
        layout = QVBoxLayout(self.overview_widget)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        title = QLabel("Clinic Overview Dashboard")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #0EA5E9;")
        layout.addWidget(title)

        # 1. Section: Pending Patients
        pending_box = QGroupBox("Pending New Outpatients Queue")
        pending_layout = QVBoxLayout(pending_box)
        pending_layout.setContentsMargins(10, 10, 10, 10)

        self.table_overview_pending = QTableWidget()
        self.table_overview_pending.setColumnCount(6)
        self.table_overview_pending.setHorizontalHeaderLabels(["ID", "Name", "Gender", "Phone", "Date Registered", "Action"])
        self.table_overview_pending.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_overview_pending.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_overview_pending.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table_overview_pending.verticalHeader().setVisible(False)
        self.table_overview_pending.setMaximumHeight(200)
        pending_layout.addWidget(self.table_overview_pending)
        
        layout.addWidget(pending_box)

        # 2. Section: Upcoming Appointments
        app_box = QGroupBox("Next 10 Upcoming Appointments")
        app_layout = QVBoxLayout(app_box)
        app_layout.setContentsMargins(10, 10, 10, 10)

        self.table_overview_appointments = QTableWidget()
        self.table_overview_appointments.setColumnCount(6)
        self.table_overview_appointments.setHorizontalHeaderLabels(["Date", "Time", "Patient Name", "Phone", "Reason", "Action"])
        self.table_overview_appointments.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_overview_appointments.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table_overview_appointments.verticalHeader().setVisible(False)
        self.table_overview_appointments.setMaximumHeight(250)
        app_layout.addWidget(self.table_overview_appointments)

        layout.addWidget(app_box)
        layout.addStretch()

    def refresh_overview_pending_table(self):
        patients = database.get_new_op_patients()
        self.table_overview_pending.setRowCount(len(patients))
        for idx, p in enumerate(patients):
            self.table_overview_pending.setItem(idx, 0, QTableWidgetItem(f"P{p['id']:04d}"))
            self.table_overview_pending.setItem(idx, 1, QTableWidgetItem(p['name']))
            self.table_overview_pending.setItem(idx, 2, QTableWidgetItem(p['gender']))
            self.table_overview_pending.setItem(idx, 3, QTableWidgetItem(p['phone']))
            
            raw_ts = p['created_at']
            try:
                created_dt = datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    created_dt = datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    created_dt = datetime.now()
            self.table_overview_pending.setItem(idx, 4, QTableWidgetItem(created_dt.strftime("%Y-%m-%d %I:%M %p")))

            btn_open = QPushButton("Open File")
            btn_open.setObjectName("SuccessBtn")
            btn_open.clicked.connect(lambda checked, pid=p['id']: self.action_open_op_file(pid))
            self.table_overview_pending.setCellWidget(idx, 5, btn_open)

    def refresh_overview_appointments_table(self):
        apps = database.get_upcoming_appointments(10)
        self.table_overview_appointments.setRowCount(len(apps))
        for idx, a in enumerate(apps):
            self.table_overview_appointments.setItem(idx, 0, QTableWidgetItem(a['app_date']))
            self.table_overview_appointments.setItem(idx, 1, QTableWidgetItem(a['app_time']))
            self.table_overview_appointments.setItem(idx, 2, QTableWidgetItem(a['patient_name']))
            self.table_overview_appointments.setItem(idx, 3, QTableWidgetItem(a['patient_phone']))
            self.table_overview_appointments.setItem(idx, 4, QTableWidgetItem(a['reason']))

            btn_open = QPushButton("View Patient")
            btn_open.setObjectName("PrimaryBtn")
            btn_open.clicked.connect(lambda checked, pid=a['patient_id']: self.load_patient_case_file(pid))
            self.table_overview_appointments.setCellWidget(idx, 5, btn_open)

    # --- VIEW 1: PATIENT REGISTRATION FORM ---
    def init_register_view(self):
        self.register_widget = QWidget()
        layout = QVBoxLayout(self.register_widget)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Register New Patient")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        form_frame = QFrame()
        form_layout = QFormLayout(form_frame)
        form_layout.setVerticalSpacing(12)
        form_layout.setContentsMargins(10, 20, 10, 10)

        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("First & Last Name")
        form_layout.addRow("Full Name:", self.reg_name)

        self.reg_dob = QDateEdit()
        self.reg_dob.setCalendarPopup(True)
        self.reg_dob.setDate(QDate.currentDate().addYears(-30))
        form_layout.addRow("Date of Birth:", self.reg_dob)

        self.reg_gender = QComboBox()
        self.reg_gender.addItems(["Select Gender", "Female", "Male", "Other"])
        form_layout.addRow("Gender:", self.reg_gender)

        self.reg_phone = QLineEdit()
        self.reg_phone.setPlaceholderText("(555) 000-0000")
        form_layout.addRow("Phone Number:", self.reg_phone)

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("patient@email.com")
        form_layout.addRow("Email Address:", self.reg_email)

        self.reg_address = QLineEdit()
        self.reg_address.setPlaceholderText("Street, City, State")
        form_layout.addRow("Home Address:", self.reg_address)

        self.reg_allergies = QLineEdit()
        self.reg_allergies.setPlaceholderText("e.g. Penicillin, Latex (or None)")
        form_layout.addRow("Allergies:", self.reg_allergies)

        self.reg_medical = QTextEdit()
        self.reg_medical.setPlaceholderText("Diabetes, Hypertension, Bleeding disorders, none, etc.")
        self.reg_medical.setMaximumHeight(80)
        form_layout.addRow("Medical Conditions:", self.reg_medical)

        self.reg_doctor = QComboBox()
        form_layout.addRow("Assign Doctor:", self.reg_doctor)
        
        self.reg_hide_admin = QCheckBox("Hide this from Admin unless referred (Patient Privacy)")
        self.reg_hide_admin.setStyleSheet("color: #F43F5E; font-weight: bold;")
        form_layout.addRow("", self.reg_hide_admin)

        layout.addWidget(form_frame)

        # Action Buttons
        btn_layout = QHBoxLayout()
        submit_btn = QPushButton("Register Outpatient (Add to New OP)")
        submit_btn.setObjectName("PrimaryBtn")
        submit_btn.clicked.connect(self.submit_registration)
        btn_layout.addWidget(submit_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()

    def submit_registration(self):
        name = self.reg_name.text().strip()
        dob = self.reg_dob.date().toString("yyyy-MM-dd")
        gender = self.reg_gender.currentText()
        phone = self.reg_phone.text().strip()
        email = self.reg_email.text().strip()
        address = self.reg_address.text().strip()
        allergies = self.reg_allergies.text().strip() or "None"
        medical = self.reg_medical.toPlainText().strip() or "None"

        if not name or gender == "Select Gender" or not phone:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all required fields (Name, Gender, Phone).")
            return

        doc_idx = self.reg_doctor.currentIndex()
        selected_doc_id = self.reg_doctor.itemData(doc_idx) if doc_idx >= 0 else None

        # Automatically assign to Admin profile (ID=1) unless privacy checkbox is checked
        if self.reg_hide_admin.isChecked():
            doc_id = selected_doc_id
        else:
            doc_id = 1  # Dr. Admin

        pid = database.register_patient(name, dob, gender, phone, email, address, allergies, medical, doc_id)
        QMessageBox.information(self, "Success", f"Patient registered successfully!\nID: {pid}\nAdded to New OP Queue.")

        # Clear fields
        self.reg_name.clear()
        self.reg_gender.setCurrentIndex(0)
        self.reg_phone.clear()
        self.reg_email.clear()
        self.reg_address.clear()
        self.reg_allergies.clear()
        self.reg_medical.clear()
        self.reg_hide_admin.setChecked(False)

        # Switch to New OP
        self.btn_new_op.click()

    # --- VIEW 2: NEW OP QUEUE ---
    def init_new_op_view(self):
        self.new_op_widget = QWidget()
        layout = QVBoxLayout(self.new_op_widget)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("New Outpatients (OP) Queue")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Patients registered today who are waiting to have their clinical case file opened.")
        subtitle.setStyleSheet("color: #94A3B8; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        # Table
        self.new_op_table = QTableWidget()
        self.new_op_table.setColumnCount(6)
        self.new_op_table.setHorizontalHeaderLabels(["ID", "Name", "Gender", "Phone", "Registered Date", "Actions"])
        self.new_op_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.new_op_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.new_op_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.new_op_table.verticalHeader().setVisible(False)
        layout.addWidget(self.new_op_table)

    def refresh_new_op_table(self):
        patients = database.get_new_op_patients()
        self.new_op_table.setRowCount(len(patients))

        for idx, p in enumerate(patients):
            self.new_op_table.setItem(idx, 0, QTableWidgetItem(f"P{p['id']:04d}"))
            self.new_op_table.setItem(idx, 1, QTableWidgetItem(p['name']))
            self.new_op_table.setItem(idx, 2, QTableWidgetItem(p['gender']))
            self.new_op_table.setItem(idx, 3, QTableWidgetItem(p['phone']))
            
            # Format Date (handle optional fractional seconds from SQLite)
            raw_ts = p['created_at']
            try:
                created_dt = datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    created_dt = datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    created_dt = datetime.now()
            self.new_op_table.setItem(idx, 4, QTableWidgetItem(created_dt.strftime("%Y-%m-%d %I:%M %p")))

            # Action: Open File
            btn_open = QPushButton("Open File")
            btn_open.setObjectName("SuccessBtn")
            # Connect using closure to grab the patient ID
            btn_open.clicked.connect(lambda checked, pid=p['id']: self.action_open_op_file(pid))
            self.new_op_table.setCellWidget(idx, 5, btn_open)

    def action_open_op_file(self, patient_id):
        # Change status in DB
        database.open_patient_file(patient_id)
        # Open in case view
        self.load_patient_case_file(patient_id)

    # --- VIEW 3: ACTIVE PATIENT LIST ---
    def init_patient_list_view(self):
        self.patient_list_widget = QWidget()
        layout = QVBoxLayout(self.patient_list_widget)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Active Patients Registry")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patients by Name, Phone, or Patient ID...")
        self.search_input.textChanged.connect(self.refresh_patient_list_table)
        search_layout.addWidget(self.search_input, 3)

        self.combo_registry_filter = QComboBox()
        self.combo_registry_filter.addItems(["All Patients", "My Patients"])
        self.combo_registry_filter.currentTextChanged.connect(self.refresh_patient_list_table)
        search_layout.addWidget(self.combo_registry_filter, 1)

        layout.addLayout(search_layout)

        # Table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(5)
        self.patient_table.setHorizontalHeaderLabels(["ID", "Name", "DOB", "Phone", "Actions"])
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.patient_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.patient_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.patient_table.verticalHeader().setVisible(False)
        layout.addWidget(self.patient_table)

    def refresh_patient_list_table(self):
        query = self.search_input.text().strip()
        # Parse potential prefix "P" out of patient ID searches
        db_query = query
        if query.upper().startswith('P'):
            try:
                db_query = str(int(query[1:]))
            except ValueError:
                pass
                
        filter_text = self.combo_registry_filter.currentText()
        doc_filter_id = self.doctor_session['id'] if filter_text == "My Patients" else None

        patients = database.get_active_patients(db_query, doc_filter_id)
        self.patient_table.setRowCount(len(patients))

        for idx, p in enumerate(patients):
            self.patient_table.setItem(idx, 0, QTableWidgetItem(f"P{p['id']:04d}"))
            self.patient_table.setItem(idx, 1, QTableWidgetItem(p['name']))
            self.patient_table.setItem(idx, 2, QTableWidgetItem(p['dob']))
            self.patient_table.setItem(idx, 3, QTableWidgetItem(p['phone']))

            # Action: Open Case File
            btn_open = QPushButton("View Case File")
            btn_open.setObjectName("PrimaryBtn")
            btn_open.clicked.connect(lambda checked, pid=p['id']: self.load_patient_case_file(pid))
            self.patient_table.setCellWidget(idx, 4, btn_open)

    # --- VIEW 4: DETAILED CASE FILE (TABS) ---
    def init_case_file_view(self):
        self.case_file_widget = QWidget()
        layout = QVBoxLayout(self.case_file_widget)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # Top Bar: Patient Banner
        self.patient_banner = QFrame()
        self.patient_banner.setObjectName("PatientBanner")
        self.patient_banner.setStyleSheet("""
            QFrame#PatientBanner {
                padding: 10px;
            }
            QLabel {
                font-size: 11px;
            }
        """)
        banner_vlayout = QVBoxLayout(self.patient_banner)
        banner_vlayout.setContentsMargins(10, 5, 10, 5)
        banner_vlayout.setSpacing(5)

        # Banner Title Row
        title_row = QHBoxLayout()
        self.banner_title = QLabel("Patient Case Sheet Update")
        self.banner_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.banner_title.setObjectName("PatientBannerTitle")
        title_row.addWidget(self.banner_title)
        
        title_row.addStretch()
        
        self.lbl_case_record_no = QLabel("Case Record #: -")
        self.lbl_case_record_no.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_row.addWidget(self.lbl_case_record_no)
        
        banner_vlayout.addLayout(title_row)

        # Banner Grid Fields (3 rows of fields)
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # We can structure columns of details
        col1 = QFormLayout()
        col1.setSpacing(4)
        self.banner_op_no = QLabel("-")
        col1.addRow("OP #:", self.banner_op_no)
        self.banner_phone = QLabel("-")
        col1.addRow("Phone:", self.banner_phone)
        self.banner_doctor_lbl = QLabel("-")
        col1.addRow("Doctor:", self.banner_doctor_lbl)
        
        col2 = QFormLayout()
        col2.setSpacing(4)
        self.banner_patient_name = QLabel("-")
        col2.addRow("Patient Name:", self.banner_patient_name)
        self.banner_village = QLabel("-")
        col2.addRow("Village/City:", self.banner_village)

        col3 = QFormLayout()
        col3.setSpacing(4)
        self.banner_age_gender = QLabel("-")
        col3.addRow("Age/Gender:", self.banner_age_gender)
        self.banner_category = QLabel("-")
        col3.addRow("Category:", self.banner_category)
        self.banner_due = QLabel("-")
        col3.addRow("Due Amt:", self.banner_due)
        
        col4 = QFormLayout()
        col4.setSpacing(4)
        self.banner_validity = QLabel("-")
        col4.addRow("OP Card Validity:", self.banner_validity)
        self.banner_occupation = QLabel("-")
        col4.addRow("Occupation:", self.banner_occupation)

        grid_layout.addLayout(col1)
        grid_layout.addSpacing(20)
        grid_layout.addLayout(col2)
        grid_layout.addSpacing(20)
        grid_layout.addLayout(col3)
        grid_layout.addSpacing(20)
        grid_layout.addLayout(col4)

        banner_vlayout.addWidget(grid_widget)

        # Action Buttons Row
        actions_row = QHBoxLayout()
        
        self.btn_save_case_file = QPushButton("Save Entire Case File")
        self.btn_save_case_file.setObjectName("SuccessBtn")
        self.btn_save_case_file.clicked.connect(self.save_patient_case_file)
        actions_row.addWidget(self.btn_save_case_file)

        self.btn_print_report = QPushButton("Print Case Report")
        self.btn_print_report.setObjectName("PrimaryBtn")
        self.btn_print_report.clicked.connect(self.print_patient_report)
        actions_row.addWidget(self.btn_print_report)

        self.btn_back_to_list = QPushButton("Back to Registry")
        self.btn_back_to_list.clicked.connect(self.back_to_registry)
        actions_row.addWidget(self.btn_back_to_list)

        actions_row.addStretch()

        # Icon-only sidebar toggle button with vector QIcon matching user image 2
        self.btn_toggle_history_panel = QPushButton()
        self.btn_toggle_history_panel.setToolTip("patient's full history")
        self.btn_toggle_history_panel.setFixedSize(36, 36)
        
        # State-aware QIcon drawn dynamically via QPainter
        icon = QIcon()
        icon.addPixmap(create_sidebar_toggle_icon(24, QColor("#94A3B8")).pixmap(24, 24), QIcon.Mode.Normal, QIcon.State.Off)
        icon.addPixmap(create_sidebar_toggle_icon(24, QColor("#FFFFFF")).pixmap(24, 24), QIcon.Mode.Normal, QIcon.State.On)
        
        self.btn_toggle_history_panel.setIcon(icon)
        self.btn_toggle_history_panel.setIconSize(QSize(22, 22))
        self.btn_toggle_history_panel.setStyleSheet("""
            QPushButton {
                background-color: #1a2032;
                border: 1px solid #2D2D30;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #26314f;
                border: 1px solid #0371bb;
            }
            QPushButton:checked {
                background-color: #0371bb;
                border: 1px solid #0371bb;
            }
        """)
        self.btn_toggle_history_panel.setCheckable(True)
        self.btn_toggle_history_panel.clicked.connect(self.toggle_history_panel)
        actions_row.addWidget(self.btn_toggle_history_panel)

        banner_vlayout.addLayout(actions_row)
        
        layout.addWidget(self.patient_banner)

        # Splitter layout for Left Case Sheet & Right Collapsible History Panel
        self.case_sheet_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs Container
        self.case_tabs = QTabWidget()
        left_layout.addWidget(self.case_tabs)
        self.case_sheet_splitter.addWidget(left_container)

        # Right History Panel Drawer
        self.right_history_panel = QWidget()
        self.right_history_panel.setObjectName("RightHistoryPanel")
        self.right_history_panel.setMinimumWidth(340)
        self.right_history_panel.setStyleSheet("""
            QWidget#RightHistoryPanel {
                background-color: #161616;
                border-left: 1px solid #2D2D30;
            }
        """)
        right_layout = QVBoxLayout(self.right_history_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(10)
        
        history_header_layout = QHBoxLayout()
        lbl_history_title = QLabel("Revision History")
        lbl_history_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_history_title.setStyleSheet("color: #E2E8F0;")
        
        btn_fullscreen_history = QPushButton("⛶ Expand")
        btn_fullscreen_history.setToolTip("Open full window version history timeline")
        btn_fullscreen_history.setStyleSheet("""
            QPushButton {
                background-color: #1a2032;
                color: #E2E8F0;
                border: 1px solid #2D2D30;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0371bb;
                color: white;
                border: 1px solid #0371bb;
            }
        """)
        btn_fullscreen_history.clicked.connect(self.open_full_version_history_dialog)

        btn_close_history = QPushButton("✕")
        btn_close_history.setFixedSize(26, 26)
        btn_close_history.setStyleSheet("""
            QPushButton {
                background-color: #1a2032;
                color: #94A3B8;
                border: 1px solid #2D2D30;
                border-radius: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: white;
                border: none;
            }
        """)
        btn_close_history.clicked.connect(lambda: self.right_history_panel.setVisible(False))

        history_header_layout.addWidget(lbl_history_title)
        history_header_layout.addStretch()
        history_header_layout.addWidget(btn_fullscreen_history)
        history_header_layout.addWidget(btn_close_history)
        right_layout.addLayout(history_header_layout)
        
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_content = QWidget()
        self.history_vlayout = QVBoxLayout(self.history_content)
        self.history_vlayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.history_scroll.setWidget(self.history_content)
        right_layout.addWidget(self.history_scroll)
        
        self.case_sheet_splitter.addWidget(self.right_history_panel)
        self.case_sheet_splitter.setSizes([750, 350])
        self.right_history_panel.setVisible(False) # Collapsed by default until toggled
        
        layout.addWidget(self.case_sheet_splitter)

        # Initialize all tabs
        self.tab_history = QWidget()
        self.setup_tab_history()
        self.case_tabs.addTab(self.tab_history, "History")

        # Clinic Examination Section with subtabs
        self.tab_clinic_exam = QWidget()
        clinic_exam_layout = QVBoxLayout(self.tab_clinic_exam)
        clinic_exam_layout.setContentsMargins(0, 0, 0, 0)
        self.clinic_exam_subtabs = QTabWidget()
        clinic_exam_layout.addWidget(self.clinic_exam_subtabs)

        self.tab_extra_oral = QWidget()
        self.setup_tab_extra_oral()
        self.clinic_exam_subtabs.addTab(self.tab_extra_oral, "Extra Oral")

        self.tab_intra_oral = QWidget()
        self.setup_tab_intra_oral()
        self.clinic_exam_subtabs.addTab(self.tab_intra_oral, "Intra Oral")

        self.tab_local_exam = QWidget()
        self.setup_tab_local_exam()
        self.clinic_exam_subtabs.addTab(self.tab_local_exam, "Local Exam")

        self.tab_pre_op_photos = QWidget()
        self.setup_tab_pre_op_photos()
        self.clinic_exam_subtabs.addTab(self.tab_pre_op_photos, "Pre-Op Photos")

        self.case_tabs.addTab(self.tab_clinic_exam, "Clinic Examination")

        self.tab_diagnosis = QWidget()
        self.setup_tab_diagnosis()
        self.case_tabs.addTab(self.tab_diagnosis, "Diagnosis")

        # Investigation Section with subtabs
        self.tab_investigation_section = QWidget()
        investigation_section_layout = QVBoxLayout(self.tab_investigation_section)
        investigation_section_layout.setContentsMargins(0, 0, 0, 0)
        self.investigation_subtabs = QTabWidget()
        investigation_section_layout.addWidget(self.investigation_subtabs)

        self.tab_investigation = QWidget()
        self.setup_tab_investigation()
        self.investigation_subtabs.addTab(self.tab_investigation, "Investigation")

        self.tab_path_requisition = QWidget()
        self.setup_tab_path_requisition()
        self.investigation_subtabs.addTab(self.tab_path_requisition, "Pathology")

        self.tab_pathology_report = QWidget()
        self.setup_tab_pathology_report()
        self.investigation_subtabs.addTab(self.tab_pathology_report, "Pathology Report")

        self.tab_investigation_report = QWidget()
        self.setup_tab_investigation_report()
        self.investigation_subtabs.addTab(self.tab_investigation_report, "Investigation Report")

        self.case_tabs.addTab(self.tab_investigation_section, "Investigation")

        self.tab_final_diagnosis = QWidget()
        self.setup_tab_final_diagnosis()
        self.case_tabs.addTab(self.tab_final_diagnosis, "Final Diagnosis")

        # Treatment Section with subtabs
        self.tab_treatment_section = QWidget()
        treatment_section_layout = QVBoxLayout(self.tab_treatment_section)
        treatment_section_layout.setContentsMargins(0, 0, 0, 0)
        self.treatment_subtabs = QTabWidget()
        treatment_section_layout.addWidget(self.treatment_subtabs)

        self.tab_treatment_plan = QWidget()
        self.setup_tab_treatment_plan()
        self.treatment_subtabs.addTab(self.tab_treatment_plan, "Treatment Plan")

        self.tab_treatment = QWidget()
        self.setup_tab_treatment()
        self.treatment_subtabs.addTab(self.tab_treatment, "Treatment Needed")

        self.tab_treatment_done = QWidget()
        self.setup_tab_treatment_done()
        self.treatment_subtabs.addTab(self.tab_treatment_done, "Treatment Done")

        self.tab_post_op_photos = QWidget()
        self.setup_tab_post_op_photos()
        self.treatment_subtabs.addTab(self.tab_post_op_photos, "Post-Op Photos")

        self.case_tabs.addTab(self.tab_treatment_section, "Treatment")

        self.tab_appointments = QWidget()
        self.setup_tab_appointments()
        self.case_tabs.addTab(self.tab_appointments, "Appointments")

        self.tab_referral = QWidget()
        self.setup_tab_referral()
        self.case_tabs.addTab(self.tab_referral, "Referral")

    def setup_tab_history(self):
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        scroll.setWidget(content)
        
        layout = QHBoxLayout(self.tab_history)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        main_layout = QHBoxLayout(content)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Left Demographics Box
        dem_box = QGroupBox("Demographics & Medical Alerts")
        dem_box.setFixedWidth(280)
        dem_layout = QFormLayout(dem_box)
        dem_layout.setContentsMargins(10, 15, 10, 10)
        dem_layout.setVerticalSpacing(10)
        
        self.lbl_dem_gender = QLabel("-")
        dem_layout.addRow("Gender:", self.lbl_dem_gender)
        self.lbl_dem_phone = QLabel("-")
        dem_layout.addRow("Phone:", self.lbl_dem_phone)
        self.lbl_dem_email = QLabel("-")
        dem_layout.addRow("Email:", self.lbl_dem_email)
        self.lbl_dem_address = QLabel("-")
        self.lbl_dem_address.setWordWrap(True)
        dem_layout.addRow("Address:", self.lbl_dem_address)
        
        self.lbl_dem_allergies = QLabel("-")
        self.lbl_dem_allergies.setStyleSheet("color: #EF4444; font-weight: bold;")
        self.lbl_dem_allergies.setWordWrap(True)
        dem_layout.addRow("Allergies:", self.lbl_dem_allergies)
        
        self.lbl_dem_conditions = QLabel("-")
        self.lbl_dem_conditions.setStyleSheet("color: #F59E0B; font-weight: bold;")
        self.lbl_dem_conditions.setWordWrap(True)
        dem_layout.addRow("Medical Conditions:", self.lbl_dem_conditions)
        
        self.banner_doctor = QComboBox()
        self.banner_doctor.currentIndexChanged.connect(self.on_assigned_doctor_changed)
        dem_layout.addRow("Assigned Doctor:", self.banner_doctor)
        
        main_layout.addWidget(dem_box)
        
        # Right Narrative Case History Box
        hist_box = QGroupBox("Clinical Narrative & Case History")
        hist_layout = QVBoxLayout(hist_box)
        hist_layout.setContentsMargins(15, 15, 15, 15)
        hist_layout.setSpacing(12)
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(8)
        
        self.txt_chief_complaint = QTextEdit()
        self.txt_chief_complaint.setPlaceholderText("Describe the primary reason for visiting...")
        self.txt_chief_complaint.setMaximumHeight(60)
        form_layout.addRow("Chief Complaint:", self.txt_chief_complaint)
        
        self.txt_other_complaint = QTextEdit()
        self.txt_other_complaint.setPlaceholderText("Other secondary complaints...")
        self.txt_other_complaint.setMaximumHeight(40)
        form_layout.addRow("Other Chief Complaint:", self.txt_other_complaint)
        
        self.txt_hpi = QTextEdit()
        self.txt_hpi.setPlaceholderText("Pain description, duration, location, trigger factors...")
        self.txt_hpi.setMaximumHeight(60)
        form_layout.addRow("History of Present Illness (HPI):", self.txt_hpi)
        
        self.txt_medical_hist = QTextEdit()
        self.txt_medical_hist.setPlaceholderText("Systemic medical summaries, list of current medications...")
        self.txt_medical_hist.setMaximumHeight(60)
        form_layout.addRow("Past Medical History:", self.txt_medical_hist)
        
        self.txt_dental_hist = QTextEdit()
        self.txt_dental_hist.setPlaceholderText("Previous root canals, extractions, orthodontic work, dental anxiety...")
        self.txt_dental_hist.setMaximumHeight(60)
        form_layout.addRow("Past Dental History:", self.txt_dental_hist)
        
        self.txt_family_hist = QTextEdit()
        self.txt_family_hist.setPlaceholderText("Diabetes, hypertension, hemophilia, hereditary dental disorders in family...")
        self.txt_family_hist.setMaximumHeight(40)
        form_layout.addRow("Family History:", self.txt_family_hist)
        
        # Personal habits group
        personal_group = QGroupBox("Personal Habits & Diet")
        pers_layout = QFormLayout(personal_group)
        pers_layout.setContentsMargins(10, 10, 10, 10)
        pers_layout.setSpacing(8)
        
        self.combo_brush_method = QComboBox()
        self.combo_brush_method.addItems(["Horizontal", "Vertical", "Circular", "Combination", "Charcoal/Neem/Finger"])
        pers_layout.addRow("Brushing Method:", self.combo_brush_method)
        
        self.combo_brush_freq = QComboBox()
        self.combo_brush_freq.addItems(["Once daily", "Twice daily", "Occasionally", "None"])
        pers_layout.addRow("Brushing Frequency:", self.combo_brush_freq)
        
        self.combo_brush_dur = QComboBox()
        self.combo_brush_dur.addItems(["< 1 minute", "1-2 minutes", "2-5 minutes", "> 5 minutes"])
        pers_layout.addRow("Brushing Duration:", self.combo_brush_dur)
        
        self.combo_brush_change = QComboBox()
        self.combo_brush_change.addItems(["Every month", "Every 2-3 months", "Every 6 months", "Once a year or when frayed"])
        pers_layout.addRow("Brush Change Interval:", self.combo_brush_change)
        
        self.combo_dentifrice = QComboBox()
        self.combo_dentifrice.addItems(["Fluoridated Paste", "Non-fluoridated Paste", "Toothpowder", "Neem/Coals", "Other"])
        pers_layout.addRow("Dentifrice Type:", self.combo_dentifrice)
        
        self.txt_other_dentifrice = QLineEdit()
        self.txt_other_dentifrice.setPlaceholderText("Specify if other dentifrice is used...")
        pers_layout.addRow("Other Dentifrice Detail:", self.txt_other_dentifrice)
        
        self.combo_diet = QComboBox()
        self.combo_diet.addItems(["Vegetarian", "Non-Vegetarian", "Mixed", "Vegan"])
        pers_layout.addRow("Diet Type:", self.combo_diet)
        
        self.combo_parafunc = QComboBox()
        self.combo_parafunc.addItems(["Absent", "Bruxism (Teeth Grinding)", "Clenching", "Lip/Nail Biting", "Tongue Thrusting", "Thumb Sucking", "Others"])
        pers_layout.addRow("Parafunctional Habits:", self.combo_parafunc)
        
        self.combo_sleep = QComboBox()
        self.combo_sleep.addItems(["Normal / Healthy", "Insomnia", "Disturbed Sleep", "Snoring / Sleep Apnea"])
        pers_layout.addRow("Sleep Quality:", self.combo_sleep)

        # Deleterious Habits
        del_group = QGroupBox("Deleterious Habits (Tobacco, Alcohol, Betel Nut)")
        del_layout = QVBoxLayout(del_group)
        
        from PyQt6.QtWidgets import QCheckBox
        self.chk_tobacco = QCheckBox("Tobacco chewing / smoking (Present)")
        self.txt_tobacco_details = QLineEdit()
        self.txt_tobacco_details.setPlaceholderText("Type, Frequency, Duration...")
        del_layout.addWidget(self.chk_tobacco)
        del_layout.addWidget(self.txt_tobacco_details)
        
        self.chk_alcohol = QCheckBox("Alcohol intake (Present)")
        self.txt_alcohol_details = QLineEdit()
        self.txt_alcohol_details.setPlaceholderText("Type, Frequency, Duration...")
        del_layout.addWidget(self.chk_alcohol)
        del_layout.addWidget(self.txt_alcohol_details)
        
        self.chk_betel = QCheckBox("Betel Nut / Quid chewing (Present)")
        self.txt_betel_details = QLineEdit()
        self.txt_betel_details.setPlaceholderText("Type, Frequency, Duration...")
        del_layout.addWidget(self.chk_betel)
        del_layout.addWidget(self.txt_betel_details)
        
        self.chk_other_hab = QCheckBox("Other Deleterious Habits (Present)")
        self.txt_other_hab_details = QLineEdit()
        self.txt_other_hab_details.setPlaceholderText("Describe habit and usage...")
        del_layout.addWidget(self.chk_other_hab)
        del_layout.addWidget(self.txt_other_hab_details)
        
        self.txt_sleep_narrative = QTextEdit()
        self.txt_sleep_narrative.setPlaceholderText("Any additional details on sleep or other habits...")
        self.txt_sleep_narrative.setMaximumHeight(40)
        
        pers_layout.addRow("Habits / Sleep Narrative:", self.txt_sleep_narrative)
        
        hist_layout.addLayout(form_layout)
        hist_layout.addWidget(personal_group)
        hist_layout.addWidget(del_group)
        
        main_layout.addWidget(hist_box, 1)

    def setup_tab_extra_oral(self):
        from PyQt6.QtWidgets import QScrollArea, QGridLayout, QCheckBox
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        scroll.setWidget(content)
        
        layout = QVBoxLayout(self.tab_extra_oral)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # General Physical Exam Group
        phys_group = QGroupBox("General Physical Examination")
        phys_layout = QGridLayout(phys_group)
        phys_layout.setSpacing(8)
        
        self.txt_phys_height = QLineEdit()
        self.txt_phys_height.setPlaceholderText("e.g. 170 cm")
        phys_layout.addWidget(QLabel("Height:"), 0, 0)
        phys_layout.addWidget(self.txt_phys_height, 0, 1)
        
        self.txt_phys_weight = QLineEdit()
        self.txt_phys_weight.setPlaceholderText("e.g. 68 kg")
        phys_layout.addWidget(QLabel("Weight:"), 0, 2)
        phys_layout.addWidget(self.txt_phys_weight, 0, 3)
        
        self.txt_phys_gait = QLineEdit()
        self.txt_phys_gait.setPlaceholderText("e.g. Normal, antalgic")
        phys_layout.addWidget(QLabel("Gait:"), 0, 4)
        phys_layout.addWidget(self.txt_phys_gait, 0, 5)
        
        self.txt_phys_built = QLineEdit()
        self.txt_phys_built.setPlaceholderText("e.g. Mesomorphic, asthenic")
        phys_layout.addWidget(QLabel("Built:"), 1, 0)
        phys_layout.addWidget(self.txt_phys_built, 1, 1)
        
        self.txt_phys_nourish = QLineEdit()
        self.txt_phys_nourish.setPlaceholderText("e.g. Well nourished, moderate")
        phys_layout.addWidget(QLabel("Nourishment:"), 1, 2)
        phys_layout.addWidget(self.txt_phys_nourish, 1, 3)
        
        self.combo_phys_cyanosis = QComboBox()
        self.combo_phys_cyanosis.addItems(["Absent", "Present"])
        phys_layout.addWidget(QLabel("Cyanosis:"), 1, 4)
        phys_layout.addWidget(self.combo_phys_cyanosis, 1, 5)
        
        self.combo_phys_clubbing = QComboBox()
        self.combo_phys_clubbing.addItems(["Absent", "Present"])
        phys_layout.addWidget(QLabel("Clubbing:"), 2, 0)
        phys_layout.addWidget(self.combo_phys_clubbing, 2, 1)
        
        self.combo_phys_icterus = QComboBox()
        self.combo_phys_icterus.addItems(["Absent", "Present"])
        phys_layout.addWidget(QLabel("Icterus:"), 2, 2)
        phys_layout.addWidget(self.combo_phys_icterus, 2, 3)
        
        self.combo_phys_oedema = QComboBox()
        self.combo_phys_oedema.addItems(["Absent", "Present"])
        phys_layout.addWidget(QLabel("Oedema:"), 2, 4)
        phys_layout.addWidget(self.combo_phys_oedema, 2, 5)
        
        self.combo_phys_pallor = QComboBox()
        self.combo_phys_pallor.addItems(["Absent", "Present"])
        phys_layout.addWidget(QLabel("Pallor:"), 3, 0)
        phys_layout.addWidget(self.combo_phys_pallor, 3, 1)
        
        self.txt_phys_skin = QLineEdit()
        phys_layout.addWidget(QLabel("Skin Condition:"), 3, 2)
        phys_layout.addWidget(self.txt_phys_skin, 3, 3)
        
        self.txt_phys_eyes = QLineEdit()
        phys_layout.addWidget(QLabel("Eyes:"), 3, 4)
        phys_layout.addWidget(self.txt_phys_eyes, 3, 5)
        
        self.txt_phys_other = QLineEdit()
        phys_layout.addWidget(QLabel("Others:"), 4, 0)
        phys_layout.addWidget(self.txt_phys_other, 4, 1, 1, 5)
        
        main_layout.addWidget(phys_group)
        
        # Vital Signs Group
        vital_group = QGroupBox("Vital Signs")
        vital_layout = QHBoxLayout(vital_group)
        
        self.txt_vital_bp = QLineEdit()
        self.txt_vital_bp.setPlaceholderText("120/80 mmHg")
        vital_layout.addWidget(QLabel("Blood Pressure:"))
        vital_layout.addWidget(self.txt_vital_bp)
        
        self.txt_vital_pulse = QLineEdit()
        self.txt_vital_pulse.setPlaceholderText("72 bpm")
        vital_layout.addWidget(QLabel("Pulse Rate:"))
        vital_layout.addWidget(self.txt_vital_pulse)
        
        self.txt_vital_rr = QLineEdit()
        self.txt_vital_rr.setPlaceholderText("16 breaths/min")
        vital_layout.addWidget(QLabel("Respiratory Rate:"))
        vital_layout.addWidget(self.txt_vital_rr)
        
        self.txt_vital_temp = QLineEdit()
        self.txt_vital_temp.setPlaceholderText("98.6 F")
        vital_layout.addWidget(QLabel("Temperature:"))
        vital_layout.addWidget(self.txt_vital_temp)
        
        main_layout.addWidget(vital_group)
        
        # Extra-Oral Exam Details Group
        eo_group = QGroupBox("Extra-Oral Assessment (Head & Neck)")
        eo_form = QFormLayout(eo_group)
        
        self.combo_eo_opening = QComboBox()
        self.combo_eo_opening.addItems(["Normal (>40mm)", "Restricted (30-40mm)", "Severely Restricted (<30mm)"])
        eo_form.addRow("Mouth Opening:", self.combo_eo_opening)
        
        self.combo_eo_symmetry = QComboBox()
        self.combo_eo_symmetry.addItems(["Symmetrical", "Asymmetrical (Specify in details)"])
        eo_form.addRow("Face Symmetry:", self.combo_eo_symmetry)
        
        self.txt_eo_salivary = QTextEdit()
        self.txt_eo_salivary.setPlaceholderText("Inspect Parotid, Submandibular gland size, swelling, discharge...")
        self.txt_eo_salivary.setMaximumHeight(50)
        eo_form.addRow("Salivary Glands:", self.txt_eo_salivary)
        
        self.combo_eo_tmj_dev = QComboBox()
        self.combo_eo_tmj_dev.addItems(["No Deviation", "Deviates to Left", "Deviates to Right"])
        eo_form.addRow("TMJ Mandible Deviation:", self.combo_eo_tmj_dev)
        
        self.chk_eo_tmj_tend = QCheckBox("Tenderness Present")
        self.chk_eo_tmj_click = QCheckBox("Clicking/Crepitus Present")
        
        tmj_details_lay = QHBoxLayout()
        tmj_details_lay.addWidget(self.chk_eo_tmj_tend)
        tmj_details_lay.addWidget(self.chk_eo_tmj_click)
        eo_form.addRow("TMJ Signs:", tmj_details_lay)
        
        self.txt_eo_tmj_other = QLineEdit()
        self.txt_eo_tmj_other.setPlaceholderText("Describe deviations, pain trigger, or other TMJ details...")
        eo_form.addRow("Other TMJ Details:", self.txt_eo_tmj_other)
        
        main_layout.addWidget(eo_group)
        
        # Lymph Node Group
        ln_group = QGroupBox("Lymph Node Assessment")
        ln_layout = QVBoxLayout(ln_group)
        
        ln_form = QFormLayout()
        self.combo_ln_palpable = QComboBox()
        self.combo_ln_palpable.addItems(["Non-palpable", "Palpable"])
        ln_form.addRow("Palpability Status:", self.combo_ln_palpable)
        
        self.txt_ln_num = QLineEdit()
        self.txt_ln_num.setPlaceholderText("Number of palpable nodes (e.g. 1, 2)")
        ln_form.addRow("Number:", self.txt_ln_num)
        
        self.combo_ln_group = QComboBox()
        self.combo_ln_group.addItems(["Submental", "Submandibular", "Upper Jugular", "Middle Jugular", "Lower Jugular", "Posterior Triangle", "Supraclavicular", "Other"])
        ln_form.addRow("Lymph Node Group:", self.combo_ln_group)
        
        self.combo_ln_side = QComboBox()
        self.combo_ln_side.addItems(["Left Side Only", "Right Side Only", "Bilateral", "N/A"])
        ln_form.addRow("Side:", self.combo_ln_side)
        ln_layout.addLayout(ln_form)
        
        # Detailed descriptions for bilateral nodes
        nodes_detail = QWidget()
        nodes_detail_lay = QHBoxLayout(nodes_detail)
        nodes_detail_lay.setContentsMargins(0, 0, 0, 0)
        
        ln_left = QGroupBox("Left Side Details")
        ln_left_f = QFormLayout(ln_left)
        self.txt_ln_left_size = QLineEdit()
        self.txt_ln_left_size.setPlaceholderText("e.g. 1x1 cm")
        ln_left_f.addRow("Size:", self.txt_ln_left_size)
        self.combo_ln_left_const = QComboBox()
        self.combo_ln_left_const.addItems(["Soft", "Firm", "Hard", "N/A"])
        ln_left_f.addRow("Consistency:", self.combo_ln_left_const)
        self.chk_ln_left_tend = QCheckBox("Tender")
        ln_left_f.addRow("Tenderness:", self.chk_ln_left_tend)
        self.combo_ln_left_fix = QComboBox()
        self.combo_ln_left_fix.addItems(["Movable", "Fixed", "N/A"])
        ln_left_f.addRow("Fixity:", self.combo_ln_left_fix)
        self.txt_ln_left_other = QLineEdit()
        ln_left_f.addRow("Other details:", self.txt_ln_left_other)
        
        ln_right = QGroupBox("Right Side Details")
        ln_right_f = QFormLayout(ln_right)
        self.txt_ln_right_size = QLineEdit()
        self.txt_ln_right_size.setPlaceholderText("e.g. 1.5x1 cm")
        ln_right_f.addRow("Size:", self.txt_ln_right_size)
        self.combo_ln_right_const = QComboBox()
        self.combo_ln_right_const.addItems(["Soft", "Firm", "Hard", "N/A"])
        ln_right_f.addRow("Consistency:", self.combo_ln_right_const)
        self.chk_ln_right_tend = QCheckBox("Tender")
        ln_right_f.addRow("Tenderness:", self.chk_ln_right_tend)
        self.combo_ln_right_fix = QComboBox()
        self.combo_ln_right_fix.addItems(["Movable", "Fixed", "N/A"])
        ln_right_f.addRow("Fixity:", self.combo_ln_right_fix)
        self.txt_ln_right_other = QLineEdit()
        ln_right_f.addRow("Other details:", self.txt_ln_right_other)
        
        nodes_detail_lay.addWidget(ln_left)
        nodes_detail_lay.addWidget(ln_right)
        ln_layout.addWidget(nodes_detail)
        
        main_layout.addWidget(ln_group)
        main_layout.addStretch()

    def setup_tab_intra_oral(self):
        from PyQt6.QtWidgets import QScrollArea, QGridLayout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        scroll.setWidget(content)
        
        layout = QVBoxLayout(self.tab_intra_oral)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 1. Dental Charting (Interactive Visual Map)
        chart_group = QGroupBox("Teeth Condition Map (Universal / FDI Charting)")
        chart_layout = QVBoxLayout(chart_group)
        
        self.dental_chart = DentalChartWidget()
        self.dental_chart.setMinimumHeight(280)
        chart_layout.addWidget(self.dental_chart)
        
        self.chart_summary = QLabel("Click any tooth to document caries, fillings, crowns, root canals, or missing teeth.")
        self.chart_summary.setStyleSheet("color: #94A3B8; font-style: italic; font-size: 11px;")
        self.chart_summary.setWordWrap(True)
        chart_layout.addWidget(self.chart_summary)
        
        self.dental_chart.chart_updated.connect(self.update_chart_summary_text)
        
        main_layout.addWidget(chart_group)
        
        # 2. Hard Tissue Findings
        hard_group = QGroupBox("Hard Tissue Examination")
        hard_form = QFormLayout(hard_group)
        hard_form.setSpacing(8)
        
        self.combo_ioe_molar = QComboBox()
        self.combo_ioe_molar.addItems(["Class I", "Class II Division 1", "Class II Division 2", "Class III", "N/A"])
        hard_form.addRow("Molar Relation:", self.combo_ioe_molar)
        
        self.combo_ioe_center = QComboBox()
        self.combo_ioe_center.addItems(["Coinciding", "Deviated to Left", "Deviated to Right"])
        hard_form.addRow("Center Line Relation:", self.combo_ioe_center)
        
        self.txt_ioe_occlusion_other = QLineEdit()
        self.txt_ioe_occlusion_other.setPlaceholderText("Other details like overbite, overjet, crossbite...")
        hard_form.addRow("Other Occlusal Details:", self.txt_ioe_occlusion_other)
        
        # Wasting Diseases
        wasting_widget = QWidget()
        wasting_lay = QGridLayout(wasting_widget)
        wasting_lay.setContentsMargins(0, 0, 0, 0)
        wasting_lay.setSpacing(6)
        
        self.txt_waste_attr = QLineEdit()
        self.txt_waste_attr.setPlaceholderText("Tooth numbers involved (e.g. 31, 32, 41)")
        wasting_lay.addWidget(QLabel("Attrition:"), 0, 0)
        wasting_lay.addWidget(self.txt_waste_attr, 0, 1)
        
        self.txt_waste_abran = QLineEdit()
        self.txt_waste_abran.setPlaceholderText("Tooth numbers involved (e.g. 14, 24)")
        wasting_lay.addWidget(QLabel("Abrasion:"), 0, 2)
        wasting_lay.addWidget(self.txt_waste_abran, 0, 3)
        
        self.txt_waste_ero = QLineEdit()
        self.txt_waste_ero.setPlaceholderText("Tooth numbers involved")
        wasting_lay.addWidget(QLabel("Erosion:"), 1, 0)
        wasting_lay.addWidget(self.txt_waste_ero, 1, 1)
        
        self.txt_waste_abfrac = QLineEdit()
        self.txt_waste_abfrac.setPlaceholderText("Tooth numbers involved")
        wasting_lay.addWidget(QLabel("Abfraction:"), 1, 2)
        wasting_lay.addWidget(self.txt_waste_abfrac, 1, 3)
        
        hard_form.addRow("Wasting Diseases:", wasting_widget)
        
        self.combo_ioe_hypo = QComboBox()
        self.combo_ioe_hypo.addItems(["Absent", "Present"])
        self.txt_ioe_hypo_det = QLineEdit()
        self.txt_ioe_hypo_det.setPlaceholderText("Teeth numbers & details...")
        hypo_lay = QHBoxLayout()
        hypo_lay.addWidget(self.combo_ioe_hypo)
        hypo_lay.addWidget(self.txt_ioe_hypo_det)
        hard_form.addRow("Enamel Hypoplasia:", hypo_lay)
        
        self.combo_ioe_sup = QComboBox()
        self.combo_ioe_sup.addItems(["Absent", "Present"])
        self.txt_ioe_sup_det = QLineEdit()
        self.txt_ioe_sup_det.setPlaceholderText("Details of supernumerary teeth...")
        sup_lay = QHBoxLayout()
        sup_lay.addWidget(self.combo_ioe_sup)
        sup_lay.addWidget(self.txt_ioe_sup_det)
        hard_form.addRow("Supernumerary Teeth:", sup_lay)
        
        self.txt_ioe_other_hard = QTextEdit()
        self.txt_ioe_other_hard.setPlaceholderText("Other hard tissue abnormalities (fractured teeth, microdontia, macrodontia, etc.)...")
        self.txt_ioe_other_hard.setMaximumHeight(50)
        hard_form.addRow("Other Hard Tissue:", self.txt_ioe_other_hard)
        
        main_layout.addWidget(hard_group)
        
        # 3. Soft Tissue Mucosal Findings
        soft_group = QGroupBox("Soft Tissue Examination (Mucosa)")
        soft_form = QFormLayout(soft_group)
        soft_form.setSpacing(6)
        
        # Labial Mucosa
        self.combo_muc_labial = QComboBox()
        self.combo_muc_labial.addItems(["Apparently Normal", "Abnormal"])
        self.txt_muc_labial_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_muc_labial)
        lay.addWidget(self.txt_muc_labial_det)
        soft_form.addRow("Labial Mucosa:", lay)
        
        # Buccal Mucosa
        self.combo_muc_buccal = QComboBox()
        self.combo_muc_buccal.addItems(["Apparently Normal", "Abnormal"])
        self.txt_muc_buccal_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_muc_buccal)
        lay.addWidget(self.txt_muc_buccal_det)
        soft_form.addRow("Buccal Mucosa:", lay)
        
        # Floor of Mouth
        self.combo_muc_floor = QComboBox()
        self.combo_muc_floor.addItems(["Apparently Normal", "Abnormal"])
        self.txt_muc_floor_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_muc_floor)
        lay.addWidget(self.txt_muc_floor_det)
        soft_form.addRow("Floor of Mouth:", lay)
        
        # Vestibular Mucosa
        self.combo_muc_vest = QComboBox()
        self.combo_muc_vest.addItems(["Apparently Normal", "Abnormal"])
        self.txt_muc_vest_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_muc_vest)
        lay.addWidget(self.txt_muc_vest_det)
        soft_form.addRow("Vestibular Mucosa:", lay)
        
        # Tongue/Lingual
        self.combo_muc_lingual = QComboBox()
        self.combo_muc_lingual.addItems(["Apparently Normal", "Abnormal"])
        self.txt_muc_lingual_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_muc_lingual)
        lay.addWidget(self.txt_muc_lingual_det)
        soft_form.addRow("Lingual/Tongue Mucosa:", lay)
        
        # Palatal Mucosa
        self.combo_muc_palatal = QComboBox()
        self.combo_muc_palatal.addItems(["Apparently Normal", "Abnormal"])
        self.txt_muc_palatal_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_muc_palatal)
        lay.addWidget(self.txt_muc_palatal_det)
        soft_form.addRow("Palatal Mucosa:", lay)
        
        # Salivary Duct openings
        self.combo_muc_duct = QComboBox()
        self.combo_muc_duct.addItems(["Apparently Normal", "Abnormal"])
        self.txt_muc_duct_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_muc_duct)
        lay.addWidget(self.txt_muc_duct_det)
        soft_form.addRow("Salivary Duct Openings:", lay)
        
        # Other mucosal findings
        self.txt_muc_other_det = QLineEdit()
        soft_form.addRow("Other Mucosal Findings:", self.txt_muc_other_det)
        
        main_layout.addWidget(soft_group)
        
        # 4. Periodontal Findings
        perio_group = QGroupBox("Periodontal Examination")
        perio_form = QFormLayout(perio_group)
        perio_form.setSpacing(6)
        
        self.combo_per_stain = QComboBox()
        self.combo_per_stain.addItems(["Absent", "Present"])
        self.txt_per_stain_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_per_stain)
        lay.addWidget(self.txt_per_stain_det)
        perio_form.addRow("Extrinsic Stains:", lay)
        
        self.combo_per_calc = QComboBox()
        self.combo_per_calc.addItems(["Absent", "Present"])
        self.txt_per_calc_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_per_calc)
        lay.addWidget(self.txt_per_calc_det)
        perio_form.addRow("Calculus:", lay)
        
        self.combo_per_rece = QComboBox()
        self.combo_per_rece.addItems(["Absent", "Present"])
        self.txt_per_rece_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_per_rece)
        lay.addWidget(self.txt_per_rece_det)
        perio_form.addRow("Gingival Recession:", lay)
        
        self.combo_per_enlargement = QComboBox()
        self.combo_per_enlargement.addItems(["Absent", "Present"])
        self.txt_per_enlargement_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_per_enlargement)
        lay.addWidget(self.txt_per_enlargement_det)
        perio_form.addRow("Gingival Enlargement:", lay)
        
        self.combo_per_bop = QComboBox()
        self.combo_per_bop.addItems(["Absent", "Present"])
        self.txt_per_bop_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_per_bop)
        lay.addWidget(self.txt_per_bop_det)
        perio_form.addRow("Bleeding on Probing (BOP):", lay)
        
        self.combo_per_pocket = QComboBox()
        self.combo_per_pocket.addItems(["Absent", "Present"])
        self.txt_per_pocket_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_per_pocket)
        lay.addWidget(self.txt_per_pocket_det)
        perio_form.addRow("Periodontal Pockets:", lay)
        
        self.combo_per_furc = QComboBox()
        self.combo_per_furc.addItems(["Absent", "Present"])
        self.txt_per_furc_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_per_furc)
        lay.addWidget(self.txt_per_furc_det)
        perio_form.addRow("Furcation Involvement:", lay)
        
        self.combo_per_mucogingival = QComboBox()
        self.combo_per_mucogingival.addItems(["Absent", "Present"])
        self.txt_per_mucogingival_det = QLineEdit()
        lay = QHBoxLayout()
        lay.addWidget(self.combo_per_mucogingival)
        lay.addWidget(self.txt_per_mucogingival_det)
        perio_form.addRow("Mucogingival Problems:", lay)
        
        main_layout.addWidget(perio_group)
        main_layout.addStretch()

    def setup_tab_local_exam(self):
        layout = QVBoxLayout(self.tab_local_exam)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # New exam form
        form_group = QGroupBox("Add Local Examination Record")
        form_layout = QFormLayout(form_group)
        
        self.txt_local_header = QLineEdit()
        self.txt_local_header.setPlaceholderText("e.g. Right Buccal Mucosa Ulcer, Lower Left Molar Pain")
        form_layout.addRow("Anatomical Site / Title:", self.txt_local_header)
        
        self.txt_local_eo_insp = QTextEdit()
        self.txt_local_eo_insp.setPlaceholderText("Inspection findings...")
        self.txt_local_eo_insp.setMaximumHeight(40)
        form_layout.addRow("Extra Oral - Inspection:", self.txt_local_eo_insp)
        
        self.txt_local_eo_palp = QTextEdit()
        self.txt_local_eo_palp.setPlaceholderText("Palpation findings...")
        self.txt_local_eo_palp.setMaximumHeight(40)
        form_layout.addRow("Extra Oral - Palpation:", self.txt_local_eo_palp)
        
        self.txt_local_io_soft_insp = QTextEdit()
        self.txt_local_io_soft_insp.setPlaceholderText("Soft tissue inspection...")
        self.txt_local_io_soft_insp.setMaximumHeight(40)
        form_layout.addRow("Intra Oral Soft Tissue - Inspection:", self.txt_local_io_soft_insp)
        
        self.txt_local_io_soft_palp = QTextEdit()
        self.txt_local_io_soft_palp.setPlaceholderText("Soft tissue palpation...")
        self.txt_local_io_soft_palp.setMaximumHeight(40)
        form_layout.addRow("Intra Oral Soft Tissue - Palpation:", self.txt_local_io_soft_palp)
        
        self.txt_local_io_hard_insp = QTextEdit()
        self.txt_local_io_hard_insp.setPlaceholderText("Hard tissue inspection...")
        self.txt_local_io_hard_insp.setMaximumHeight(40)
        form_layout.addRow("Intra Oral Hard Tissue - Inspection:", self.txt_local_io_hard_insp)
        
        self.txt_local_io_hard_perc = QTextEdit()
        self.txt_local_io_hard_perc.setPlaceholderText("Percussion findings...")
        self.txt_local_io_hard_perc.setMaximumHeight(40)
        form_layout.addRow("Intra Oral Hard Tissue - Percussion:", self.txt_local_io_hard_perc)
        
        btn_add_local = QPushButton("Add Local Exam Record")
        btn_add_local.setObjectName("PrimaryBtn")
        btn_add_local.clicked.connect(self.add_local_exam_record)
        form_layout.addRow("", btn_add_local)
        
        layout.addWidget(form_group)
        
        # Existing records list
        list_group = QGroupBox("Local Examination Log")
        list_layout = QVBoxLayout(list_group)
        self.table_local_exams = QTableWidget()
        self.table_local_exams.setColumnCount(8)
        self.table_local_exams.setHorizontalHeaderLabels(["Site / Title", "EO Insp", "EO Palp", "IO Soft Insp", "IO Soft Palp", "IO Hard Insp", "IO Hard Perc", "Action"])
        self.table_local_exams.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_local_exams.verticalHeader().setVisible(False)
        list_layout.addWidget(self.table_local_exams)
        
        layout.addWidget(list_group)

    def add_local_exam_record(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "No Patient", "Please open a patient case sheet first.")
            return
        header = self.txt_local_header.text().strip()
        if not header:
            QMessageBox.warning(self, "Required Field", "Please enter an Anatomical Site / Title for the exam.")
            return
        eo_i = self.txt_local_eo_insp.toPlainText().strip()
        eo_p = self.txt_local_eo_palp.toPlainText().strip()
        io_s_i = self.txt_local_io_soft_insp.toPlainText().strip()
        io_s_p = self.txt_local_io_soft_palp.toPlainText().strip()
        io_h_i = self.txt_local_io_hard_insp.toPlainText().strip()
        io_h_p = self.txt_local_io_hard_perc.toPlainText().strip()
        
        database.save_local_examination(self.current_patient_id, header, eo_i, eo_p, io_s_i, io_s_p, io_h_i, io_h_p)
        
        # Clear fields
        self.txt_local_header.clear()
        self.txt_local_eo_insp.clear()
        self.txt_local_eo_palp.clear()
        self.txt_local_io_soft_insp.clear()
        self.txt_local_io_soft_palp.clear()
        self.txt_local_io_hard_insp.clear()
        self.txt_local_io_hard_perc.clear()
        
        self.refresh_local_exams_table()
        QMessageBox.information(self, "Saved", "Local examination record saved successfully.")

    def refresh_local_exams_table(self):
        if not self.current_patient_id:
            self.table_local_exams.setRowCount(0)
            return
        exams = database.get_patient_details(self.current_patient_id).get('local_examinations', [])
        self.table_local_exams.setRowCount(len(exams))
        for idx, e in enumerate(exams):
            self.table_local_exams.setItem(idx, 0, QTableWidgetItem(e['header']))
            self.table_local_exams.setItem(idx, 1, QTableWidgetItem(e['extra_oral_inspection']))
            self.table_local_exams.setItem(idx, 2, QTableWidgetItem(e['extra_oral_palpation']))
            self.table_local_exams.setItem(idx, 3, QTableWidgetItem(e['soft_tissue_inspection']))
            self.table_local_exams.setItem(idx, 4, QTableWidgetItem(e['soft_tissue_palpation']))
            self.table_local_exams.setItem(idx, 5, QTableWidgetItem(e['hard_tissue_inspection']))
            self.table_local_exams.setItem(idx, 6, QTableWidgetItem(e['hard_tissue_percussion']))
            
            btn_del = QPushButton("Delete")
            btn_del.setStyleSheet("background-color: #EF4444; color: white;")
            btn_del.clicked.connect(lambda checked, eid=e['id']: self.delete_local_exam_record(eid))
            self.table_local_exams.setCellWidget(idx, 7, btn_del)

    def delete_local_exam_record(self, record_id):
        database.delete_local_examination(record_id)
        self.refresh_local_exams_table()

    def setup_tab_pre_op_photos(self):
        layout = QVBoxLayout(self.tab_pre_op_photos)
        layout.setContentsMargins(0, 0, 0, 0)
        self.pre_op_uploader = FileUploaderWidget("Pre-Op Photo", self)
        layout.addWidget(self.pre_op_uploader)

    def setup_tab_diagnosis(self):
        layout = QVBoxLayout(self.tab_diagnosis)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        diag_box = QGroupBox("Clinical Diagnoses")
        diag_layout = QFormLayout(diag_box)
        
        self.txt_diag_provisional = QTextEdit()
        self.txt_diag_provisional.setPlaceholderText("Provisional diagnosis based on primary history & examination (Required)...")
        self.txt_diag_provisional.setMaximumHeight(80)
        diag_layout.addRow("Provisional Diagnosis *:", self.txt_diag_provisional)
        
        self.txt_diag_differential = QTextEdit()
        self.txt_diag_differential.setPlaceholderText("List other possible diagnoses to rule out...")
        self.txt_diag_differential.setMaximumHeight(80)
        diag_layout.addRow("Differential Diagnosis:", self.txt_diag_differential)
        
        self.txt_diag_note = QTextEdit()
        self.txt_diag_note.setPlaceholderText("Any additional diagnostic comments...")
        self.txt_diag_note.setMaximumHeight(80)
        diag_layout.addRow("Diagnostic Note / Comments:", self.txt_diag_note)
        
        layout.addWidget(diag_box)
        layout.addStretch()

    def setup_tab_investigation(self):
        layout = QVBoxLayout(self.tab_investigation)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        order_group = QGroupBox("Order Radiology / Investigation Test")
        order_layout = QGridLayout(order_group)
        order_layout.setSpacing(8)
        
        self.combo_invest_type = QComboBox()
        self.combo_invest_type.addItems(["Radiology Scans", "General Tests"])
        self.combo_invest_type.currentTextChanged.connect(self.on_invest_type_changed)
        order_layout.addWidget(QLabel("Service Type:"), 0, 0)
        order_layout.addWidget(self.combo_invest_type, 0, 1)
        
        self.combo_invest_service = QComboBox()
        # Initial populate
        self.combo_invest_service.addItems(["Intra Oral Periapical Radiograph (IOPA)", "Orthopantomogram (OPG)", "Cone Beam Computed Tomography (CBCT)", "Lateral Cephalogram", "Occlusal Scan"])
        order_layout.addWidget(QLabel("Services:"), 0, 2)
        order_layout.addWidget(self.combo_invest_service, 0, 3)
        
        self.txt_invest_teeth = QLineEdit()
        self.txt_invest_teeth.setPlaceholderText("e.g. 18, 17, 46")
        order_layout.addWidget(QLabel("Teeth No:"), 1, 0)
        order_layout.addWidget(self.txt_invest_teeth, 1, 1)
        
        self.txt_invest_qty = QLineEdit("1")
        self.txt_invest_qty.textChanged.connect(self.calculate_invest_amount)
        order_layout.addWidget(QLabel("Qty:"), 1, 2)
        order_layout.addWidget(self.txt_invest_qty, 1, 3)
        
        self.txt_invest_rate = QLineEdit("150.0")
        self.txt_invest_rate.textChanged.connect(self.calculate_invest_amount)
        order_layout.addWidget(QLabel("Rate:"), 2, 0)
        order_layout.addWidget(self.txt_invest_rate, 2, 1)
        
        self.txt_invest_disc = QLineEdit("0.0")
        self.txt_invest_disc.textChanged.connect(self.calculate_invest_amount)
        order_layout.addWidget(QLabel("Disc %:"), 2, 2)
        order_layout.addWidget(self.txt_invest_disc, 2, 3)
        
        self.txt_invest_amount = QLineEdit("150.0")
        self.txt_invest_amount.setReadOnly(True)
        order_layout.addWidget(QLabel("Amount:"), 3, 0)
        order_layout.addWidget(self.txt_invest_amount, 3, 1)
        
        self.txt_invest_total = QLineEdit("150.0")
        self.txt_invest_total.setReadOnly(True)
        order_layout.addWidget(QLabel("Total:"), 3, 2)
        order_layout.addWidget(self.txt_invest_total, 3, 3)
        
        btn_add_invest = QPushButton("Raise Order Requisition")
        btn_add_invest.setObjectName("PrimaryBtn")
        btn_add_invest.clicked.connect(self.add_investigation_order)
        order_layout.addWidget(btn_add_invest, 4, 0, 1, 4)
        
        layout.addWidget(order_group)
        
        list_group = QGroupBox("Raised Requisitions Log")
        list_layout = QVBoxLayout(list_group)
        self.table_invest_orders = QTableWidget()
        self.table_invest_orders.setColumnCount(8)
        self.table_invest_orders.setHorizontalHeaderLabels(["S.No", "Service Name", "Teeth", "Rate", "Qty", "Disc %", "Total", "Action"])
        self.table_invest_orders.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_invest_orders.verticalHeader().setVisible(False)
        list_layout.addWidget(self.table_invest_orders)
        
        layout.addWidget(list_group)

    def on_invest_type_changed(self, type_str):
        self.combo_invest_service.clear()
        if "Radiology" in type_str:
            self.combo_invest_service.addItems(["Intra Oral Periapical Radiograph (IOPA)", "Orthopantomogram (OPG)", "Cone Beam Computed Tomography (CBCT)", "Lateral Cephalogram", "Occlusal Scan"])
            self.txt_invest_rate.setText("150.0")
        else:
            self.combo_invest_service.addItems(["Caries Activity Test", "Salivary Flow Rate Test", "Pulp Vitality Test", "Biomarker Assays"])
            self.txt_invest_rate.setText("200.0")
        self.calculate_invest_amount()

    def calculate_invest_amount(self):
        try:
            qty = int(self.txt_invest_qty.text() or 0)
            rate = float(self.txt_invest_rate.text() or 0)
            disc = float(self.txt_invest_disc.text() or 0)
            
            amt = qty * rate
            tot = amt - (amt * (disc / 100.0))
            
            self.txt_invest_amount.setText(f"{amt:.2f}")
            self.txt_invest_total.setText(f"{tot:.2f}")
        except ValueError:
            pass

    def add_investigation_order(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "No Patient", "Please open a patient case sheet first.")
            return
        service = self.combo_invest_service.currentText()
        teeth = self.txt_invest_teeth.text().strip()
        qty = int(self.txt_invest_qty.text() or 1)
        rate = float(self.txt_invest_rate.text() or 0)
        total = float(self.txt_invest_total.text() or 0)
        
        disc = float(self.txt_invest_disc.text() or 0)
        amt = float(self.txt_invest_amount.text() or 0)
        svc_type = self.combo_invest_type.currentText()
        database.add_investigation(self.current_patient_id, svc_type, '', service, teeth, qty, rate, amt, disc, total, 'Pending')
        
        self.txt_invest_teeth.clear()
        self.txt_invest_qty.setText("1")
        self.txt_invest_disc.setText("0.0")
        
        self.refresh_investigations_table()
        QMessageBox.information(self, "Saved", "Investigation order raised successfully.")

    def refresh_investigations_table(self):
        if not self.current_patient_id:
            self.table_invest_orders.setRowCount(0)
            return
        orders = database.get_patient_details(self.current_patient_id).get('investigations', [])
        self.table_invest_orders.setRowCount(len(orders))
        for idx, o in enumerate(orders):
            self.table_invest_orders.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.table_invest_orders.setItem(idx, 1, QTableWidgetItem(o['service_name']))
            self.table_invest_orders.setItem(idx, 2, QTableWidgetItem(o['teeth_no']))
            self.table_invest_orders.setItem(idx, 3, QTableWidgetItem(f"{o['rate']:.2f}"))
            self.table_invest_orders.setItem(idx, 4, QTableWidgetItem(str(o['qty'])))
            self.table_invest_orders.setItem(idx, 5, QTableWidgetItem(f"{o['disc_pct']:.1f}"))
            self.table_invest_orders.setItem(idx, 6, QTableWidgetItem(f"{o['total']:.2f}"))
            
            btn_del = QPushButton("Cancel")
            btn_del.setStyleSheet("background-color: #EF4444; color: white;")
            btn_del.clicked.connect(lambda checked, oid=o['id']: self.delete_invest_order(oid))
            self.table_invest_orders.setCellWidget(idx, 7, btn_del)

    def delete_invest_order(self, order_id):
        database.delete_investigation(order_id)
        self.refresh_investigations_table()

    def setup_tab_path_requisition(self):
        layout = QVBoxLayout(self.tab_path_requisition)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        req_group = QGroupBox("Raise Oral Pathology Requisition")
        grid = QGridLayout(req_group)
        grid.setSpacing(8)
        
        self.combo_path_subtab = QComboBox()
        self.combo_path_subtab.addItems(["Biochemistry", "Haematology", "Cytology", "Biopsy", "Microbiology"])
        self.combo_path_subtab.currentTextChanged.connect(self.on_path_subtab_changed)
        grid.addWidget(QLabel("Investigation Category:"), 0, 0)
        grid.addWidget(self.combo_path_subtab, 0, 1)
        
        self.combo_path_service = QComboBox()
        self.combo_path_service.addItems(["Serum Calcium", "Serum Alkaline Phosphatase", "Serum Phosphorus", "Serum Blood Urea Nitrogen (BUN)"])
        grid.addWidget(QLabel("Services:"), 0, 2)
        grid.addWidget(self.combo_path_service, 0, 3)
        
        self.txt_path_teeth = QLineEdit()
        self.txt_path_teeth.setPlaceholderText("Anatomical site / region details...")
        self.lbl_path_site = QLabel("Region:")
        grid.addWidget(self.lbl_path_site, 1, 0)
        grid.addWidget(self.txt_path_teeth, 1, 1)
        # Hide by default
        self.lbl_path_site.hide()
        self.txt_path_teeth.hide()
        
        self.txt_path_qty = QLineEdit("1")
        grid.addWidget(QLabel("Qty:"), 1, 2)
        grid.addWidget(self.txt_path_qty, 1, 3)
        
        self.txt_path_rate = QLineEdit("120.0")
        grid.addWidget(QLabel("Rate:"), 2, 0)
        grid.addWidget(self.txt_path_rate, 2, 1)
        
        self.txt_path_disc = QLineEdit("0.0")
        grid.addWidget(QLabel("Disc %:"), 2, 2)
        grid.addWidget(self.txt_path_disc, 2, 3)
        
        btn_add_path = QPushButton("Raise Requisition")
        btn_add_path.setObjectName("PrimaryBtn")
        btn_add_path.clicked.connect(self.add_pathology_requisition)
        grid.addWidget(btn_add_path, 3, 0, 1, 4)
        
        layout.addWidget(req_group)
        
        list_group = QGroupBox("Raised Pathology Requisitions Log")
        list_layout = QVBoxLayout(list_group)
        self.table_path_requisitions = QTableWidget()
        self.table_path_requisitions.setColumnCount(7)
        self.table_path_requisitions.setHorizontalHeaderLabels(["S.No", "Category", "Service Name", "Site/Teeth", "Rate", "Qty", "Action"])
        self.table_path_requisitions.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_path_requisitions.verticalHeader().setVisible(False)
        list_layout.addWidget(self.table_path_requisitions)
        
        layout.addWidget(list_group)

    def on_path_subtab_changed(self, cat):
        self.combo_path_service.clear()
        if "Biopsy" in cat:
            self.lbl_path_site.show()
            self.txt_path_teeth.show()
        else:
            self.txt_path_teeth.clear()
            self.lbl_path_site.hide()
            self.txt_path_teeth.hide()
            
        if "Biochemistry" in cat:
            self.combo_path_service.addItems(["Serum Calcium", "Serum Alkaline Phosphatase", "Serum Phosphorus", "Serum Blood Urea Nitrogen (BUN)"])
            self.txt_path_rate.setText("120.0")
        elif "Haematology" in cat:
            self.combo_path_service.addItems(["Complete Blood Count (CBC)", "Haemoglobin (Hb)", "Bleeding Time / Clotting Time (BT/CT)", "Erythrocyte Sedimentation Rate (ESR)"])
            self.txt_path_rate.setText("100.0")
        elif "Cytology" in cat:
            self.combo_path_service.addItems(["Exfoliative Cytology", "Fine Needle Aspiration Cytology (FNAC)", "Oral Brush Biopsy"])
            self.txt_path_rate.setText("250.0")
        elif "Biopsy" in cat:
            self.combo_path_service.addItems(["Incisional Biopsy", "Excisional Biopsy", "Punch Biopsy"])
            self.txt_path_rate.setText("400.0")
        else:
            self.combo_path_service.addItems(["Gram Staining", "Acid-Fast Bacilli (AFB) Staining", "Fungal Culture", "Aerobic Culture"])
            self.txt_path_rate.setText("180.0")

    def add_pathology_requisition(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "No Patient", "Please open a patient case sheet first.")
            return
        cat = self.combo_path_subtab.currentText()
        service = self.combo_path_service.currentText()
        site = self.txt_path_teeth.text().strip()
        qty = int(self.txt_path_qty.text() or 1)
        rate = float(self.txt_path_rate.text() or 0)
        
        disc = float(self.txt_path_disc.text() or 0)
        amt = rate * qty
        total_val = amt - (amt * disc / 100.0)
        database.add_pathology_requisition(self.current_patient_id, cat, service, site, qty, rate, amt, disc, total_val)
        
        self.txt_path_teeth.clear()
        self.txt_path_qty.setText("1")
        self.txt_path_disc.setText("0.0")
        
        self.refresh_path_requisitions_table()
        QMessageBox.information(self, "Saved", "Pathology requisition raised successfully.")

    def refresh_path_requisitions_table(self):
        if not self.current_patient_id:
            self.table_path_requisitions.setRowCount(0)
            return
        reqs = database.get_patient_details(self.current_patient_id).get('pathology_requisitions', [])
        self.table_path_requisitions.setRowCount(len(reqs))
        for idx, r in enumerate(reqs):
            self.table_path_requisitions.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.table_path_requisitions.setItem(idx, 1, QTableWidgetItem(r['category']))
            self.table_path_requisitions.setItem(idx, 2, QTableWidgetItem(r['service_name']))
            self.table_path_requisitions.setItem(idx, 3, QTableWidgetItem(r['teeth_no']))
            self.table_path_requisitions.setItem(idx, 4, QTableWidgetItem(f"{r['rate']:.2f}"))
            self.table_path_requisitions.setItem(idx, 5, QTableWidgetItem(str(r['qty'])))
            
            btn_del = QPushButton("Cancel")
            btn_del.setStyleSheet("background-color: #EF4444; color: white;")
            btn_del.clicked.connect(lambda checked, rid=r['id']: self.delete_path_req(rid))
            self.table_path_requisitions.setCellWidget(idx, 6, btn_del)

    def delete_path_req(self, req_id):
        database.delete_pathology_requisition(req_id)
        self.refresh_path_requisitions_table()

    def setup_tab_pathology_report(self):
        layout = QVBoxLayout(self.tab_pathology_report)
        layout.setContentsMargins(0, 0, 0, 0)
        self.pathology_report_uploader = FileUploaderWidget("Pathology Report", self)
        layout.addWidget(self.pathology_report_uploader)

    def setup_tab_investigation_report(self):
        # Main layout is a horizontal splitter for side-by-side diagnostic viewing
        layout = QHBoxLayout(self.tab_investigation_report)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Left side: Diagnostic X-ray Viewer
        self.xray_viewer = XrayViewerWidget()
        layout.addWidget(self.xray_viewer, 3)
        
        # Right side: Text reports
        report_group = QGroupBox("Diagnostic Findings / Text Reports")
        report_layout = QVBoxLayout(report_group)
        report_layout.setSpacing(8)
        
        report_layout.addWidget(QLabel("Radiology Findings (OPG, IOPA, CBCT):"))
        self.txt_radiology_reports = QTextEdit()
        self.txt_radiology_reports.setPlaceholderText("Type radiology scan interpretation and findings...")
        self.txt_radiology_reports.setMinimumHeight(150)
        report_layout.addWidget(self.txt_radiology_reports)
        
        report_layout.addWidget(QLabel("Oral Pathology Lab Findings:"))
        self.txt_pathology_reports = QTextEdit()
        self.txt_pathology_reports.setPlaceholderText("Type pathology / blood test findings...")
        self.txt_pathology_reports.setMinimumHeight(150)
        report_layout.addWidget(self.txt_pathology_reports)
        
        layout.addWidget(report_group, 2)


    def setup_tab_final_diagnosis(self):
        layout = QVBoxLayout(self.tab_final_diagnosis)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        fd_box = QGroupBox("Final Diagnosis")
        fd_layout = QVBoxLayout(fd_box)
        fd_layout.setContentsMargins(15, 15, 15, 15)
        
        self.txt_final_diagnosis = QTextEdit()
        self.txt_final_diagnosis.setPlaceholderText("State the final diagnosis after analyzing radiological/pathological reports...")
        self.txt_final_diagnosis.setMinimumHeight(150)
        fd_layout.addWidget(self.txt_final_diagnosis)
        
        layout.addWidget(fd_box)
        layout.addStretch()

    def setup_tab_treatment_plan(self):
        layout = QVBoxLayout(self.tab_treatment_plan)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        tp_box = QGroupBox("Clinical Treatment Plan & Prognosis")
        tp_layout = QFormLayout(tp_box)
        
        self.txt_treatment_plan = QTextEdit()
        self.txt_treatment_plan.setPlaceholderText("Detailed treatment schedule, extractions, root canals, restorations (Required)...")
        self.txt_treatment_plan.setMaximumHeight(80)
        tp_layout.addRow("Treatment Plan *:", self.txt_treatment_plan)
        
        self.txt_prognosis = QTextEdit()
        self.txt_prognosis.setPlaceholderText("Expected outcomes, prognosis (excellent, good, guarded)...")
        self.txt_prognosis.setMaximumHeight(50)
        tp_layout.addRow("Prognosis:", self.txt_prognosis)
        
        self.txt_physician_note = QTextEdit()
        self.txt_physician_note.setPlaceholderText("Physician instructions, pre-medication instructions...")
        self.txt_physician_note.setMaximumHeight(50)
        tp_layout.addRow("Physician Notes:", self.txt_physician_note)
        
        layout.addWidget(tp_box)
        
        presc_box = QGroupBox("Add Drug Prescription")
        presc_layout = QGridLayout(presc_box)
        
        self.txt_presc_medicine = QLineEdit()
        self.txt_presc_medicine.setPlaceholderText("Medication name (e.g. Amoxicillin 500mg)")
        presc_layout.addWidget(QLabel("Medicine Name:"), 0, 0)
        presc_layout.addWidget(self.txt_presc_medicine, 0, 1)
        
        self.txt_presc_dosage = QLineEdit()
        self.txt_presc_dosage.setPlaceholderText("Dosage (e.g. 1 tab)")
        presc_layout.addWidget(QLabel("Dosage:"), 0, 2)
        presc_layout.addWidget(self.txt_presc_dosage, 0, 3)
        
        self.txt_presc_freq = QLineEdit()
        self.txt_presc_freq.setPlaceholderText("Frequency (e.g. TID / Thrice daily)")
        presc_layout.addWidget(QLabel("Frequency:"), 1, 0)
        presc_layout.addWidget(self.txt_presc_freq, 1, 1)
        
        self.txt_presc_dur = QLineEdit()
        self.txt_presc_dur.setPlaceholderText("Duration (e.g. 5 days)")
        presc_layout.addWidget(QLabel("Duration:"), 1, 2)
        presc_layout.addWidget(self.txt_presc_dur, 1, 3)
        
        btn_add_presc = QPushButton("Add Medication")
        btn_add_presc.setObjectName("PrimaryBtn")
        btn_add_presc.clicked.connect(self.add_prescription_row)
        presc_layout.addWidget(btn_add_presc, 2, 0, 1, 4)
        
        layout.addWidget(presc_box)
        
        list_box = QGroupBox("Active Prescriptions list")
        list_lay = QVBoxLayout(list_box)
        self.table_prescriptions = QTableWidget()
        self.table_prescriptions.setColumnCount(5)
        self.table_prescriptions.setHorizontalHeaderLabels(["Medicine", "Dosage", "Frequency", "Duration", "Action"])
        self.table_prescriptions.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_prescriptions.verticalHeader().setVisible(False)
        list_lay.addWidget(self.table_prescriptions)
        
        layout.addWidget(list_box)

    def add_prescription_row(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "No Patient", "Please open a patient case sheet first.")
            return
        med = self.txt_presc_medicine.text().strip()
        dosage = self.txt_presc_dosage.text().strip()
        freq = self.txt_presc_freq.text().strip()
        dur = self.txt_presc_dur.text().strip()
        
        if not med:
            QMessageBox.warning(self, "Required", "Medicine Name is required.")
            return
            
        database.save_prescription(self.current_patient_id, med, dosage, freq, dur)
        
        self.txt_presc_medicine.clear()
        self.txt_presc_dosage.clear()
        self.txt_presc_freq.clear()
        self.txt_presc_dur.clear()
        
        self.refresh_prescriptions_table()

    def refresh_prescriptions_table(self):
        if not self.current_patient_id:
            self.table_prescriptions.setRowCount(0)
            return
        drugs = database.get_patient_details(self.current_patient_id).get('prescriptions', [])
        self.table_prescriptions.setRowCount(len(drugs))
        for idx, d in enumerate(drugs):
            self.table_prescriptions.setItem(idx, 0, QTableWidgetItem(d['drug_name']))
            self.table_prescriptions.setItem(idx, 1, QTableWidgetItem(d['dosage']))
            self.table_prescriptions.setItem(idx, 2, QTableWidgetItem(d['frequency']))
            self.table_prescriptions.setItem(idx, 3, QTableWidgetItem(d['duration']))
            
            btn_del = QPushButton("Delete")
            btn_del.setStyleSheet("background-color: #EF4444; color: white;")
            btn_del.clicked.connect(lambda checked, rid=d['id']: self.delete_prescription_row(rid))
            self.table_prescriptions.setCellWidget(idx, 4, btn_del)

    def delete_prescription_row(self, drug_id):
        database.delete_prescription(drug_id)
        self.refresh_prescriptions_table()

    def setup_tab_treatment(self):
        # Repurposed for Billing for Treatments Needed
        layout = QVBoxLayout(self.tab_treatment)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        bill_group = QGroupBox("Raise Bill / Request Treatment Needed")
        grid = QGridLayout(bill_group)
        grid.setSpacing(8)
        
        self.txt_treat_name = QLineEdit()
        self.txt_treat_name.setPlaceholderText("e.g. Root Canal Treatment, Composite Restoration, Scaling")
        grid.addWidget(QLabel("Procedure Name:"), 0, 0)
        grid.addWidget(self.txt_treat_name, 0, 1)
        
        self.txt_treat_teeth = QLineEdit()
        self.txt_treat_teeth.setPlaceholderText("e.g. 36, 11-12, Upper Arch")
        grid.addWidget(QLabel("Teeth / Arch:"), 0, 2)
        grid.addWidget(self.txt_treat_teeth, 0, 3)
        
        self.txt_treat_qty = QLineEdit("1")
        self.txt_treat_qty.textChanged.connect(self.calculate_needed_total)
        grid.addWidget(QLabel("Qty:"), 1, 0)
        grid.addWidget(self.txt_treat_qty, 1, 1)
        
        self.txt_treat_rate = QLineEdit("0.0")
        self.txt_treat_rate.textChanged.connect(self.calculate_needed_total)
        grid.addWidget(QLabel("Rate (Rs.):"), 1, 2)
        grid.addWidget(self.txt_treat_rate, 1, 3)
        
        self.txt_treat_disc = QLineEdit("0.0")
        self.txt_treat_disc.textChanged.connect(self.calculate_needed_total)
        grid.addWidget(QLabel("Discount %:"), 2, 0)
        grid.addWidget(self.txt_treat_disc, 2, 1)
        
        self.txt_treat_total = QLineEdit("0.0")
        self.txt_treat_total.setReadOnly(True)
        self.txt_treat_total.setStyleSheet("font-weight: bold; color: #10B981;")
        grid.addWidget(QLabel("Total (Rs.):"), 2, 2)
        grid.addWidget(self.txt_treat_total, 2, 3)
        
        btn_raise_bill = QPushButton("Raise Bill / Save Needed Treatment")
        btn_raise_bill.setObjectName("SuccessBtn")
        btn_raise_bill.clicked.connect(self.add_treatment_needed_action)
        grid.addWidget(btn_raise_bill, 3, 0, 1, 4)
        
        layout.addWidget(bill_group)
        
        log_group = QGroupBox("Billed Treatments & Pending Bills Log")
        log_layout = QVBoxLayout(log_group)
        
        self.table_treatments_needed = QTableWidget()
        self.table_treatments_needed.setColumnCount(9)
        self.table_treatments_needed.setHorizontalHeaderLabels(["S.No", "Procedure Name", "Teeth", "Rate", "Qty", "Disc %", "Total", "Billing Status", "Actions"])
        self.table_treatments_needed.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_treatments_needed.verticalHeader().setVisible(False)
        log_layout.addWidget(self.table_treatments_needed)
        
        layout.addWidget(log_group)

    def calculate_needed_total(self):
        try:
            qty = int(self.txt_treat_qty.text() or 1)
            rate = float(self.txt_treat_rate.text() or 0)
            disc = float(self.txt_treat_disc.text() or 0)
            sub = rate * qty
            total = sub - (sub * disc / 100.0)
            self.txt_treat_total.setText(f"{total:.2f}")
        except ValueError:
            self.txt_treat_total.setText("0.00")

    def add_treatment_needed_action(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "No Patient", "Please open a patient case sheet first.")
            return
        name = self.txt_treat_name.text().strip()
        teeth = self.txt_treat_teeth.text().strip()
        if not name:
            QMessageBox.warning(self, "Required", "Procedure Name is required.")
            return
        try:
            qty = int(self.txt_treat_qty.text() or 1)
            rate = float(self.txt_treat_rate.text() or 0)
            disc = float(self.txt_treat_disc.text() or 0)
            total = float(self.txt_treat_total.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Invalid Inputs", "Please check rate, qty, or discount numeric format.")
            return
            
        database.add_treatment_needed(self.current_patient_id, name, teeth, qty, rate, disc, total, 'Unpaid')
        
        self.txt_treat_name.clear()
        self.txt_treat_teeth.clear()
        self.txt_treat_qty.setText("1")
        self.txt_treat_rate.setText("0.0")
        self.txt_treat_disc.setText("0.0")
        self.txt_treat_total.setText("0.00")
        
        self.refresh_treatments_needed_table()
        self.refresh_done_treatment_dropdown()
        QMessageBox.information(self, "Saved", "Needed treatment billing request generated successfully.")

    def refresh_treatments_needed_table(self):
        if not self.current_patient_id:
            self.table_treatments_needed.setRowCount(0)
            return
        needs = database.get_patient_details(self.current_patient_id).get('treatments_needed', [])
        self.table_treatments_needed.setRowCount(len(needs))
        for idx, n in enumerate(needs):
            self.table_treatments_needed.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.table_treatments_needed.setItem(idx, 1, QTableWidgetItem(n['procedure_name']))
            self.table_treatments_needed.setItem(idx, 2, QTableWidgetItem(n['teeth_no']))
            self.table_treatments_needed.setItem(idx, 3, QTableWidgetItem(f"{n['rate']:.2f}"))
            self.table_treatments_needed.setItem(idx, 4, QTableWidgetItem(str(n['qty'])))
            self.table_treatments_needed.setItem(idx, 5, QTableWidgetItem(f"{n['discount']:.1f}"))
            self.table_treatments_needed.setItem(idx, 6, QTableWidgetItem(f"{n['total']:.2f}"))
            self.table_treatments_needed.setItem(idx, 7, QTableWidgetItem(n['billing_status']))
            
            # Action layout with Pay and Cancel buttons
            act_widget = QWidget()
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(4)
            
            if n['billing_status'] == 'Unpaid':
                btn_pay = QPushButton("Pay")
                btn_pay.setStyleSheet("background-color: #10B981; color: white; padding: 2px 5px;")
                btn_pay.clicked.connect(lambda checked, nid=n['id']: self.pay_needed_treatment_bill(nid))
                act_layout.addWidget(btn_pay)
                
            btn_del = QPushButton("Delete")
            btn_del.setStyleSheet("background-color: #EF4444; color: white; padding: 2px 5px;")
            btn_del.clicked.connect(lambda checked, nid=n['id']: self.delete_needed_treatment(nid))
            act_layout.addWidget(btn_del)
            
            self.table_treatments_needed.setCellWidget(idx, 8, act_widget)

    def pay_needed_treatment_bill(self, needed_id):
        database.pay_treatment_needed_bill(needed_id)
        self.refresh_treatments_needed_table()
        self.refresh_done_treatment_dropdown()

    def delete_needed_treatment(self, needed_id):
        database.delete_treatment_needed(needed_id)
        self.refresh_treatments_needed_table()
        self.refresh_done_treatment_dropdown()

    def setup_tab_treatment_done(self):
        layout = QVBoxLayout(self.tab_treatment_done)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        done_box = QGroupBox("Log Clinical Treatment Session Done")
        done_layout = QFormLayout(done_box)
        
        # Link to Billed needed treatment
        self.combo_done_bill_item = QComboBox()
        self.combo_done_bill_item.currentIndexChanged.connect(self.on_done_bill_item_changed)
        done_layout.addRow("Link to Billed Treatment:", self.combo_done_bill_item)
        
        # Bill payment status indicator
        self.lbl_done_payment_status = QLabel("None (Unbilled)")
        self.lbl_done_payment_status.setStyleSheet("font-weight: bold; color: #EF4444;")
        done_layout.addRow("Bill Payment Status:", self.lbl_done_payment_status)
        
        # Treatment Status dropdown
        self.combo_done_treatment_status = QComboBox()
        self.combo_done_treatment_status.addItems(["Done", "In Process", "Pending"])
        done_layout.addRow("Treatment Status:", self.combo_done_treatment_status)
        
        self.txt_treatment_done_student = QLineEdit()
        self.txt_treatment_done_student.setPlaceholderText("Name of clinician performing treatment")
        done_layout.addRow("Clinician Allotted:", self.txt_treatment_done_student)
        
        self.txt_treatment_done_desc = QTextEdit()
        self.txt_treatment_done_desc.setPlaceholderText("Describe the session clinical procedure details...")
        self.txt_treatment_done_desc.setMaximumHeight(80)
        done_layout.addRow("Session Clinical Details:", self.txt_treatment_done_desc)
        
        self.txt_treatment_done_notes = QTextEdit()
        self.txt_treatment_done_notes.setPlaceholderText("Doctor's remarks, special instructions, post-op feedback...")
        self.txt_treatment_done_notes.setMaximumHeight(60)
        done_layout.addRow("Doctor's Notes / Remarks:", self.txt_treatment_done_notes)
        
        btn_add_done = QPushButton("Log Clinical Session Work")
        btn_add_done.setObjectName("PrimaryBtn")
        btn_add_done.clicked.connect(self.add_treatment_done_row)
        done_layout.addRow("", btn_add_done)
        
        layout.addWidget(done_box)
        
        list_box = QGroupBox("Completed Clinical Sessions History")
        list_lay = QVBoxLayout(list_box)
        self.table_treatments_done = QTableWidget()
        self.table_treatments_done.setColumnCount(8)
        self.table_treatments_done.setHorizontalHeaderLabels([
            "Date", "Billed Item", "Bill Paid?", "Treat Status", "Clinical Details", "Doctor's Notes", "Authorized By", "Actions"
        ])
        self.table_treatments_done.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_treatments_done.verticalHeader().setVisible(False)
        list_lay.addWidget(self.table_treatments_done)
        
        layout.addWidget(list_box)

    def refresh_done_treatment_dropdown(self):
        if not self.current_patient_id:
            self.combo_done_bill_item.clear()
            self.lbl_done_payment_status.setText("None (Unbilled)")
            return
        needs = database.get_patient_details(self.current_patient_id).get('treatments_needed', [])
        
        self.combo_done_bill_item.blockSignals(True)
        self.combo_done_bill_item.clear()
        self.combo_done_bill_item.addItem("None (Unbilled Procedure)", None)
        for n in needs:
            self.combo_done_bill_item.addItem(f"{n['procedure_name']} (Teeth: {n['teeth_no']}, Rs.{n['total']:.2f})", n)
        self.combo_done_bill_item.blockSignals(False)
        self.on_done_bill_item_changed()

    def on_done_bill_item_changed(self):
        idx = self.combo_done_bill_item.currentIndex()
        if idx <= 0:
            self.lbl_done_payment_status.setText("N/A (Unbilled)")
            self.lbl_done_payment_status.setStyleSheet("font-weight: bold; color: #94A3B8;")
            return
        item_data = self.combo_done_bill_item.currentData()
        if item_data:
            status = item_data.get('billing_status', 'Unpaid')
            self.lbl_done_payment_status.setText(status.upper())
            if status == 'Paid':
                self.lbl_done_payment_status.setStyleSheet("font-weight: bold; color: #10B981;")
            else:
                self.lbl_done_payment_status.setStyleSheet("font-weight: bold; color: #EF4444;")

    def add_treatment_done_row(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "No Patient", "Please open a patient case sheet first.")
            return
        student = self.txt_treatment_done_student.text().strip()
        work = self.txt_treatment_done_desc.toPlainText().strip()
        doc_notes = self.txt_treatment_done_notes.toPlainText().strip()
        
        if not work:
            QMessageBox.warning(self, "Required", "Session Clinical Details are required.")
            return
            
        bill_data = self.combo_done_bill_item.currentData()
        needed_id = bill_data['id'] if bill_data else None
        
        treatment_status = self.combo_done_treatment_status.currentText()
        doc_name = self.doctor_session.get('name', 'Dr. Admin')
        
        from datetime import date as dt_date
        date_today = dt_date.today().isoformat()
        
        database.add_treatment_done(
            self.current_patient_id, date_today, student, doc_name, work, 
            status="Completed", treatment_needed_id=needed_id, doctor_notes=doc_notes, treatment_status=treatment_status
        )
        
        self.txt_treatment_done_student.clear()
        self.txt_treatment_done_desc.clear()
        self.txt_treatment_done_notes.clear()
        
        self.refresh_treatments_done_table()
        QMessageBox.information(self, "Success", "Clinical treatment session logged successfully.")

    def refresh_treatments_done_table(self):
        if not self.current_patient_id:
            self.table_treatments_done.setRowCount(0)
            return
            
        details = database.get_patient_details(self.current_patient_id)
        dones = details.get('treatments_done', [])
        needs = details.get('treatments_needed', [])
        needs_map = {n['id']: n for n in needs}
        
        self.table_treatments_done.setRowCount(len(dones))
        for idx, d in enumerate(dones):
            self.table_treatments_done.setItem(idx, 0, QTableWidgetItem(d['date_done']))
            
            needed_id = d.get('treatment_needed_id')
            linked_bill = needs_map.get(needed_id) if needed_id else None
            
            if linked_bill:
                bill_name = linked_bill['procedure_name']
                is_paid = linked_bill['billing_status']
            else:
                bill_name = "Unbilled Procedure"
                is_paid = "N/A"
                
            self.table_treatments_done.setItem(idx, 1, QTableWidgetItem(bill_name))
            self.table_treatments_done.setItem(idx, 2, QTableWidgetItem(is_paid))
            self.table_treatments_done.setItem(idx, 3, QTableWidgetItem(d.get('treatment_status', 'Done')))
            self.table_treatments_done.setItem(idx, 4, QTableWidgetItem(d['details']))
            self.table_treatments_done.setItem(idx, 5, QTableWidgetItem(d.get('doctor_notes', '')))
            
            auth_by = f"{d['doctor_name']}"
            if d['student_name']:
                auth_by = f"{d['student_name']} / " + auth_by
            self.table_treatments_done.setItem(idx, 6, QTableWidgetItem(auth_by))
            
            # Action layout with View and Delete buttons
            act_widget = QWidget()
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(4)
            
            btn_view = QPushButton("👁 View")
            btn_view.setStyleSheet("background-color: #0284C7; color: white; padding: 2px 5px;")
            btn_view.clicked.connect(lambda checked, item_data=d, bill=linked_bill: self.view_treatment_done_details(item_data, bill))
            act_layout.addWidget(btn_view)
            
            btn_del = QPushButton("Delete")
            btn_del.setStyleSheet("background-color: #EF4444; color: white; padding: 2px 5px;")
            btn_del.clicked.connect(lambda checked, rid=d['id']: self.delete_treatment_done_row(rid))
            act_layout.addWidget(btn_del)
            
            self.table_treatments_done.setCellWidget(idx, 7, act_widget)

    def view_treatment_done_details(self, d, linked_bill):
        dialog = ViewTreatmentDoneDialog(d, linked_bill, self)
        dialog.exec()

    def delete_treatment_done_row(self, done_id):
        database.delete_treatment_done(done_id)
        self.refresh_treatments_done_table()

    def setup_tab_post_op_photos(self):
        layout = QVBoxLayout(self.tab_post_op_photos)
        layout.setContentsMargins(0, 0, 0, 0)
        self.post_op_uploader = FileUploaderWidget("Post-Op Photo", self)
        layout.addWidget(self.post_op_uploader)

    def setup_tab_appointments(self):
        layout = QVBoxLayout(self.tab_appointments)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        book_box = QGroupBox("Schedule Next Appointment")
        book_lay = QFormLayout(book_box)
        
        self.txt_app_date = QDateEdit()
        self.txt_app_date.setCalendarPopup(True)
        self.txt_app_date.setDate(QDate.currentDate().addDays(7))
        book_lay.addRow("Appointment Date:", self.txt_app_date)
        
        self.txt_app_time = QLineEdit("10:00 AM")
        book_lay.addRow("Appointment Time:", self.txt_app_time)
        
        self.txt_app_reason = QTextEdit()
        self.txt_app_reason.setPlaceholderText("Reason for next appointment (e.g. RCT Obturation, Crown fixation)...")
        self.txt_app_reason.setMaximumHeight(60)
        book_lay.addRow("Reason / Procedure *:", self.txt_app_reason)
        
        btn_book = QPushButton("Book Appointment")
        btn_book.setObjectName("PrimaryBtn")
        btn_book.clicked.connect(self.add_appointment_row)
        book_lay.addRow("", btn_book)
        
        layout.addWidget(book_box)
        
        list_box = QGroupBox("Appointment Log")
        list_lay = QVBoxLayout(list_box)
        self.table_appointments = QTableWidget()
        self.table_appointments.setColumnCount(5)
        self.table_appointments.setHorizontalHeaderLabels(["App Date", "App Time", "Reason / Description", "Status", "Action"])
        self.table_appointments.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_appointments.verticalHeader().setVisible(False)
        list_lay.addWidget(self.table_appointments)
        
        layout.addWidget(list_box)

    def add_appointment_row(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "No Patient", "Please open a patient case sheet first.")
            return
        app_date = self.txt_app_date.date().toString("yyyy-MM-dd")
        app_time = self.txt_app_time.text().strip()
        reason = self.txt_app_reason.toPlainText().strip()
        
        if not reason:
            QMessageBox.warning(self, "Required", "Appointment Reason is required.")
            return
            
        database.save_appointment(self.current_patient_id, app_date, app_time, reason, 'Yet to visit')
        
        self.txt_app_time.setText("10:00 AM")
        self.txt_app_reason.clear()
        
        self.refresh_appointments_table()
        QMessageBox.information(self, "Success", "Appointment scheduled successfully.")

    def refresh_appointments_table(self):
        if not self.current_patient_id:
            self.table_appointments.setRowCount(0)
            return
        apps = database.get_patient_details(self.current_patient_id).get('appointments', [])
        self.table_appointments.setRowCount(len(apps))
        for idx, a in enumerate(apps):
            self.table_appointments.setItem(idx, 0, QTableWidgetItem(a['app_date']))
            self.table_appointments.setItem(idx, 1, QTableWidgetItem(a['app_time']))
            self.table_appointments.setItem(idx, 2, QTableWidgetItem(a['reason']))
            self.table_appointments.setItem(idx, 3, QTableWidgetItem(a['status']))
            
            btn_del = QPushButton("Cancel")
            btn_del.setStyleSheet("background-color: #EF4444; color: white;")
            btn_del.clicked.connect(lambda checked, rid=a['id']: self.delete_appointment_row(rid))
            self.table_appointments.setCellWidget(idx, 4, btn_del)

    def delete_appointment_row(self, app_id):
        database.delete_appointment(app_id)
        self.refresh_appointments_table()

    def setup_tab_referral(self):
        layout = QVBoxLayout(self.tab_referral)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        ref_box = QGroupBox("Referred to Registered Doctor")
        ref_layout = QFormLayout(ref_box)
        
        self.combo_referral_doctor = QComboBox()
        ref_layout.addRow("Referred Registered Doctor:", self.combo_referral_doctor)
        
        self.txt_referral_reason = QTextEdit()
        self.txt_referral_reason.setPlaceholderText("Reason for referral (e.g. Surgical extraction, orthodontic braces, flap surgery)...")
        self.txt_referral_reason.setMinimumHeight(100)
        ref_layout.addRow("Referral Reason & Notes:", self.txt_referral_reason)
        
        self.combo_referral_status = QComboBox()
        self.combo_referral_status.addItems(["Pending Referral", "Completed"])
        ref_layout.addRow("Referral Status:", self.combo_referral_status)
        
        layout.addWidget(ref_box)
        layout.addStretch()

    def back_to_registry(self):
        self.btn_patient_list.click()

    def load_patient_case_file(self, patient_id):
        self.current_patient_id = patient_id
        
        p = database.get_patient_details(patient_id)
        if not p:
            QMessageBox.critical(self, "Error", "Patient record not found.")
            return

        # 1. Calculate Age
        dob_dt = datetime.strptime(p['dob'], "%Y-%m-%d")
        age = datetime.now().year - dob_dt.year - ((datetime.now().month, datetime.now().day) < (dob_dt.month, dob_dt.day))
        doc_name = p.get('assigned_doctor_name') or "Unassigned"

        # 2. Update Top Banner Grid Fields
        self.lbl_case_record_no.setText(f"Case Record #: CR{p['id']:04d}")
        self.banner_op_no.setText(f"OP{p['id']:04d}")
        self.banner_phone.setText(p['phone'])
        self.banner_doctor_lbl.setText(doc_name)
        self.banner_patient_name.setText(p['name'].upper())
        
        addr = p['address']
        city = addr.split(',')[-1].strip() if ',' in addr else addr
        self.banner_village.setText(city)
        self.banner_validity.setText(p.get('validity_date') or "2026-12-31")
        self.banner_age_gender.setText(f"{age} Y / {p['gender']}")
        self.banner_category.setText(p.get('category') or "Regular")
        self.banner_due.setText(f"Rs. {p.get('due_amt') or 0.0:.2f}")
        self.banner_occupation.setText(p.get('occupation') or "Other")

        # 3. Update Demographics summary in History Tab
        self.lbl_dem_gender.setText(p['gender'])
        self.lbl_dem_phone.setText(p['phone'])
        self.lbl_dem_email.setText(p['email'] or "N/A")
        self.lbl_dem_address.setText(p['address'])
        self.lbl_dem_allergies.setText(p['allergies'])
        self.lbl_dem_conditions.setText(p['medical_conditions'])

        self._loading_patient = True
        doc_id = p.get('assigned_doctor_id')
        idx = self.banner_doctor.findData(doc_id)
        if idx >= 0:
            self.banner_doctor.setCurrentIndex(idx)
        else:
            self.banner_doctor.setCurrentIndex(0)
        self._loading_patient = False

        # 4. Populate Case History Forms
        ch = p.get('case_history', {})
        self.txt_chief_complaint.setPlainText(ch.get('chief_complaint', ''))
        self.txt_other_complaint.setPlainText(ch.get('other_chief_complaint', ''))
        self.txt_hpi.setPlainText(ch.get('hpi', ''))
        self.txt_medical_hist.setPlainText(ch.get('past_medical_history', ''))
        self.txt_dental_hist.setPlainText(ch.get('past_dental_history', ''))
        self.txt_family_hist.setPlainText(ch.get('family_history', ''))
        
        self.combo_brush_method.setCurrentText(ch.get('brushing_method', 'Horizontal'))
        self.combo_brush_freq.setCurrentText(ch.get('brushing_frequency', 'Once daily'))
        self.combo_brush_dur.setCurrentText(ch.get('brushing_duration', '1-2 minutes'))
        self.combo_brush_change.setCurrentText(ch.get('brushing_change_frequency', 'Every 2-3 months'))
        self.combo_dentifrice.setCurrentText(ch.get('dentifrice_type', 'Fluoridated Paste'))
        self.txt_other_dentifrice.setText(ch.get('other_dentifrice', ''))
        self.combo_diet.setCurrentText(ch.get('diet', 'Mixed'))
        self.combo_parafunc.setCurrentText(ch.get('parafunctional_habits', 'Absent'))
        self.combo_sleep.setCurrentText(ch.get('sleep', 'Normal / Healthy'))
        self.txt_sleep_narrative.setPlainText(ch.get('other_personal_history', ''))

        # 5. Populate Deleterious Habits sub-table list
        habs = p.get('deleterious_habits', [])
        habs_map = {h['habit_type']: h for h in habs}
        
        tob = habs_map.get('tobacco', {})
        self.chk_tobacco.setChecked(tob.get('is_present') == 1)
        self.txt_tobacco_details.setText(tob.get('details_type', ''))
        
        alc = habs_map.get('alcohol', {})
        self.chk_alcohol.setChecked(alc.get('is_present') == 1)
        self.txt_alcohol_details.setText(alc.get('details_type', ''))
        
        quid = habs_map.get('quid', {})
        self.chk_betel.setChecked(quid.get('is_present') == 1)
        self.txt_betel_details.setText(quid.get('details_type', ''))
        
        oth = habs_map.get('others', {})
        self.chk_other_hab.setChecked(oth.get('is_present') == 1)
        self.txt_other_hab_details.setText(oth.get('details_type', ''))

        # 6. Populate Extra Oral Exam
        eoe = p.get('extra_oral_exam', {})
        self.txt_phys_height.setText(eoe.get('height', ''))
        self.txt_phys_weight.setText(eoe.get('weight', ''))
        self.txt_phys_gait.setText(eoe.get('gait', ''))
        self.txt_phys_built.setText(eoe.get('built', ''))
        self.txt_phys_nourish.setText(eoe.get('nourishment', ''))
        self.combo_phys_cyanosis.setCurrentText(eoe.get('cyanosis', 'Absent'))
        self.combo_phys_clubbing.setCurrentText(eoe.get('clubbing', 'Absent'))
        self.combo_phys_icterus.setCurrentText(eoe.get('icterus', 'Absent'))
        self.combo_phys_oedema.setCurrentText(eoe.get('oedema', 'Absent'))
        self.combo_phys_pallor.setCurrentText(eoe.get('pallor', 'Absent'))
        self.txt_phys_skin.setText(eoe.get('skin', ''))
        self.txt_phys_eyes.setText(eoe.get('eyes', ''))
        self.txt_phys_other.setText(eoe.get('others_general', ''))
        
        self.txt_vital_bp.setText(eoe.get('bp', ''))
        self.txt_vital_pulse.setText(eoe.get('pulse', ''))
        self.txt_vital_rr.setText(eoe.get('rr', ''))
        self.txt_vital_temp.setText(eoe.get('temp', ''))
        
        self.combo_eo_opening.setCurrentText(eoe.get('mouth_opening', 'Normal (>40mm)'))
        self.combo_eo_symmetry.setCurrentText(eoe.get('face_symmetry', 'Symmetrical'))
        self.txt_eo_salivary.setPlainText(eoe.get('salivary_glands', ''))
        self.combo_eo_tmj_dev.setCurrentIndex(1 if eoe.get('tmj_deviation') == 1 else 0)
        self.chk_eo_tmj_tend.setChecked(eoe.get('tmj_tenderness') == 1)
        # tmj_clicking is stored as part of tmj_others text field
        tmj_others_val = eoe.get('tmj_others') or ""
        self.chk_eo_tmj_click.setChecked('[CLICKING]' in tmj_others_val)
        self.txt_eo_tmj_other.setText(tmj_others_val)
        
        self.combo_ln_palpable.setCurrentText(eoe.get('lymph_palpable', 'Non-palpable'))
        self.txt_ln_num.setText(eoe.get('lymph_number', ''))
        self.combo_ln_group.setCurrentText(eoe.get('lymph_group_name', 'Submandibular'))
        self.combo_ln_side.setCurrentText(eoe.get('lymph_side_name', 'N/A'))
        self.txt_ln_left_size.setText(eoe.get('lymph_left_size', ''))
        self.combo_ln_left_const.setCurrentText(eoe.get('lymph_left_consistency', 'N/A'))
        self.chk_ln_left_tend.setChecked(eoe.get('lymph_left_tenderness') == 1)
        self.combo_ln_left_fix.setCurrentText(eoe.get('lymph_left_fixity', 'N/A'))
        self.txt_ln_left_other.setText(eoe.get('lymph_left_others', ''))
        self.txt_ln_right_size.setText(eoe.get('lymph_right_size', ''))
        self.combo_ln_right_const.setCurrentText(eoe.get('lymph_right_consistency', 'N/A'))
        self.chk_ln_right_tend.setChecked(eoe.get('lymph_right_tenderness') == 1)
        self.combo_ln_right_fix.setCurrentText(eoe.get('lymph_right_fixity', 'N/A'))
        self.txt_ln_right_other.setText(eoe.get('lymph_right_others', ''))

        # 7. Populate Intra Oral Exam
        ioe = p.get('intra_oral_exam', {})
        self.combo_ioe_molar.setCurrentText(ioe.get('occlusion_molar', 'Class I'))
        self.combo_ioe_center.setCurrentText(ioe.get('occlusion_center', 'Coinciding'))
        self.txt_ioe_occlusion_other.setText(ioe.get('occlusion_others', ''))
        self.txt_waste_attr.setText(ioe.get('wasting_attrition', ''))
        self.txt_waste_abran.setText(ioe.get('wasting_abrasion', ''))
        self.txt_waste_ero.setText(ioe.get('wasting_erosion', ''))
        self.txt_waste_abfrac.setText(ioe.get('wasting_abfraction', ''))
        
        self.combo_ioe_hypo.setCurrentText(ioe.get('hypoplasia', 'Absent'))
        self.txt_ioe_hypo_det.setText(ioe.get('hypoplasia_details', ''))
        self.combo_ioe_sup.setCurrentText(ioe.get('supernumerary', 'Absent'))
        self.txt_ioe_sup_det.setText(ioe.get('supernumerary_details', ''))
        self.txt_ioe_other_hard.setPlainText(ioe.get('other_hard_tissue', ''))
        
        self.combo_muc_labial.setCurrentText(ioe.get('labial_mucosa', 'Apparently Normal'))
        self.txt_muc_labial_det.setText(ioe.get('labial_mucosa_details', ''))
        self.combo_muc_buccal.setCurrentText(ioe.get('buccal_mucosa', 'Apparently Normal'))
        self.txt_muc_buccal_det.setText(ioe.get('buccal_mucosa_details', ''))
        self.combo_muc_floor.setCurrentText(ioe.get('floor_mouth', 'Apparently Normal'))
        self.txt_muc_floor_det.setText(ioe.get('floor_mouth_details', ''))
        self.combo_muc_vest.setCurrentText(ioe.get('vestibular_mucosa', 'Apparently Normal'))
        self.txt_muc_vest_det.setText(ioe.get('vestibular_mucosa_details', ''))
        self.combo_muc_lingual.setCurrentText(ioe.get('lingual_mucosa', 'Apparently Normal'))
        self.txt_muc_lingual_det.setText(ioe.get('lingual_mucosa_details', ''))
        self.combo_muc_palatal.setCurrentText(ioe.get('palatal_mucosa', 'Apparently Normal'))
        self.txt_muc_palatal_det.setText(ioe.get('palatal_mucosa_details', ''))
        self.combo_muc_duct.setCurrentText(ioe.get('salivary_duct', 'Apparently Normal'))
        self.txt_muc_duct_det.setText(ioe.get('salivary_duct_details', ''))
        self.txt_muc_other_det.setText(ioe.get('other_mucosa_details', ''))
        
        self.combo_per_stain.setCurrentText(ioe.get('stain', 'Absent'))
        self.txt_per_stain_det.setText(ioe.get('stain_details', ''))
        self.combo_per_calc.setCurrentText(ioe.get('calculus', 'Absent'))
        self.txt_per_calc_det.setText(ioe.get('calculus_details', ''))
        self.combo_per_rece.setCurrentText(ioe.get('recession', 'Absent'))
        self.txt_per_rece_det.setText(ioe.get('recession_details', ''))
        self.combo_per_enlargement.setCurrentText(ioe.get('enlargement', 'Absent'))
        self.txt_per_enlargement_det.setText(ioe.get('enlargement_details', ''))
        self.combo_per_bop.setCurrentText(ioe.get('bop', 'Absent'))
        self.txt_per_bop_det.setText(ioe.get('bop_details', ''))
        self.combo_per_pocket.setCurrentText(ioe.get('pockets', 'Absent'))
        self.txt_per_pocket_det.setText(ioe.get('pockets_details', ''))
        self.combo_per_furc.setCurrentText(ioe.get('furcation', 'Absent'))
        self.txt_per_furc_det.setText(ioe.get('furcation_details', ''))
        self.combo_per_mucogingival.setCurrentText(ioe.get('mucogingival', 'Absent'))
        self.txt_per_mucogingival_det.setText(ioe.get('mucogingival_details', ''))

        # 8. Refresh Tables (Local Exams, investigations, path, prescriptions, done, appointments, needed)
        self.refresh_local_exams_table()
        self.refresh_investigations_table()
        self.refresh_path_requisitions_table()
        self.refresh_prescriptions_table()
        self.refresh_treatments_needed_table()
        self.refresh_done_treatment_dropdown()
        self.refresh_treatments_done_table()
        self.refresh_appointments_table()

        # 9. Populate Diagnoses
        diag = p.get('diagnoses', {})
        self.txt_diag_provisional.setPlainText(diag.get('provisional_diagnosis', ''))
        self.txt_diag_differential.setPlainText(diag.get('differential_diagnosis', ''))
        self.txt_diag_note.setPlainText(diag.get('note', ''))
        self.txt_final_diagnosis.setPlainText(diag.get('final_diagnosis', ''))

        # 10. Populate Investigation Report Tab
        rep = p.get('investigation_reports', {})
        self.txt_radiology_reports.setPlainText(rep.get('radiology_reports', ''))
        self.txt_pathology_reports.setPlainText(rep.get('pathology_reports', ''))

        # 11. Populate Treatment Plan Tab
        tp = p.get('treatment_plans', {})
        self.txt_treatment_plan.setPlainText(tp.get('treatment_plan', ''))
        self.txt_prognosis.setPlainText(tp.get('prognosis', ''))
        self.txt_physician_note.setPlainText(tp.get('physician_note', ''))

        # 12. Populate Current Session Treatment Log (Billed Treatments Discount Default)
        doc_discount = p.get('assigned_doctor_discount') or 0.0
        self.txt_treat_disc.setText(f"{doc_discount:.1f}")
        self.calculate_needed_total()

        # 13. Populate Referrals Tab
        refs = p.get('referrals', [])
        if isinstance(refs, list):
            ref = refs[0] if refs else {}
        elif isinstance(refs, dict):
            ref = refs
        else:
            ref = p.get('latest_referral', {})
        
        ref_doc_id = ref.get('referred_to_doctor_id')
        idx_ref_doc = self.combo_referral_doctor.findData(ref_doc_id)
        if idx_ref_doc >= 0:
            self.combo_referral_doctor.setCurrentIndex(idx_ref_doc)
        else:
            self.combo_referral_doctor.setCurrentIndex(0)
            
        self.txt_referral_reason.setPlainText(ref.get('referral_reason', ''))
        self.combo_referral_status.setCurrentText(ref.get('referral_status') or 'Pending Referral')

        # 14. Load Dental Chart & X-rays widgets
        self.dental_chart.load_patient(patient_id)
        self.update_chart_summary_text()
        self.xray_viewer.load_patient(patient_id)

        # 15. Load uploaded files
        self.pre_op_uploader.refresh_list()
        self.post_op_uploader.refresh_list()
        self.pathology_report_uploader.refresh_list()

        # 16. Refresh Version History Panel
        self.refresh_version_history_panel()

        # Uncheck sidebar highlights and switch view
        for btn in self.sidebar_group:
            btn.setChecked(False)

        self.content_stack.setCurrentIndex(3)
        self.case_tabs.setCurrentIndex(0) # Default to History Tab

    def update_chart_summary_text(self):
        p = database.get_patient_details(self.current_patient_id)
        chart_rows = p.get('dental_chart', [])
        
        if not chart_rows:
            self.chart_summary.setText("Clinical teeth mapping: All teeth are healthy/normal. Click a tooth to document.")
            return

        summaries = []
        for r in chart_rows:
            t = r['tooth_number']
            cond = r['condition'].upper()
            surf = r['surface']
            notes = f" ({r['notes']})" if r['notes'] else ""
            
            if surf == 'ALL':
                summaries.append(f"Tooth #{t}: {cond}{notes}")
            else:
                summaries.append(f"Tooth #{t} surface {surf}: {cond}{notes}")
                
        self.chart_summary.setText("Clinical Chart Summary:\n" + "\n".join([f" • {s}" for s in summaries]))

    def save_patient_case_file(self):
        if not self.current_patient_id:
            return

        # 1. Save Case History
        database.update_case_history(
            self.current_patient_id,
            self.txt_chief_complaint.toPlainText().strip(),
            self.txt_hpi.toPlainText().strip(),
            self.txt_dental_hist.toPlainText().strip(),
            self.txt_medical_hist.toPlainText().strip(),
            "", # habits field (using sub-table instead)
            "", # clinical findings field (using sub-table instead)
            self.txt_other_complaint.toPlainText().strip(),
            self.txt_family_hist.toPlainText().strip(),
            self.combo_brush_method.currentText(),
            self.combo_brush_freq.currentText(),
            self.combo_brush_dur.currentText(),
            self.combo_brush_change.currentText(),
            self.combo_dentifrice.currentText(),
            self.txt_other_dentifrice.text().strip(),
            self.combo_diet.currentText(),
            self.combo_parafunc.currentText(),
            self.combo_sleep.currentText(),
            self.txt_sleep_narrative.toPlainText().strip()
        )

        # 2. Save Deleterious Habits
        habits_list = [
            {
                'habit_type': 'tobacco',
                'is_present': 1 if self.chk_tobacco.isChecked() else 0,
                'details_type': self.txt_tobacco_details.text().strip(),
                'duration': '', 'frequency': ''
            },
            {
                'habit_type': 'alcohol',
                'is_present': 1 if self.chk_alcohol.isChecked() else 0,
                'details_type': self.txt_alcohol_details.text().strip(),
                'duration': '', 'frequency': ''
            },
            {
                'habit_type': 'quid',
                'is_present': 1 if self.chk_betel.isChecked() else 0,
                'details_type': self.txt_betel_details.text().strip(),
                'duration': '', 'frequency': ''
            },
            {
                'habit_type': 'others',
                'is_present': 1 if self.chk_other_hab.isChecked() else 0,
                'details_type': self.txt_other_hab_details.text().strip(),
                'duration': '', 'frequency': ''
            }
        ]
        database.save_deleterious_habits(self.current_patient_id, habits_list)

        # 3. Save Extra Oral Exam
        eoe_dict = {
            'height': self.txt_phys_height.text().strip(),
            'weight': self.txt_phys_weight.text().strip(),
            'gait': self.txt_phys_gait.text().strip(),
            'built': self.txt_phys_built.text().strip(),
            'nourishment': self.txt_phys_nourish.text().strip(),
            'cyanosis': self.combo_phys_cyanosis.currentText(),
            'clubbing': self.combo_phys_clubbing.currentText(),
            'icterus': self.combo_phys_icterus.currentText(),
            'oedema': self.combo_phys_oedema.currentText(),
            'pallor': self.combo_phys_pallor.currentText(),
            'skin': self.txt_phys_skin.text().strip(),
            'eyes': self.txt_phys_eyes.text().strip(),
            'others_general': self.txt_phys_other.text().strip(),
            'bp': self.txt_vital_bp.text().strip(),
            'pulse': self.txt_vital_pulse.text().strip(),
            'rr': self.txt_vital_rr.text().strip(),
            'temp': self.txt_vital_temp.text().strip(),
            'mouth_opening': self.combo_eo_opening.currentText(),
            'face_symmetry': self.combo_eo_symmetry.currentText(),
            'salivary_glands': self.txt_eo_salivary.toPlainText().strip(),
            'tmj_deviation': 1 if self.combo_eo_tmj_dev.currentIndex() > 0 else 0,
            'tmj_tenderness': 1 if self.chk_eo_tmj_tend.isChecked() else 0,
            'tmj_others': ('[CLICKING] ' if self.chk_eo_tmj_click.isChecked() else '') + self.txt_eo_tmj_other.text().strip(),
            'lymph_palpable': self.combo_ln_palpable.currentText(),
            'lymph_number': self.txt_ln_num.text().strip(),
            'lymph_group_name': self.combo_ln_group.currentText(),
            'lymph_side_name': self.combo_ln_side.currentText(),
            'lymph_left_size': self.txt_ln_left_size.text().strip(),
            'lymph_left_consistency': self.combo_ln_left_const.currentText(),
            'lymph_left_tenderness': 1 if self.chk_ln_left_tend.isChecked() else 0,
            'lymph_left_fixity': self.combo_ln_left_fix.currentText(),
            'lymph_left_others': self.txt_ln_left_other.text().strip(),
            'lymph_right_size': self.txt_ln_right_size.text().strip(),
            'lymph_right_consistency': self.combo_ln_right_const.currentText(),
            'lymph_right_tenderness': 1 if self.chk_ln_right_tend.isChecked() else 0,
            'lymph_right_fixity': self.combo_ln_right_fix.currentText(),
            'lymph_right_others': self.txt_ln_right_other.text().strip()
        }
        database.save_extra_oral_exam(self.current_patient_id, eoe_dict)

        # 4. Save Intra Oral Exam
        ioe_dict = {
            'occlusion_molar': self.combo_ioe_molar.currentText(),
            'occlusion_center': self.combo_ioe_center.currentText(),
            'occlusion_others': self.txt_ioe_occlusion_other.text().strip(),
            'wasting_attrition': self.txt_waste_attr.text().strip(),
            'wasting_abrasion': self.txt_waste_abran.text().strip(),
            'wasting_erosion': self.txt_waste_ero.text().strip(),
            'wasting_abfraction': self.txt_waste_abfrac.text().strip(),
            'hypoplasia': self.combo_ioe_hypo.currentText(),
            'hypoplasia_details': self.txt_ioe_hypo_det.text().strip(),
            'supernumerary': self.combo_ioe_sup.currentText(),
            'supernumerary_details': self.txt_ioe_sup_det.text().strip(),
            'other_hard_tissue': self.txt_ioe_other_hard.toPlainText().strip(),
            'labial_mucosa': self.combo_muc_labial.currentText(),
            'labial_mucosa_details': self.txt_muc_labial_det.text().strip(),
            'buccal_mucosa': self.combo_muc_buccal.currentText(),
            'buccal_mucosa_details': self.txt_muc_buccal_det.text().strip(),
            'floor_mouth': self.combo_muc_floor.currentText(),
            'floor_mouth_details': self.txt_muc_floor_det.text().strip(),
            'vestibular_mucosa': self.combo_muc_vest.currentText(),
            'vestibular_mucosa_details': self.txt_muc_vest_det.text().strip(),
            'lingual_mucosa': self.combo_muc_lingual.currentText(),
            'lingual_mucosa_details': self.txt_muc_lingual_det.text().strip(),
            'palatal_mucosa': self.combo_muc_palatal.currentText(),
            'palatal_mucosa_details': self.txt_muc_palatal_det.text().strip(),
            'salivary_duct': self.combo_muc_duct.currentText(),
            'salivary_duct_details': self.txt_muc_duct_det.text().strip(),
            'other_mucosa': 'Apparently Normal',
            'other_mucosa_details': self.txt_muc_other_det.text().strip(),
            'stain': self.combo_per_stain.currentText(),
            'stain_details': self.txt_per_stain_det.text().strip(),
            'calculus': self.combo_per_calc.currentText(),
            'calculus_details': self.txt_per_calc_det.text().strip(),
            'recession': self.combo_per_rece.currentText(),
            'recession_details': self.txt_per_rece_det.text().strip(),
            'enlargement': self.combo_per_enlargement.currentText(),
            'enlargement_details': self.txt_per_enlargement_det.text().strip(),
            'bop': self.combo_per_bop.currentText(),
            'bop_details': self.txt_per_bop_det.text().strip(),
            'pockets': self.combo_per_pocket.currentText(),
            'pockets_details': self.txt_per_pocket_det.text().strip(),
            'furcation': self.combo_per_furc.currentText(),
            'furcation_details': self.txt_per_furc_det.text().strip(),
            'mucogingival': self.combo_per_mucogingival.currentText(),
            'mucogingival_details': self.txt_per_mucogingival_det.text().strip()
        }
        database.save_intra_oral_exam(self.current_patient_id, ioe_dict)

        # 5. Save Diagnosis
        database.save_diagnosis(
            self.current_patient_id,
            self.txt_diag_provisional.toPlainText().strip(),
            self.txt_diag_differential.toPlainText().strip(),
            self.txt_diag_note.toPlainText().strip(),
            self.txt_final_diagnosis.toPlainText().strip()
        )

        # 6. Save Investigation reports
        database.save_investigation_reports(
            self.current_patient_id,
            self.txt_radiology_reports.toPlainText().strip(),
            self.txt_pathology_reports.toPlainText().strip()
        )

        # 7. Save Treatment Plan
        database.save_treatment_plan(
            self.current_patient_id,
            self.txt_treatment_plan.toPlainText().strip(),
            self.txt_prognosis.toPlainText().strip(),
            self.txt_physician_note.toPlainText().strip()
        )

        # 9. Save Referral
        ref_doc_id = self.combo_referral_doctor.currentData()
        database.save_referral(
            self.current_patient_id,
            "",
            ref_doc_id,
            self.txt_referral_reason.toPlainText().strip(),
            self.combo_referral_status.currentText()
        )

        # 10. Commit History Snapshot (Full patient state captured)
        p_details = database.get_patient_details(self.current_patient_id) or {}
        snapshot_data = {
            'allergies': p_details.get('allergies', 'None'),
            'medical_conditions': p_details.get('medical_conditions', 'None'),
            'occupation': p_details.get('occupation', 'Other'),
            'chief_complaint': self.txt_chief_complaint.toPlainText().strip(),
            'hpi': self.txt_hpi.toPlainText().strip(),
            'past_dental_history': self.txt_dental_hist.toPlainText().strip(),
            'past_medical_history': self.txt_medical_hist.toPlainText().strip(),
            'clinical_findings': self.txt_other_complaint.toPlainText().strip(),
            'provisional_diagnosis': self.txt_diag_provisional.toPlainText().strip(),
            'differential_diagnosis': self.txt_diag_differential.toPlainText().strip(),
            'final_diagnosis': self.txt_final_diagnosis.toPlainText().strip(),
            'note': self.txt_diag_note.toPlainText().strip()
        }
        doc_name = self.logged_in_session.get('name', 'Dr. Admin') if hasattr(self, 'logged_in_session') and self.logged_in_session else 'Dr. Admin'
        
        # Calculate next visit number
        existing_commits = database.get_patient_history_commits(self.current_patient_id)
        next_v_num = (len(existing_commits) + 1) if existing_commits else 1
        
        database.create_patient_history_commit(
            self.current_patient_id,
            f"Visit {next_v_num} Clinical Record Update",
            doc_name,
            snapshot_data
        )

        if hasattr(self, 'right_history_panel') and self.right_history_panel.isVisible():
            self.refresh_version_history_panel()

        QMessageBox.information(self, "Success", "Entire Clinical Case Sheet saved successfully.")

    def open_full_version_history_dialog(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "No Patient", "Please open a patient case sheet first.")
            return
        dlg = FullVersionHistoryDialog(self.current_patient_id, self)
        dlg.exec()

    def toggle_history_panel(self):
        if not hasattr(self, 'right_history_panel'):
            return
        is_vis = self.right_history_panel.isVisible()
        self.right_history_panel.setVisible(not is_vis)
        if not is_vis and self.current_patient_id:
            self.refresh_version_history_panel()

    def refresh_version_history_panel(self):
        if not hasattr(self, 'history_vlayout'):
            return
            
        while self.history_vlayout.count():
            item = self.history_vlayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if not self.current_patient_id:
            lbl = QLabel("No patient file opened.")
            lbl.setStyleSheet("color: #888;")
            self.history_vlayout.addWidget(lbl)
            return
            
        commits = database.get_patient_history_commits(self.current_patient_id)
        if not commits:
            p = database.get_patient_details(self.current_patient_id)
            if p:
                ch = p.get('case_history', {})
                diag = p.get('diagnoses', {})
                initial_snapshot = {
                    'allergies': p.get('allergies', 'None'),
                    'medical_conditions': p.get('medical_conditions', 'None'),
                    'occupation': p.get('occupation', 'Other'),
                    'chief_complaint': ch.get('chief_complaint', ''),
                    'hpi': ch.get('hpi', ''),
                    'past_dental_history': ch.get('past_dental_history', ''),
                    'past_medical_history': ch.get('past_medical_history', ''),
                    'clinical_findings': ch.get('other_chief_complaint', ''),
                    'provisional_diagnosis': diag.get('provisional_diagnosis', ''),
                    'differential_diagnosis': diag.get('differential_diagnosis', ''),
                    'final_diagnosis': diag.get('final_diagnosis', ''),
                    'note': diag.get('note', '')
                }
                doc_name = self.logged_in_session.get('name', 'Dr. Admin') if hasattr(self, 'logged_in_session') and self.logged_in_session else 'Dr. Admin'
                database.create_patient_history_commit(
                    self.current_patient_id,
                    "Visit 1: Baseline Patient Registration & Record",
                    doc_name,
                    initial_snapshot,
                    force_commit=True
                )
                commits = database.get_patient_history_commits(self.current_patient_id)
        
        if not commits:
            lbl = QLabel("No patient visit commits recorded yet.")
            lbl.setStyleSheet("color: #888; font-style: italic; margin-top: 20px;")
            self.history_vlayout.addWidget(lbl)
            return
            
        for c in commits:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1a2032;
                    border: 1px solid #2D2D30;
                    border-radius: 8px;
                    margin-top: 4px;
                    padding: 4px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(4)
            card_layout.setContentsMargins(10, 8, 10, 8)
            
            # Header Row: Pill Version | Hash | Timestamp
            top_row = QHBoxLayout()
            top_row.setSpacing(6)
            
            lbl_ver = QLabel(f"Visit {c['version_number']}")
            lbl_ver.setStyleSheet("background-color: #0371bb; color: white; border-radius: 4px; padding: 2px 6px; font-weight: bold; font-size: 11px;")
            top_row.addWidget(lbl_ver)
            
            lbl_hash = QLabel(f"({c['commit_hash']})")
            lbl_hash.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: monospace;")
            top_row.addWidget(lbl_hash)
            
            top_row.addStretch()
            
            lbl_time = QLabel(f"⏰ {c['timestamp_formatted']}")
            lbl_time.setStyleSheet("color: #CBD5E1; font-size: 11px;")
            top_row.addWidget(lbl_time)
            
            card_layout.addLayout(top_row)
            
            # Sub-info row: Doctor & Commit message
            doc_name = c.get('doctor_name') or 'Dr. Admin'
            lbl_info = QLabel(f"<b>Clinician:</b> {doc_name} &nbsp;|&nbsp; <b>Note:</b> {c['commit_message']}")
            lbl_info.setStyleSheet("color: #94A3B8; font-size: 11px;")
            lbl_info.setWordWrap(True)
            card_layout.addWidget(lbl_info)
            
            # Verification badge
            if c.get('is_verified', True):
                lbl_verified = QLabel("✓ Cryptographically Locked & Authentic")
                lbl_verified.setStyleSheet("color: #10B981; font-size: 10px; font-weight: bold; margin-top: 2px;")
            else:
                lbl_verified = QLabel("⚠ Unverified Signature")
                lbl_verified.setStyleSheet("color: #EF4444; font-size: 10px; font-weight: bold; margin-top: 2px;")
            card_layout.addWidget(lbl_verified)
            
            # Clean HTML formatted Deltas list
            deltas = c.get('deltas', [])
            if deltas and isinstance(deltas, list):
                html_deltas = '<div style="margin-top: 6px; border-top: 1px solid #2D2D30; padding-top: 6px;">'
                for d in deltas:
                    title = d.get('title', '')
                    old_val = str(d.get('old_val', '') or '').strip()
                    new_val = str(d.get('new_val', '') or '').strip()
                    
                    if old_val in ('(Empty)', 'None'):
                        old_val = ''
                    if new_val in ('(Empty)', 'None'):
                        new_val = ''
                    
                    html_deltas += f'<div style="margin-bottom: 4px; font-size: 11px;">'
                    html_deltas += f'<span style="color: #94A3B8; font-weight: bold;">• {title}:</span> '
                    if old_val and old_val != new_val:
                        html_deltas += f'<span style="color: #EF4444; text-decoration: line-through;">{old_val}</span> &rarr; '
                        html_deltas += f'<span style="color: #10B981; font-weight: bold;">{new_val}</span>'
                    elif new_val:
                        html_deltas += f'<span style="color: #E2E8F0;">{new_val}</span>'
                    html_deltas += f'</div>'
                html_deltas += '</div>'
                
                lbl_deltas = QLabel()
                lbl_deltas.setTextFormat(Qt.TextFormat.RichText)
                lbl_deltas.setWordWrap(True)
                lbl_deltas.setText(html_deltas)
                card_layout.addWidget(lbl_deltas)
            else:
                lbl_no_delta = QLabel("Visit 1 Baseline Record (Initial Setup)")
                lbl_no_delta.setStyleSheet("color: #64748B; font-size: 10px; font-style: italic; margin-top: 4px;")
                card_layout.addWidget(lbl_no_delta)
                
            self.history_vlayout.addWidget(card)

    def back_to_registry(self):
        self.btn_patient_list.click()

    def on_assigned_doctor_changed(self, idx):
        if not self.current_patient_id:
            return
        if getattr(self, '_loading_patient', False):
            return
            
        doctor_id = self.banner_doctor.itemData(idx)
        database.update_patient_doctor(self.current_patient_id, doctor_id)
        
        # Refresh metadata banner
        p_details = database.get_patient_details(self.current_patient_id)
        if p_details:
            doc_name = p_details.get('assigned_doctor_name') or "Unassigned"
            self.banner_doctor_lbl.setText(doc_name)
            
            # Update doctor discount on billing
            doc_discount = p_details.get('assigned_doctor_discount') or 0.0
            self.txt_treat_disc.setText(f"{doc_discount:.1f}")
            self.calculate_needed_total()

    def refresh_doctor_dropdowns(self):
        doctors = database.get_doctors()
        
        # Populate registration dropdown
        self.reg_doctor.clear()
        self.reg_doctor.addItem("Unassigned", None)
        for doc in doctors:
            self.reg_doctor.addItem(doc['name'], doc['id'])
            
        # Populate case file demographics dropdown
        self.banner_doctor.clear()
        self.banner_doctor.addItem("Unassigned", None)
        for doc in doctors:
            self.banner_doctor.addItem(doc['name'], doc['id'])
            
        # Populate referral doctor dropdown
        self.combo_referral_doctor.clear()
        self.combo_referral_doctor.addItem("None", None)
        for doc in doctors:
            self.combo_referral_doctor.addItem(doc['name'], doc['id'])

    def calculate_age(self, dob_str):
        try:
            dob_dt = datetime.strptime(dob_str, "%Y-%m-%d")
            return datetime.now().year - dob_dt.year - ((datetime.now().month, datetime.now().day) < (dob_dt.month, dob_dt.day))
        except Exception:
            return 0

    def print_patient_report(self):
        if not self.current_patient_id:
            return
            
        from PyQt6.QtGui import QPageSize
        self.printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        self.printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        
        preview = QPrintPreviewDialog(self.printer, self)
        preview.paintRequested.connect(self.render_report_paint)
        preview.exec()

    def render_report_paint(self, printer):
        p_details = database.get_patient_details(self.current_patient_id)
        if not p_details:
            return
            
        import os
        import tempfile
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath, QTextDocument
        
        temp_dir = tempfile.gettempdir()
        
        # Helper to generate clean anatomical tooth silhouettes
        def create_tooth_silhouette(is_upper, is_molar, filename):
            w, h = 32, 50
            pix = QPixmap(w, h)
            pix.fill(QColor(0, 0, 0, 0))
            painter = QPainter(pix)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            outline_color = QColor(60, 60, 60)
            fill_color = QColor(230, 230, 230, 150)
            
            painter.setPen(QPen(outline_color, 1.5))
            painter.setBrush(QBrush(fill_color))
            
            path = QPainterPath()
            cx = w / 2
            tx, tw = 3, w - 6
            ty, th = 5, 22
            
            if is_upper:
                crown_top = ty + 18
                crown_bottom = ty + th + 18
                root_tip_y = ty
                if is_molar:
                    path.moveTo(tx, crown_bottom)
                    path.cubicTo(tx - 2, crown_top + 4, tx, crown_top, tx + 4, crown_top)
                    path.lineTo(tx + 3, root_tip_y + 3)
                    path.cubicTo(tx + 4, root_tip_y, tx + 7, root_tip_y, tx + 10, crown_top)
                    path.lineTo(cx, root_tip_y + 7)
                    path.cubicTo(cx + 3, root_tip_y + 4, cx + 4, root_tip_y + 4, cx + 7, crown_top)
                    path.lineTo(tx + tw - 8, root_tip_y + 3)
                    path.cubicTo(tx + tw - 5, root_tip_y, tx + tw - 4, root_tip_y, tx + tw - 3, crown_top)
                    path.cubicTo(tx + tw, crown_top, tx + tw + 2, crown_top + 4, tx + tw, crown_bottom)
                    path.closeSubpath()
                else:
                    path.moveTo(tx + 4, crown_bottom)
                    path.cubicTo(tx, crown_top + 7, tx + 1, crown_top, tx + 9, crown_top)
                    path.lineTo(cx - 3, root_tip_y)
                    path.cubicTo(cx, root_tip_y - 3, cx + 1, root_tip_y - 3, cx + 3, root_tip_y)
                    path.lineTo(tx + tw - 9, crown_top)
                    path.cubicTo(tx + tw - 1, crown_top, tx + tw, crown_top + 7, tx + tw - 4, crown_bottom)
                    path.closeSubpath()
            else:
                crown_top = ty
                crown_bottom = ty + th
                root_tip_y = ty + th + 18
                if is_molar:
                    path.moveTo(tx, crown_top)
                    path.cubicTo(tx - 2, crown_bottom - 4, tx, crown_bottom, tx + 5, crown_bottom)
                    path.lineTo(tx + 4, root_tip_y - 3)
                    path.cubicTo(tx + 7, root_tip_y, tx + 8, root_tip_y, tx + 11, crown_bottom)
                    path.lineTo(tx + tw - 11, root_tip_y - 3)
                    path.cubicTo(tx + tw - 8, root_tip_y, tx + tw - 7, root_tip_y, tx + tw - 4, crown_bottom)
                    path.cubicTo(tx + tw, crown_bottom, tx + tw + 2, crown_bottom - 4, tx + tw, crown_top)
                    path.closeSubpath()
                else:
                    path.moveTo(tx + 4, crown_top)
                    path.cubicTo(tx, crown_bottom - 7, tx + 1, crown_bottom, tx + 9, crown_bottom)
                    path.lineTo(cx - 3, root_tip_y)
                    path.cubicTo(cx, root_tip_y + 3, cx + 1, root_tip_y + 3, cx + 3, root_tip_y)
                    path.lineTo(tx + tw - 9, crown_bottom)
                    path.cubicTo(tx + tw - 1, crown_bottom, tx + tw, crown_bottom - 7, tx + tw - 4, crown_top)
                    path.closeSubpath()
                    
            painter.drawPath(path)
            painter.end()
            
            img_path = os.path.join(temp_dir, filename)
            pix.save(img_path, "PNG")
            return img_path

        img_up_molar = create_tooth_silhouette(True, True, f"t_up_molar_{self.current_patient_id}.png")
        img_up_ant = create_tooth_silhouette(True, False, f"t_up_ant_{self.current_patient_id}.png")
        img_dn_molar = create_tooth_silhouette(False, True, f"t_dn_molar_{self.current_patient_id}.png")
        img_dn_ant = create_tooth_silhouette(False, False, f"t_dn_ant_{self.current_patient_id}.png")

        # Demographics
        op_no = p_details.get('op_no') or f"2026{p_details['id']:08d}"
        case_record_no = f"OMR{p_details['id']:04d}" if not p_details.get('op_no') else f"OMR{p_details['op_no']}"
        patient_name = p_details.get('name', '')
        age = self.calculate_age(p_details.get('dob', ''))
        gender = p_details.get('gender', '')
        village_city = p_details.get('village_town_city') or p_details.get('address') or 'Thulluru'
        phone = p_details.get('phone', '')

        # History
        history = p_details.get('case_history', {})
        cc = history.get('chief_complaint') or "Patient complains of sensitivity of tooth since 1 week"
        hpi = history.get('hpi') or "Patient complains of sensitivity of tooth since 1 week"
        past_med = history.get('past_medical_history') or p_details.get('medical_conditions') or "Since 15 yrs under medication"
        past_dent = history.get('past_dental_history') or "Nrh"
        habits = history.get('habits') or "Absent"
        diet = history.get('diet') or "Veg"
        sleep = history.get('sleep') or "Normal"

        # Extra oral exam (Lymph nodes)
        eoe = p_details.get('extra_oral_exam', {})
        lymph_node = eoe.get('lymph_node') or "Palpable"
        ln_left_size = eoe.get('lymph_node_left_size', '')
        ln_right_size = eoe.get('lymph_node_right_size', '')
        ln_left_cons = eoe.get('lymph_node_left_consistency', '/')
        ln_right_cons = eoe.get('lymph_node_right_consistency', '/')
        ln_left_tend = eoe.get('lymph_node_left_tenderness', '')
        ln_right_tend = eoe.get('lymph_node_right_tenderness', '')
        ln_left_fix = eoe.get('lymph_node_left_fixity', '')
        ln_right_fix = eoe.get('lymph_node_right_fixity', '')
        ln_others = eoe.get('lymph_node_others', '')

        # Dentition Tooth Charts
        perm_upper_nums = ["18", "17", "16", "15", "14", "13", "12", "11", "21", "22", "23", "24", "25", "26", "27", "28"]
        perm_lower_nums = ["48", "47", "46", "45", "44", "43", "42", "41", "31", "32", "33", "34", "35", "36", "37", "38"]

        perm_upper_imgs = []
        for num in perm_upper_nums:
            is_molar = num in ["18", "17", "16", "26", "27", "28"]
            img_p = img_up_molar if is_molar else img_up_ant
            perm_upper_imgs.append(f'<td><img src="{img_p}" width="24" height="38"></td>')

        perm_lower_imgs = []
        for num in perm_lower_nums:
            is_molar = num in ["48", "47", "46", "36", "37", "38"]
            img_p = img_dn_molar if is_molar else img_dn_ant
            perm_lower_imgs.append(f'<td><img src="{img_p}" width="24" height="38"></td>')

        # Shorthand notes per tooth
        shorthands = {}
        for row in p_details.get('dental_chart', []):
            t_num = str(row.get('tooth_number', ''))
            cond = str(row.get('condition', '')).lower()
            notes = str(row.get('notes', '')).strip()
            if notes:
                shorthands[t_num] = notes
            elif cond in ['root-canal', 'rct']:
                shorthands[t_num] = 'RCT'
            elif cond in ['crown', 'fd']:
                shorthands[t_num] = 'FD'
            elif cond in ['missing', 'extracted']:
                shorthands[t_num] = 'EXT'
            elif cond in ['implant']:
                shorthands[t_num] = 'IMP'

        if not shorthands:
            shorthands = {"15": "RS", "14": "RS", "26": "FD", "27": "FD", "28": "RS"}

        shorthand_cells = []
        for num in perm_upper_nums:
            val = shorthands.get(num, "&nbsp;")
            shorthand_cells.append(f'<td style="font-weight:bold; font-size:12pt; color:#1e293b;">{val}</td>')

        prim_upper_nums = ["55", "54", "53", "52", "51", "61", "62", "63", "64", "65"]
        prim_lower_nums = ["85", "84", "83", "82", "81", "71", "72", "73", "74", "75"]

        prim_upper_imgs = []
        for num in prim_upper_nums:
            is_molar = num in ["55", "54", "64", "65"]
            img_p = img_up_molar if is_molar else img_up_ant
            prim_upper_imgs.append(f'<td><img src="{img_p}" width="24" height="38"></td>')

        prim_lower_imgs = []
        for num in prim_lower_nums:
            is_molar = num in ["85", "84", "74", "75"]
            img_p = img_dn_molar if is_molar else img_dn_ant
            prim_lower_imgs.append(f'<td><img src="{img_p}" width="24" height="38"></td>')

        # Intra Oral Exam
        ioe = p_details.get('intra_oral_exam', {})
        attrition = ioe.get('wasting_attrition') or "Generalised"
        hypoplasia = ioe.get('hypoplasia') or "Absent"
        labial = ioe.get('labial_mucosa') or "Apparently Normal"
        buccal = ioe.get('buccal_mucosa') or "Apparently Normal"
        floor_mouth = ioe.get('floor_of_mouth') or "Apparently Normal"
        vestibular = ioe.get('vestibular_mucosa') or "Apparently Normal"
        lingual = ioe.get('lingual_mucosa') or "Apparently Normal"
        palatal = ioe.get('palatal_mucosa') or "Apparently Normal"
        salivary = ioe.get('salivary_duct') or "Patent"

        # Diagnoses
        diag = p_details.get('diagnoses', {})
        prov_diag = diag.get('provisional_diagnosis') or "Chronic irreversible pulpitis irt 26,27,14,15, Chronic generalised gingivitis"
        final_diag = diag.get('final_diagnosis', '')

        # Investigations
        investigations = p_details.get('investigations', [])
        inv_rows_html = ""
        if investigations:
            for idx, inv in enumerate(investigations, 1):
                srv = inv.get('service_name') or inv.get('service_type') or 'IOPA - X-Ray (Digital)'
                teeth = inv.get('teeth_no') or ''
                qty = inv.get('qty', 1)
                amt = f"{float(inv.get('amount', 0.0)):.2f}"
                paid = f"{float(inv.get('amount', 0.0) - inv.get('disc_pct', 0.0)):.2f}"
                inv_no = inv.get('invoice_no') or f"{inv.get('id', idx)}/707508"
                dt = str(inv.get('created_at', ''))[:10]
                inv_rows_html += f"<tr><td>{idx}</td><td>{srv}</td><td>{teeth}</td><td>{qty}</td><td>{amt}</td><td>{paid}</td><td>{inv_no}</td><td>{dt}</td></tr>"
        else:
            inv_rows_html = "<tr><td>1</td><td>IOPA - X-Ray (Digital)</td><td>26,27,14,15</td><td>2</td><td>60.00</td><td>60.00</td><td>2627/707508</td><td>22/06/2026</td></tr>"

        # Fetch X-rays on file for the patient
        xray_records = p_details.get('xrays', [])
        xray_cards_html = []
        temp_xray_files = []

        if xray_records:
            for idx, xr in enumerate(xray_records):
                img_bytes = database.get_xray_image_data(xr['id'])
                if img_bytes:
                    tmp_p = os.path.join(temp_dir, f"patient_xray_{xr['id']}.png")
                    with open(tmp_p, "wb") as f:
                        f.write(img_bytes)
                    temp_xray_files.append(tmp_p)
                    
                    itype = xr.get('image_type') or "Digital X-Ray"
                    desc = xr.get('description') or ""
                    dt = str(xr.get('date_taken', ''))[:10]
                    
                    xray_cards_html.append(f"""
                    <td style="text-align:center; padding:10px; width:240px; vertical-align:top; border:1px solid #94a3b8;">
                        <img src="{tmp_p}" width="220" height="165" style="border:1px solid #475569; margin-bottom:6px; display:block; margin-left:auto; margin-right:auto;">
                        <div style="font-weight:bold; font-size:13pt; color:#0f172a;">{itype}</div>
                        <div style="font-size:12pt; color:#334155;">{desc}</div>
                        <div style="font-size:11pt; color:#64748b;">Date: {dt}</div>
                    </td>
                    """)
        else:
            sample_bytes = database.generate_procedural_xray_bytes()
            if sample_bytes:
                tmp_p = os.path.join(temp_dir, f"sample_xray_{self.current_patient_id}.png")
                with open(tmp_p, "wb") as f:
                    f.write(sample_bytes)
                temp_xray_files.append(tmp_p)
                xray_cards_html.append(f"""
                <td style="text-align:center; padding:10px; width:240px; vertical-align:top; border:1px solid #94a3b8;">
                    <img src="{tmp_p}" width="220" height="165" style="border:1px solid #475569; margin-bottom:6px; display:block; margin-left:auto; margin-right:auto;">
                    <div style="font-weight:bold; font-size:13pt; color:#0f172a;">IOPA - X-Ray (Digital)</div>
                    <div style="font-size:12pt; color:#334155;">Teeth: 26, 27, 14, 15</div>
                    <div style="font-size:11pt; color:#64748b;">Date: 22/06/2026</div>
                </td>
                """)

        xray_grid_html = ""
        if xray_cards_html:
            xray_grid_html = '<div class="sub-hdr" style="margin-top:12px;">Radiographs & X-Rays on File</div><table class="cs-tbl" style="margin-bottom:14px;"><tr>'
            for i, card in enumerate(xray_cards_html):
                if i > 0 and i % 3 == 0:
                    xray_grid_html += "</tr><tr>"
                xray_grid_html += card
            xray_grid_html += "</tr></table>"

        # Referrals
        referrals = p_details.get('referrals', [])
        ref_rows_html = ""
        if referrals:
            for ref in referrals:
                dt = str(ref.get('created_at', ''))[:10]
                prio = ref.get('priority', 1)
                from_d = ref.get('from_dept', 'OPD')
                to_d = ref.get('referred_to_dept', 'OMR')
                reason = ref.get('referral_reason', '')
                status = ref.get('referral_status', 'Visited')
                visited = ref.get('visited_on', dt)
                status_color = "#22c55e" if status.lower() == 'visited' else "#f59e0b"
                ref_rows_html += f"<tr><td>{dt}</td><td>{prio}</td><td>{from_d}</td><td>{to_d}</td><td>{reason}</td><td><span style='color:{status_color}; font-weight:bold;'>{status}</span></td><td>{visited}</td></tr>"
        else:
            ref_rows_html = "<tr><td>22/06/2026</td><td>1</td><td>OPD</td><td>OMR</td><td>Referral for OMR evaluation</td><td><span style='color:#22c55e; font-weight:bold;'>Visited</span></td><td>22/06/2026</td></tr>"

        # Prepare Clinic Details & Logo (Dynamic setup details)
        clinic_info = database.get_clinic_details()
        clinic_name = clinic_info.get('name') or "Dental Care & Specialty Clinic"
        clinic_dept = clinic_info.get('department') or "Department of Dental Surgery & Diagnostics"
        clinic_addr = clinic_info.get('address') or "Main Road, Medical District, City - 520002"
        clinic_phone = clinic_info.get('phone') or "+91 98480 12345"
        clinic_email = clinic_info.get('email') or "info@dentalclinic.com"
        clinic_contact_str = f"Ph: {clinic_phone} | Email: {clinic_email}"

        logo_path = os.path.join(temp_dir, f"clinic_logo_{self.current_patient_id}.png")
        saved_logo = clinic_info.get('logo_path')
        if saved_logo and os.path.exists(saved_logo):
            pix = QPixmap(saved_logo)
            pix.save(logo_path, "PNG")
        elif os.path.exists("app_icon.png"):
            pix = QPixmap("app_icon.png")
            pix.save(logo_path, "PNG")
        else:
            pix = QPixmap(150, 150)
            pix.fill(QColor(0, 0, 0, 0))
            p = QPainter(pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setBrush(QBrush(QColor(15, 118, 110)))
            p.setPen(QPen(QColor(13, 148, 136), 2))
            p.drawEllipse(5, 5, 140, 140)
            p.setPen(QPen(QColor(255, 255, 255), 8))
            p.drawLine(75, 35, 75, 115)
            p.drawLine(35, 75, 115, 75)
            p.end()
            pix.save(logo_path, "PNG")

        html_content = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, 'Segoe UI', sans-serif; color: #000000; margin: 15px; font-size: 13pt; line-height: 1.4; }}
            table.letterhead-tbl {{ width: 100%; border-collapse: collapse; margin-bottom: 8px; }}
            .clinic-name {{ font-size: 20pt; font-weight: bold; color: #0f172a; font-family: 'Segoe UI', Arial, sans-serif; letter-spacing: 0.5px; }}
            .clinic-sub {{ font-size: 14pt; font-weight: bold; color: #0284c7; margin-top: 2px; }}
            .clinic-addr {{ font-size: 11pt; color: #334155; margin-top: 3px; }}
            .clinic-contact {{ font-size: 10pt; color: #64748b; margin-top: 2px; }}
            .report-badge {{ font-size: 15pt; font-weight: bold; color: #0f172a; background-color: #f1f5f9; padding: 4px 8px; border-radius: 4px; display: inline-block; margin-bottom: 4px; text-align: center; }}
            .case-no {{ font-size: 13pt; font-weight: bold; color: #1e293b; }}
            .op-no {{ font-size: 12pt; color: #475569; margin-top: 2px; }}
            .letterhead-divider {{ border-bottom: 3px double #0f172a; margin-top: 8px; margin-bottom: 16px; }}
            
            .sec-hdr {{ font-size: 17pt; font-weight: bold; color: #000000; margin-top: 16px; margin-bottom: 8px; border-bottom: 1px solid #000000; padding-bottom: 2px; }}
            .sub-hdr {{ font-size: 15pt; font-weight: bold; color: #000000; margin-top: 10px; margin-bottom: 6px; }}
            table.cs-tbl {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; }}
            table.cs-tbl th, table.cs-tbl td {{ border: 1px solid #94a3b8; padding: 7px 10px; font-size: 13pt; text-align: left; vertical-align: middle; }}
            table.cs-tbl .lbl {{ font-weight: bold; color: #000000; width: 28%; background-color: #f8fafc; }}
            table.cs-tbl .hdr-cell {{ text-align: center; font-weight: bold; background-color: #f1f5f9; padding: 8px; font-size: 14pt; }}
            table.teeth-tbl {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; }}
            table.teeth-tbl td {{ border: 1px solid #94a3b8; text-align: center; padding: 4px 2px; font-size: 12pt; }}
        </style>
        </head>
        <body>
            <table class="letterhead-tbl">
                <tr>
                    <td style="width: 95px; vertical-align: middle; text-align: left;">
                        <img src="{logo_path}" width="80" height="80" style="display: block;">
                    </td>
                    <td style="vertical-align: middle; text-align: left; padding-left: 10px;">
                        <div class="clinic-name">{clinic_name}</div>
                        <div class="clinic-sub">{clinic_dept}</div>
                        <div class="clinic-addr">{clinic_addr}</div>
                        <div class="clinic-contact">{clinic_contact_str}</div>
                    </td>
                    <td style="width: 220px; vertical-align: middle; text-align: right; border-left: 2px solid #94a3b8; padding-left: 12px;">
                        <div class="report-badge">PATIENT CASE SHEET</div>
                        <div class="case-no">CRN: {case_record_no}</div>
                        <div class="op-no">OP #: {op_no}</div>
                    </td>
                </tr>
            </table>
            <div class="letterhead-divider"></div>

            <div class="sec-hdr">Patient Details</div>
            <table class="cs-tbl">
                <tr>
                    <td class="lbl">OP #</td><td>{op_no}</td>
                    <td class="lbl">Patient Name</td><td>{patient_name}</td>
                </tr>
                <tr>
                    <td class="lbl">Age/Gender</td><td>{age}/{gender}</td>
                    <td class="lbl">Village/Town/City</td><td>{village_city}</td>
                </tr>
                <tr>
                    <td class="lbl">Phone</td><td colspan="3">{phone}</td>
                </tr>
            </table>

            <div class="sec-hdr">History</div>
            <table class="cs-tbl">
                <tr>
                    <td class="lbl">Chief Complaint</td><td>{cc}</td>
                </tr>
                <tr>
                    <td class="lbl">History of Present Illness</td><td>{hpi}</td>
                </tr>
            </table>

            <table class="cs-tbl">
                <tr><th colspan="2" class="hdr-cell">Past Medical History</th></tr>
                <tr><td class="lbl">Diabetes Milletus</td><td>{past_med}</td></tr>
            </table>

            <table class="cs-tbl">
                <tr><th colspan="2" class="hdr-cell">Past Dental History</th></tr>
                <tr><td class="lbl">Past Dental History</td><td>{past_dent}</td></tr>
            </table>

            <table class="cs-tbl">
                <tr><th colspan="3" class="hdr-cell">Parafunctional Habits</th></tr>
                <tr><td class="lbl">Parafunctional Habits</td><td style="width:35%;">{habits}</td><td></td></tr>
            </table>

            <table class="cs-tbl">
                <tr><th colspan="2" class="hdr-cell">Diet</th></tr>
                <tr><td class="lbl">Diet</td><td>{diet}</td></tr>
            </table>

            <table class="cs-tbl">
                <tr><th colspan="3" class="hdr-cell">Sleep</th></tr>
                <tr><td class="lbl">Sleep</td><td style="width:35%;">{sleep}</td><td></td></tr>
            </table>

            <table class="cs-tbl">
                <tr><th colspan="3" class="hdr-cell">Lymph Nodes</th></tr>
                <tr><td class="lbl">Lymph Node</td><td style="width:35%;">{lymph_node}</td><td></td></tr>
                <tr style="font-weight:bold; background-color:#f1f5f9;"><td></td><td>Left</td><td>Right</td></tr>
                <tr><td class="lbl">Size</td><td>{ln_left_size}</td><td>{ln_right_size}</td></tr>
                <tr><td class="lbl">Consistency</td><td>{ln_left_cons}</td><td>{ln_right_cons}</td></tr>
                <tr><td class="lbl">Tenderness</td><td>{ln_left_tend}</td><td>{ln_right_tend}</td></tr>
                <tr><td class="lbl">Fixity</td><td>{ln_left_fix}</td><td>{ln_right_fix}</td></tr>
                <tr><td class="lbl">Others</td><td colspan="2">{ln_others}</td></tr>
            </table>

            <div class="sec-hdr">Intra Oral Examination</div>
            <div class="sub-hdr">Hard Tissue Examination</div>

            <table class="cs-tbl">
                <tr><th colspan="16" class="hdr-cell">Permanent Dentition</th></tr>
            </table>
            <table class="teeth-tbl">
                <tr>{"".join(perm_upper_imgs)}</tr>
                <tr style="font-weight:bold; background-color:#f8fafc;">{"".join([f"<td>{n}</td>" for n in perm_upper_nums])}</tr>
                <tr>{"".join(shorthand_cells)}</tr>
                <tr style="font-weight:bold; background-color:#f8fafc;">{"".join([f"<td>{n}</td>" for n in perm_lower_nums])}</tr>
                <tr>{"".join(perm_lower_imgs)}</tr>
            </table>

            <table class="cs-tbl">
                <tr><th colspan="10" class="hdr-cell">Primary Dentition</th></tr>
            </table>
            <table class="teeth-tbl">
                <tr>{"".join(prim_upper_imgs)}</tr>
                <tr style="font-weight:bold; background-color:#f8fafc;">{"".join([f"<td>{n}</td>" for n in prim_upper_nums])}</tr>
                <tr style="font-weight:bold; background-color:#f8fafc;">{"".join([f"<td>{n}</td>" for n in prim_lower_nums])}</tr>
                <tr>{"".join(prim_lower_imgs)}</tr>
            </table>

            <table class="cs-tbl">
                <tr><th colspan="2" class="hdr-cell">Wasting Diseases</th></tr>
                <tr><td class="lbl">Attrition</td><td>{attrition}</td></tr>
            </table>

            <table class="cs-tbl">
                <tr><th colspan="3" class="hdr-cell">Hypoplasia Teeth</th></tr>
                <tr><td class="lbl">Hypoplasia</td><td style="width:35%;">{hypoplasia}</td><td></td></tr>
            </table>

            <div class="sub-hdr">Soft Tissue Examination</div>
            <table class="cs-tbl">
                <tr><th colspan="3" class="hdr-cell">Mucosa</th></tr>
                <tr><td class="lbl">Labial</td><td style="width:35%;">{labial}</td><td></td></tr>
                <tr><td class="lbl">Buccal</td><td style="width:35%;">{buccal}</td><td></td></tr>
                <tr><td class="lbl">Floor of the Mouth</td><td style="width:35%;">{floor_mouth}</td><td></td></tr>
                <tr><td class="lbl">Vestibular</td><td style="width:35%;">{vestibular}</td><td></td></tr>
                <tr><td class="lbl">Lingual</td><td style="width:35%;">{lingual}</td><td></td></tr>
                <tr><td class="lbl">Palatal</td><td style="width:35%;">{palatal}</td><td></td></tr>
                <tr><td class="lbl">Salivary duct orifice</td><td colspan="2">{salivary}</td></tr>
            </table>

            <div class="sec-hdr">Diagnosis</div>
            <table class="cs-tbl">
                <tr><td class="lbl">Provisional Diagnosis</td><td>{prov_diag}</td></tr>
            </table>

            <div class="sec-hdr">Investigations</div>
            <table class="cs-tbl">
                <tr style="font-weight:bold; background-color:#f1f5f9;">
                    <td>S.No</td><td>Service</td><td>Teeth No</td><td>Qty</td><td>Amount</td><td>Paid</td><td>Invoice #</td><td>Date</td>
                </tr>
                {inv_rows_html}
            </table>
            {xray_grid_html}

            <div class="sec-hdr">Final Diagnosis</div>
            {f'<table class="cs-tbl"><tr><td>{final_diag}</td></tr></table>' if final_diag else ''}

            <div class="sec-hdr">Referral Details</div>
            <table class="cs-tbl">
                <tr style="font-weight:bold; background-color:#f1f5f9;">
                    <td>Date</td><td>Priority</td><td>From Dept</td><td>To Dept</td><td>Reason to refer</td><td>Status</td><td>Visited On</td>
                </tr>
                {ref_rows_html}
            </table>

            <div style="border: 2px solid #64748b; border-radius: 8px; padding: 16px; margin-top: 20px; background-color: #ffffff;">
                <div style="text-align: center; font-size: 20pt; font-weight: bold; margin-bottom: 14px; font-family: 'Segoe UI', Arial, sans-serif;">
                    పేషెంట్ అనుమతి పత్రము
                </div>
                <div style="font-size: 14pt; line-height: 1.8; margin-left: 10px; margin-right: 10px;">
                    <div style="text-align: center; margin-bottom: 12px;">
                        నాకు ట్రీట్మెంట్ చేయు విధానము దానిలో గల లోటు పాట్లు పూర్తిగా &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ఒందే డాక్టరుగారు వివరించారు
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span style="font-size:16pt; font-weight:bold;">[&#10003;]</span>
                        నేను నా ఇష్ట పూర్వకముగానే ట్రీట్మెంట్ చేయించుకొనుచున్నాను, కనుక నాకు ట్రీట్మెంట్ వలన గాని, మందులు పడకపోవడం వలన గాని ఏ విధమైన అవాంఛనీయ సంఘటన జరిగినా దానికి డాక్టరు గారు గాని, సిబ్బందిగాని, ఈ దంత వైద్యశాల కాని బాధ్యులుకారు.
                    </div>
                    <div style="margin-bottom: 18px;">
                        <span style="font-size:16pt; font-weight:bold;">[&#10003;]</span>
                        నా కూతురు / కొడుకు మైనర్ అయినందు వలన వారికి సంబంధించిన వ్యక్తీగా ట్రీట్మెంట్ చేయించుటకు అంగీకరించుచున్నాను.
                    </div>
                    <div style="text-align: right; margin-top: 25px; font-size: 15pt; font-weight: bold;">
                        సంతకము / వేలుముద్ర _________________________
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        doc = QTextDocument()
        doc.setHtml(html_content)
        
        # Print using QPrinter
        doc.print(printer)
        
        # Cleanup temp tooth, logo and xray images
        for fpath in [img_up_molar, img_up_ant, img_dn_molar, img_dn_ant, logo_path] + temp_xray_files:
            try:
                os.remove(fpath)
            except Exception:
                pass

    def init_settings_view(self):
        self.settings_widget = QWidget()
        layout = QVBoxLayout(self.settings_widget)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Clinic Settings")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        from PyQt6.QtWidgets import QScrollArea, QFormLayout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)

        # 1. Profile Settings Group
        profile_group = QGroupBox("Clinic Profile Settings")
        profile_layout = QFormLayout(profile_group)
        profile_layout.setContentsMargins(15, 15, 15, 15)
        profile_layout.setVerticalSpacing(12)

        profile = database.get_clinic_profile('admin') or {'name': 'Clinic', 'username': 'admin'}

        self.settings_clinic_name = QLineEdit(profile.get('name', ''))
        profile_layout.addRow("Clinic Display Name:", self.settings_clinic_name)

        # Custom Logo
        self.settings_logo_preview = QLabel()
        self.settings_logo_preview.setFixedSize(190, 60)
        self.settings_logo_preview.setObjectName("SettingsLogoPreview")
        self.refresh_settings_logo_preview()
        profile_layout.addRow("Clinic Logo Preview:", self.settings_logo_preview)

        btn_upload_logo = QPushButton("Upload Clinic Logo")
        btn_upload_logo.setObjectName("PrimaryBtn")
        btn_upload_logo.clicked.connect(self.upload_clinic_logo)
        profile_layout.addRow("", btn_upload_logo)

        btn_save_profile = QPushButton("Save Clinic Name")
        btn_save_profile.setObjectName("PrimaryBtn")
        btn_save_profile.clicked.connect(self.save_clinic_profile)
        profile_layout.addRow("", btn_save_profile)

        scroll_layout.addWidget(profile_group)

        # 1.5 Theme Settings Group
        theme_group = QGroupBox("Application Theme Settings")
        theme_layout = QFormLayout(theme_group)
        theme_layout.setContentsMargins(15, 15, 15, 15)
        theme_layout.setVerticalSpacing(12)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Custom Dark", "Custom Light"])
        
        current_theme = load_theme_setting()
        if current_theme == "light":
            self.theme_combo.setCurrentText("Custom Light")
        else:
            self.theme_combo.setCurrentText("Custom Dark")
            
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addRow("Active Theme:", self.theme_combo)

        scroll_layout.addWidget(theme_group)

        # 2. Manage Doctors Group
        doc_group = QGroupBox("Manage Doctor Profiles")
        doc_layout = QVBoxLayout(doc_group)
        doc_layout.setContentsMargins(15, 15, 15, 15)
        doc_layout.setSpacing(12)

        btn_add_doctor_wizard = QPushButton("➕ Add Doctor Account (Step 2 Wizard with Security Key)")
        btn_add_doctor_wizard.setObjectName("PrimaryBtn")
        btn_add_doctor_wizard.clicked.connect(self.open_add_doctor_dialog_with_admin_auth)
        doc_layout.addWidget(btn_add_doctor_wizard)

        lbl_quick_reg = QLabel("<b>Quick Doctor Registration:</b>")
        lbl_quick_reg.setStyleSheet("color: #94A3B8; margin-top: 8px;")
        doc_layout.addWidget(lbl_quick_reg)

        form_doc = QFormLayout()
        self.settings_doc_name = QLineEdit()
        self.settings_doc_name.setPlaceholderText("Full Name (e.g. Dr. Jane Doe)")
        form_doc.addRow("Doctor Name:", self.settings_doc_name)

        self.settings_doc_user = QLineEdit()
        self.settings_doc_user.setPlaceholderText("Login Username")
        form_doc.addRow("Username:", self.settings_doc_user)

        self.settings_doc_pwd = QLineEdit()
        self.settings_doc_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        form_doc.addRow("Password:", self.settings_doc_pwd)
        self.settings_doc_disc = QLineEdit("0.0")
        form_doc.addRow("Discount Allowed (%):", self.settings_doc_disc)

        doc_layout.addLayout(form_doc)

        btn_create_doc = QPushButton("Quick Register Doctor")
        btn_create_doc.clicked.connect(self.register_new_doctor_profile)
        doc_layout.addWidget(btn_create_doc)

        scroll_layout.addWidget(doc_group)

        # 3. Database Group
        db_group = QGroupBox("Database Administration")
        db_layout = QVBoxLayout(db_group)
        db_layout.setContentsMargins(15, 15, 15, 15)
        db_layout.setSpacing(10)

        import os
        db_path = os.path.abspath(database.DB_NAME)
        path_lbl = QLabel(f"Database File: {db_path}")
        path_lbl.setStyleSheet("color: #94A3B8; font-style: italic;")
        db_layout.addWidget(path_lbl)

        btn_backup = QPushButton("Backup Database (Export .db)")
        btn_backup.clicked.connect(self.backup_database_action)
        db_layout.addWidget(btn_backup)

        btn_optimize = QPushButton("Optimize & Vacuum Database")
        btn_optimize.clicked.connect(self.optimize_database_action)
        db_layout.addWidget(btn_optimize)

        scroll_layout.addWidget(db_group)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def save_clinic_profile(self):
        new_name = self.settings_clinic_name.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Invalid Input", "Display Name cannot be empty.")
            return
        try:
            database.update_clinic_profile('admin', new_name, 'admin')
            QMessageBox.information(self, "Success", "Clinic Display Name updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not update profile: {e}")

    def upload_clinic_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Clinic Logo Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            try:
                dest_dir = os.path.dirname(os.path.abspath(__file__))
                dest_path = os.path.join(dest_dir, "clinic_logo_user.png")
                shutil.copy(file_path, dest_path)
                database.save_clinic_logo_path(dest_path)
                self.refresh_settings_logo_preview()
                self.update_clinic_logo()
                QMessageBox.information(self, "Logo Saved", "Clinic Logo updated successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Upload Error", f"Failed to upload clinic logo:\n{e}")

    def refresh_settings_logo_preview(self):
        logo_path = database.get_clinic_logo_path()
        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(190, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.settings_logo_preview.setPixmap(scaled_pixmap)
            self.settings_logo_preview.setText("")
        else:
            self.settings_logo_preview.setPixmap(QPixmap())
            self.settings_logo_preview.setText("No Logo Uploaded")
            self.settings_logo_preview.setStyleSheet("qproperty-alignment: AlignCenter;")

    def register_new_doctor_profile(self):
        name = self.settings_doc_name.text().strip()
        user = self.settings_doc_user.text().strip()
        pwd = self.settings_doc_pwd.text()
        try:
            disc = float(self.settings_doc_disc.text() or 0.0)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Discount must be a number.")
            return

        if not name or not user or not pwd:
            QMessageBox.warning(self, "Invalid Input", "All fields are required.")
            return

        if database.create_doctor(name, user, pwd, disc):
            QMessageBox.information(self, "Success", f"Doctor '{name}' registered successfully.")
            self.settings_doc_name.clear()
            self.settings_doc_user.clear()
            self.settings_doc_pwd.clear()
            self.settings_doc_disc.setText("0.0")
            self.refresh_doctor_dropdowns()
        else:
            QMessageBox.warning(self, "Duplicate", "Username already exists. Choose a different username.")

    def open_add_doctor_dialog_with_admin_auth(self):
        auth_dlg = AdminAuthDialog(self)
        if auth_dlg.exec() == QDialog.DialogCode.Accepted:
            setup_dlg = FirstLaunchSetupDialog(start_step=2, parent=self)
            if setup_dlg.exec() == QDialog.DialogCode.Accepted:
                self.refresh_doctor_dropdowns()
                QMessageBox.information(self, "Success", "New Doctor account created successfully with security recovery keys.")

    def backup_database_action(self):
        from PyQt6.QtWidgets import QFileDialog
        import shutil
        file_path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "dental_clinic_backup.db", "SQLite Database Files (*.db)")
        if file_path:
            try:
                shutil.copy(database.DB_NAME, file_path)
                QMessageBox.information(self, "Backup Success", f"Database backed up to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Backup Error", f"Failed to backup database:\n{e}")

    def optimize_database_action(self):
        try:
            database.vacuum_database()
            QMessageBox.information(self, "Database Optimized", "The database has been optimized and defragmented (VACUUM completed).")
        except Exception as e:
            QMessageBox.critical(self, "Defrag Error", f"Optimization failed:\n{e}")

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        stylesheet = get_theme_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
        self.propagate_theme_to_widgets()

    def propagate_theme_to_widgets(self):
        from widgets.dental_chart import DentalChartWidget
        from widgets.xray_viewer import XrayViewerWidget
        
        charts = self.findChildren(DentalChartWidget)
        for chart in charts:
            chart.update_theme(self.current_theme)
            
        xrays = self.findChildren(XrayViewerWidget)
        for xray in xrays:
            xray.refresh_list()

    def save_theme_setting(self, theme_name):
        import json
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_config.json")
        try:
            with open(config_path, "w") as f:
                json.dump({"theme": theme_name}, f)
        except Exception:
            pass

    def on_theme_changed(self, text):
        theme_name = "classic"
        if "Light" in text:
            theme_name = "light"
        
        self.save_theme_setting(theme_name)
        self.apply_theme(theme_name)

