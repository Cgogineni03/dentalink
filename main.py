# DentaLink Native Patient Management Desktop Application (main.py)
import sys
import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QLineEdit, QComboBox, QDateEdit, QTextEdit, 
                             QTabWidget, QFormLayout, QMessageBox, QGroupBox, QDialog, QFileDialog, QGridLayout, QCheckBox)
from PyQt6.QtCore import Qt, QDate, pyqtSlot, QRect, pyqtSignal, QPointF
from PyQt6.QtGui import QFont, QIcon, QPainter, QPixmap, QColor, QPen
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

import database
from widgets.dental_chart import DentalChartWidget
from widgets.xray_viewer import XrayViewerWidget

def crash_exception_hook(exctype, value, tb):
    import traceback
    with open("crash.log", "w") as f:
        traceback.print_exception(exctype, value, tb, file=f)
    sys.__excepthook__(exctype, value, tb)
sys.excepthook = crash_exception_hook

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

# Premium Dark CSS/QSS Stylesheet
DARK_STYLESHEET = """
QMainWindow {
    background-color: #101010;
}
QDialog {
    background-color: #161616;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #E2E8F0;
    font-size: 13px;
}
QFrame#Sidebar {
    background-color: #161616;
    border-right: 1px solid #2D2D30;
}
QLabel#SidebarTitle {
    color: #38BDF8;
    font-size: 18px;
    font-weight: bold;
    padding: 8px 12px;
    border: 1px solid #2D2D30;
    border-radius: 6px;
    background-color: #1a2032;
    margin-bottom: 10px;
}
QLabel#SidebarTitle:hover {
    color: #60A5FA;
    background-color: #26314f;
    border: 1px solid #38BDF8;
}
QPushButton#SidebarBtn {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    padding: 12px 15px;
    text-align: left;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#SidebarBtn:hover {
    background-color: #1a2032;
    color: #E2E8F0;
}
QPushButton#SidebarBtn:checked {
    background-color: #0371bb;
    color: white;
}
QStackedWidget {
    background-color: #101010;
}
QTableWidget {
    background-color: #161616;
    border: 1px solid #2D2D30;
    gridline-color: #2D2D30;
    border-radius: 10px;
    color: #E2E8F0;
}
QTableWidget::item:selected {
    background-color: #1a2032;
    color: #0371bb;
}
QHeaderView::section {
    background-color: #1a2032;
    color: #94A3B8;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #2D2D30;
    font-weight: bold;
}
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: #1a2032;
    border: 1px solid #2D2D30;
    border-radius: 6px;
    padding: 6px 10px;
    color: white;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1.5px solid #0371bb;
}
QPushButton {
    background-color: #1a2032;
    border: 1px solid #2D2D30;
    border-radius: 8px;
    padding: 8px 16px;
    color: white;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #26314f;
}
QPushButton#PrimaryBtn {
    background-color: #0371bb;
    border: none;
    color: white;
}
QPushButton#PrimaryBtn:hover {
    background-color: #025c99;
}
QPushButton#SuccessBtn {
    background-color: #10B981;
    border: none;
    color: white;
}
QPushButton#SuccessBtn:hover {
    background-color: #059669;
}
QTabWidget::pane {
    border: 1px solid #2D2D30;
    background-color: #161616;
    border-radius: 10px;
}
QTabBar::tab {
    background-color: #1a2032;
    color: #94A3B8;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: #161616;
    color: white;
}
QGroupBox {
    border: 1px solid #2D2D30;
    border-radius: 10px;
    margin-top: 15px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #0371bb;
}
QFrame#PatientBanner {
    background-color: #161616;
    border: 1px solid #2D2D30;
    border-radius: 10px;
}
QLabel#PatientBannerTitle {
    color: #0371bb;
}
QScrollArea, QScrollArea > QWidget > QWidget {
    background-color: transparent;
    border: none;
}
QPushButton#XrayListItem {
    background-color: #1a2032;
    color: #E2E8F0;
    border: 1px solid #2D2D30;
    border-radius: 8px;
    padding: 8px;
    text-align: left;
    font-size: 11px;
}
QPushButton#XrayListItem:hover {
    background-color: #26314f;
}
QLabel#XrayDisplayLabel {
    background-color: #161616;
    border: 2px dashed #2D2D30;
    border-radius: 10px;
    color: #64748B;
    font-size: 13px;
}
QLabel#SettingsLogoPreview {
    border: 1px dashed #2D2D30;
    border-radius: 8px;
    background-color: #161616;
}
QScrollBar:vertical {
    background-color: #101010;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #2D2D30;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background-color: #0371bb;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
QScrollBar:horizontal {
    background-color: #101010;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background-color: #2D2D30;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #0371bb;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}
"""

