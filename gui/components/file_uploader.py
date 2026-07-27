# File Uploader Widget Component
from datetime import datetime
import os
import sys

from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import database


class FileUploaderWidget(QWidget):
    """Reusable tab widget for browsing, uploading, listing, viewing, and deleting patient attachments."""

    def __init__(self, file_category, parent_window, parent=None):
        super().__init__(parent)
        self.file_category = file_category
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # 1. Upload Box
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

        # 2. File List Table
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