LIGHT_STYLESHEET = """
QMainWindow {
    background-color: #EEEEEE;
}
QDialog {
    background-color: #FFFFFF;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #0F172A;
    font-size: 13px;
}
QFrame#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #CBD5E1;
}
QFrame#Sidebar QWidget {
    color: #475569;
}
QFrame#Sidebar QLabel#SidebarTitle {
    color: #0371bb;
    font-size: 18px;
    font-weight: bold;
    padding: 8px 12px;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    background-color: #F1F5F9;
    margin-bottom: 10px;
}
QFrame#Sidebar QLabel#SidebarTitle:hover {
    color: #025c99;
    background-color: #E2E8F0;
    border: 1px solid #0371bb;
}
QFrame#Sidebar QPushButton#SidebarBtn {
    background-color: transparent;
    color: #475569;
    border: none;
    border-radius: 8px;
    padding: 12px 15px;
    text-align: left;
    font-size: 13px;
    font-weight: bold;
}
QFrame#Sidebar QPushButton#SidebarBtn:hover {
    background-color: #EEEEEE;
    color: #0F172A;
}
QFrame#Sidebar QPushButton#SidebarBtn:checked {
    background-color: #0371bb;
    color: white;
}
QStackedWidget {
    background-color: #EEEEEE;
}
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    gridline-color: #D1D5DB;
    border-radius: 10px;
    color: #0F172A;
}
QTableWidget::item:selected {
    background-color: #E5E7EB;
    color: #0371bb;
}
QHeaderView::section {
    background-color: #F3F4F6;
    color: #475569;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #D1D5DB;
    font-weight: bold;
}
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #0F172A;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1.5px solid #0371bb;
}
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 16px;
    color: #0F172A;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #F3F4F6;
}
QPushButton#PrimaryBtn {
    background-color: #0371bb;
    border: none;
    color: white;
}
QPushButton#PrimaryBtn:hover {
    background-color: #025c99;
}
QPushButton#SuccessBtn {
    background-color: #10B981;
    border: none;
    color: white;
}
QPushButton#SuccessBtn:hover {
    background-color: #059669;
}
QTabWidget::pane {
    border: 1px solid #D1D5DB;
    background-color: #FFFFFF;
    border-radius: 10px;
}
QTabBar::tab {
    background-color: #E5E7EB;
    color: #475569;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: #FFFFFF;
    color: #0F172A;
}
QGroupBox {
    border: 1px solid #D1D5DB;
    border-radius: 10px;
    margin-top: 15px;
    font-weight: bold;
    color: #0F172A;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #0371bb;
}
QFrame#PatientBanner {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 10px;
}
QLabel#PatientBannerTitle {
    color: #0371bb;
}
QScrollArea, QScrollArea > QWidget > QWidget {
    background-color: transparent;
    border: none;
}
QPushButton#XrayListItem {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px;
    text-align: left;
    font-size: 11px;
}
QPushButton#XrayListItem:hover {
    background-color: #F3F4F6;
}
QLabel#XrayDisplayLabel {
    background-color: #FFFFFF;
    border: 2px dashed #CBD5E1;
    border-radius: 10px;
    color: #475569;
    font-size: 13px;
}
QLabel#SettingsLogoPreview {
    border: 1px dashed #CBD5E1;
    border-radius: 8px;
    background-color: #FFFFFF;
}
QScrollBar:vertical {
    background-color: #EEEEEE;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #CBD5E1;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background-color: #0371bb;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
QScrollBar:horizontal {
    background-color: #EEEEEE;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background-color: #CBD5E1;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #0371bb;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}
"""

def load_theme_setting():
    import json
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return data.get("theme", "classic")
        except Exception:
            pass
    return "classic"

def get_theme_stylesheet(theme_name):
    if theme_name == "light":
        return LIGHT_STYLESHEET
    else:
        return DARK_STYLESHEET


class ViewTreatmentDoneDialog(QDialog):
    def __init__(self, treatment_done_data, linked_bill=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("View Clinical Session Details")
        self.setMinimumSize(450, 420)
        theme_name = load_theme_setting()
        self.setStyleSheet(get_theme_stylesheet(theme_name))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Clinical Session Details")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #0371bb;")
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        
        lbl_date = QLabel(treatment_done_data.get('date_done', 'N/A'))
        form_layout.addRow("Date:", lbl_date)
        
        if linked_bill:
            lbl_bill = QLabel(f"{linked_bill['procedure_name']} (Teeth: {linked_bill['teeth_no']}, Rs.{linked_bill['total']:.2f})")
            lbl_paid = QLabel(linked_bill['billing_status'])
            if linked_bill['billing_status'] == 'Paid':
                lbl_paid.setStyleSheet("color: #10B981; font-weight: bold;")
            else:
                lbl_paid.setStyleSheet("color: #EF4444; font-weight: bold;")
        else:
            lbl_bill = QLabel("Unbilled Procedure")
            lbl_paid = QLabel("N/A")
            
        form_layout.addRow("Linked Bill Procedure:", lbl_bill)
        form_layout.addRow("Bill Payment Status:", lbl_paid)
        
        lbl_status = QLabel(treatment_done_data.get('treatment_status', 'Done'))
        form_layout.addRow("Treatment Status:", lbl_status)
        
        lbl_student = QLabel(treatment_done_data.get('student_name') or "None")
        form_layout.addRow("Clinician Allotted:", lbl_student)
        
        lbl_doctor = QLabel(treatment_done_data.get('doctor_name', 'Dr. Admin'))
        form_layout.addRow("Authorized Doctor:", lbl_doctor)
        
        layout.addLayout(form_layout)
        
        details_label = QLabel("Session Clinical Details:")
        details_label.setStyleSheet("font-weight: bold; color: #0371bb;")
        layout.addWidget(details_label)
        
        txt_details = QTextEdit()
        txt_details.setPlainText(treatment_done_data.get('details', ''))
        txt_details.setReadOnly(True)
        txt_details.setMaximumHeight(80)
        layout.addWidget(txt_details)
        
        notes_label = QLabel("Doctor's Notes / Remarks:")
        notes_label.setStyleSheet("font-weight: bold; color: #0371bb;")
        layout.addWidget(notes_label)
        
        txt_notes = QTextEdit()
        txt_notes.setPlainText(treatment_done_data.get('doctor_notes', ''))
        txt_notes.setReadOnly(True)
        txt_notes.setMaximumHeight(60)
        layout.addWidget(txt_notes)
        
        btn_close = QPushButton("Close")
        btn_close.setObjectName("PrimaryBtn")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class FileUploaderWidget(QWidget):
    def __init__(self, file_category, parent_window, parent=None):
        super().__init__(parent)
        self.file_category = file_category
        self.parent_window = parent_window  # reference to DentaLinkMainWindow to get current_patient_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # 1. Upload box
        upload_box = QGroupBox(f"Upload {self.file_category}s")
        grid = QHBoxLayout(upload_box)
        grid.setSpacing(8)
        
        self.txt_file_path = QLineEdit()
        self.txt_file_path.setReadOnly(True)
        self.txt_file_path.setPlaceholderText("Select a file to upload...")
        
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self.browse_file)
        
        btn_upload = QPushButton("Upload")
        btn_upload.setObjectName("SuccessBtn")
        btn_upload.clicked.connect(self.upload_file)
        
        grid.addWidget(self.txt_file_path, 1)
        grid.addWidget(btn_browse)
        grid.addWidget(btn_upload)
        layout.addWidget(upload_box)
        
        # 2. File list table
        list_box = QGroupBox(f"Uploaded {self.file_category}s History")
        list_lay = QVBoxLayout(list_box)
        
        self.table_files = QTableWidget()
        self.table_files.setColumnCount(4)
        self.table_files.setHorizontalHeaderLabels(["Upload Date", "File Name", "File Type", "Actions"])
        self.table_files.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_files.verticalHeader().setVisible(False)
        list_lay.addWidget(self.table_files)
        
        layout.addWidget(list_box)

    def browse_file(self):
        if self.file_category == "Pathology Report":
            filter_str = "All Files (*.pdf *.png *.jpg *.jpeg *.bmp *.tiff);;PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        else:
            filter_str = "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select {self.file_category}", "", filter_str
        )
        if file_path:
            self.txt_file_path.setText(file_path)

    def upload_file(self):
        patient_id = self.parent_window.current_patient_id
        if not patient_id:
            QMessageBox.warning(self, "Warning", "Please open a patient file first.")
            return
            
        file_path = self.txt_file_path.text().strip()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Warning", "Please select a valid file first.")
            return
            
        try:
            filename = os.path.basename(file_path)
            file_ext = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            from datetime import datetime
            now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            
            database.add_patient_file(patient_id, self.file_category, filename, file_data, now_str, file_ext)
            
            self.txt_file_path.clear()
            self.refresh_list()
            QMessageBox.information(self, "Success", f"{self.file_category} uploaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read/upload file: {str(e)}")

    def refresh_list(self):
        self.table_files.setRowCount(0)
        patient_id = self.parent_window.current_patient_id
        if not patient_id:
            return
            
        files = database.get_patient_files(patient_id, self.file_category)
        self.table_files.setRowCount(len(files))
        for idx, f in enumerate(files):
            self.table_files.setItem(idx, 0, QTableWidgetItem(f['upload_date']))
            self.table_files.setItem(idx, 1, QTableWidgetItem(f['file_name']))
            self.table_files.setItem(idx, 2, QTableWidgetItem(f['file_type'].upper()))
            
            # Action layout with View and Delete buttons
            act_widget = QWidget()
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(4)
            
            btn_view = QPushButton("👁 View")
            btn_view.setStyleSheet("background-color: #0284C7; color: white; padding: 2px 5px;")
            btn_view.clicked.connect(lambda checked, fid=f['id']: self.view_file(fid))
            act_layout.addWidget(btn_view)
            
            btn_del = QPushButton("Delete")
            btn_del.setStyleSheet("background-color: #EF4444; color: white; padding: 2px 5px;")
            btn_del.clicked.connect(lambda checked, fid=f['id']: self.delete_file(fid))
            act_layout.addWidget(btn_del)
            
            self.table_files.setCellWidget(idx, 3, act_widget)

    def view_file(self, file_id):
        file_record = database.get_patient_file(file_id)
        if not file_record:
            QMessageBox.critical(self, "Error", "File record not found.")
            return
            
        file_data = file_record['file_data']
        file_name = file_record['file_name']
        
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file_name)
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(file_data)
                
            if sys.platform == 'win32':
                os.startfile(temp_path)
            else:
                import subprocess
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, temp_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def delete_file(self, file_id):
        reply = QMessageBox.question(
            self, "Confirm Delete", f"Are you sure you want to permanently delete this {self.file_category.lower()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_patient_file(file_id)
            self.refresh_list()


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
        self.banner_title = QLabel("Oral Medicine and Radiology Case Sheet Update")
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
        banner_vlayout.addLayout(actions_row)
        
        layout.addWidget(self.patient_banner)

        # Tabs Container
        self.case_tabs = QTabWidget()
        layout.addWidget(self.case_tabs)

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
        ref = p.get('referrals', {})
        
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

        QMessageBox.information(self, "Success", "Entire Clinical Case Sheet saved successfully.")

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
        
        # Save teeth chart QPixmap to a temporary file
        temp_dir = tempfile.gettempdir()
        temp_chart_path = os.path.join(temp_dir, f"denta_chart_{self.current_patient_id}.png")
        
        chart_pixmap = self.dental_chart.chart_view.grab()
        chart_pixmap.save(temp_chart_path, "PNG")
        
        # Patient age
        age = self.calculate_age(p_details['dob'])
        
        # Clinic Profile Name
        clinic_profile = database.get_clinic_profile('admin') or {'name': 'DentaLink Dental Clinic'}
        clinic_name = clinic_profile.get('name', 'DentaLink Dental Clinic')
        
        # Date of print
        date_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        
        # Doctor name
        doc_name = p_details.get('assigned_doctor_name') or "Unassigned"
        
        # Allergies & Medical alerts box
        allergies = p_details.get('allergies', 'None')
        meds = p_details.get('medical_conditions', 'None')
        alert_html = ""
        if allergies != "None" or meds != "None":
            alert_html = f"""
            <div class="alert-box">
                CRITICAL MEDICAL ALERTS:<br>
                • Allergies: {allergies}<br>
                • Medical Conditions: {meds}
            </div>
            """
            
        # Narratives
        history = p_details.get('case_history', {})
        cc = history.get('chief_complaint') or "No entry"
        hpi = history.get('hpi') or "No entry"
        findings = history.get('clinical_findings') or "No entry"
        
        # Convert narrative newlines to html line breaks
        cc = cc.replace("\n", "<br>")
        hpi = hpi.replace("\n", "<br>")
        findings = findings.replace("\n", "<br>")

        html_content = f"""
        <html>
        <head>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #0F172A; margin: 20px; }}
            .header {{ border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 20px; }}
            .header h1 {{ font-size: 22px; margin: 0; color: #0EA5E9; text-transform: uppercase; font-weight: bold; }}
            .header p {{ font-size: 11px; margin: 4px 0 0 0; color: #64748B; }}
            .section-title {{ font-size: 12px; font-weight: bold; margin-top: 25px; margin-bottom: 10px; color: #0F172A; border-bottom: 1px solid #CBD5E1; padding-bottom: 4px; letter-spacing: 0.5px; }}
            .grid {{ width: 100%; margin-bottom: 15px; border: none; }}
            .grid td {{ padding: 4px 10px 4px 0; font-size: 11px; vertical-align: top; }}
            .alert-box {{ background-color: #FEF2F2; border: 1px solid #FCA5A5; color: #B91C1C; padding: 10px; border-radius: 4px; font-size: 11px; margin: 15px 0; line-height: 1.4; }}
            .chart-container {{ text-align: center; margin: 15px 0; padding: 10px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; }}
            .chart-img {{ width: 620px; height: auto; }}
            .history-table {{ width: 100%; border: none; margin-bottom: 20px; }}
            .history-table td {{ padding: 6px 10px 6px 0; font-size: 11px; vertical-align: top; }}
            .history-label {{ font-weight: bold; width: 150px; color: #334155; }}
            .signature-container {{ margin-top: 40px; text-align: right; }}
            .signature-box {{ display: inline-block; text-align: left; width: 220px; border-top: 1px solid #94A3B8; padding-top: 6px; }}
            .signature-title {{ font-size: 10px; color: #64748B; margin-top: 2px; }}
        </style>
        </head>
        <body>
            <div class="header">
                <h1>{clinic_name}</h1>
                <p>Clinical Patient Chart Report & Odontogram | Generated: {date_str}</p>
            </div>
            
            <div class="section-title">PATIENT DEMOGRAPHICS</div>
            <table class="grid">
                <tr>
                    <td width="50%"><strong>Patient Name:</strong> {p_details['name']}</td>
                    <td width="50%"><strong>Patient ID:</strong> P{p_details['id']:04d}</td>
                </tr>
                <tr>
                    <td><strong>Date of Birth:</strong> {p_details['dob']} (Age: {age} yrs)</td>
                    <td><strong>Gender:</strong> {p_details['gender']}</td>
                </tr>
                <tr>
                    <td><strong>Phone:</strong> {p_details['phone']}</td>
                    <td><strong>Email:</strong> {p_details['email'] or 'N/A'}</td>
                </tr>
                <tr>
                    <td><strong>Address:</strong> {p_details['address']}</td>
                    <td><strong>Assigned Clinician:</strong> {doc_name}</td>
                </tr>
            </table>
            
            {alert_html}
            
            <div class="section-title">VISUAL DENTAL CHART / ODONTOGRAM</div>
            <div class="chart-container">
                <img class="chart-img" src="{temp_chart_path}">
            </div>
            
            <div class="section-title">CLINICAL FINDINGS & CASE HISTORY</div>
            <table class="history-table">
                <tr>
                    <td class="history-label">Chief Complaint:</td>
                    <td>{cc}</td>
                </tr>
                <tr>
                    <td class="history-label">History of Present Illness:</td>
                    <td>{hpi}</td>
                </tr>
                <tr>
                    <td class="history-label">Clinical Findings:</td>
                    <td>{findings}</td>
                </tr>
            </table>
            
            <div class="signature-container">
                <div class="signature-box">
                    <strong>Dr. {doc_name}</strong>
                    <div class="signature-title">Authorized Clinical Signature</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        from PyQt6.QtGui import QTextDocument
        doc = QTextDocument()
        doc.setHtml(html_content)
        
        # Print using QPrinter
        doc.print(printer)
        
        # Cleanup temp file
        try:
            os.remove(temp_chart_path)
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

        btn_create_doc = QPushButton("Register New Doctor")
        btn_create_doc.setObjectName("PrimaryBtn")
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

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Doctor Login")
        self.setFixedSize(350, 220)
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
        
        self.username_input = QLineEdit("dr_admin")
        self.username_input.setPlaceholderText("Doctor Username")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        self.btn_login = QPushButton("Login")
        self.btn_login.setObjectName("PrimaryBtn")
        self.btn_login.clicked.connect(self.attempt_login)
        layout.addWidget(self.btn_login)
        
        # Focus password box by default
        self.password_input.setFocus()
        
    def attempt_login(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text()
        
        session = database.verify_password(user, pwd)
        if session:
            self.logged_in_session = session
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()

def main():
    try:
        app = QApplication(sys.argv)
        
        # Initialize DB first to ensure clinics and doctors exist before login
        database.initialize_database()
        
        login = LoginWindow()
        if login.exec() == QDialog.DialogCode.Accepted:
            window = DentaLinkMainWindow(login.logged_in_session)
            window.show()
            sys.exit(app.exec())
        else:
            sys.exit(0)
    except Exception as e:
        import traceback
        with open("crash.log", "w") as f:
            traceback.print_exc(file=f)
        raise e

if __name__ == "__main__":
    main()
