# DentaLink Diagnostic X-ray Viewer Widget (widgets/xray_viewer.py)
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QCheckBox, QPushButton, QFileDialog, 
                             QMessageBox, QSplitter, QComboBox)
from PyQt6.QtGui import QImage, QPixmap, QColor, QFont, qRgb
from PyQt6.QtCore import Qt, pyqtSignal

import database

class XrayViewerWidget(QWidget):
    xray_list_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_id = None
        self.current_xray_id = None
        self.original_image = None
        self.filtered_image = None
        
        self.brightness = 0  # -100 to 100
        self.contrast = 0    # -100 to 100
        self.inverted = False
        
        self.init_ui()

    def init_ui(self):
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Main Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)

        # Left Panel: X-ray List & Upload
        self.list_panel = QWidget()
        list_layout = QVBoxLayout(self.list_panel)
        list_layout.setContentsMargins(0, 0, 5, 0)

        list_title = QLabel("Clinical Images")
        list_title.setFont(QFont("Ubuntu", 11, QFont.Weight.Bold))
        list_layout.addWidget(list_title)

        # Dynamic list container for X-ray items
        self.list_container = QWidget()
        self.list_scroll_layout = QVBoxLayout(self.list_container)
        self.list_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        list_layout.addWidget(self.list_container, 1)

        # Upload Button
        self.btn_upload = QPushButton("Upload Image")
        self.btn_upload.setObjectName("PrimaryBtn")
        self.btn_upload.clicked.connect(self.upload_xray)
        list_layout.addWidget(self.btn_upload)
        
        self.splitter.addWidget(self.list_panel)

        # Right Panel: Image Display & Controls
        self.display_panel = QWidget()
        display_layout = QVBoxLayout(self.display_panel)
        display_layout.setContentsMargins(5, 0, 0, 0)

        # Image display container
        self.img_label = QLabel("Select an X-ray to view diagnostic details")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setObjectName("XrayDisplayLabel")
        self.img_label.setMinimumSize(400, 300)
        display_layout.addWidget(self.img_label, 1)

        # Controls Panel (Sliders)
        self.controls_widget = QWidget()
        self.controls_widget.setEnabled(False) # Disabled until image is loaded
        controls_layout = QVBoxLayout(self.controls_widget)
        controls_layout.setContentsMargins(0, 5, 0, 0)

        # Slider 1: Brightness
        bright_layout = QHBoxLayout()
        bright_lbl = QLabel("Brightness:")
        bright_lbl.setFixedWidth(80)
        
        self.slider_brightness = QSlider(Qt.Orientation.Horizontal)
        self.slider_brightness.setRange(-100, 100)
        self.slider_brightness.setValue(0)
        self.slider_brightness.valueChanged.connect(self.on_brightness_changed)
        
        self.val_brightness = QLabel("0")
        self.val_brightness.setFixedWidth(30)
        
        bright_layout.addWidget(bright_lbl)
        bright_layout.addWidget(self.slider_brightness)
        bright_layout.addWidget(self.val_brightness)
        controls_layout.addLayout(bright_layout)

        # Slider 2: Contrast
        contrast_layout = QHBoxLayout()
        contrast_lbl = QLabel("Contrast:")
        contrast_lbl.setFixedWidth(80)
        
        self.slider_contrast = QSlider(Qt.Orientation.Horizontal)
        self.slider_contrast.setRange(-100, 100)
        self.slider_contrast.setValue(0)
        self.slider_contrast.valueChanged.connect(self.on_contrast_changed)
        
        self.val_contrast = QLabel("0")
        self.val_contrast.setFixedWidth(30)
        
        contrast_layout.addWidget(contrast_lbl)
        contrast_layout.addWidget(self.slider_contrast)
        contrast_layout.addWidget(self.val_contrast)
        controls_layout.addLayout(contrast_layout)

        # Preset LUT ComboBox
        preset_layout = QHBoxLayout()
        preset_lbl = QLabel("LUT Preset:")
        preset_lbl.setFixedWidth(80)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["General", "Endodontic", "Periodontal"])
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(preset_lbl)
        preset_layout.addWidget(self.preset_combo)
        controls_layout.addLayout(preset_layout)

        # Bottom row: Invert checkbox and Reset button
        bottom_row = QHBoxLayout()
        self.chk_invert = QCheckBox("Invert Colors (Diagnostic Negative)")
        self.chk_invert.toggled.connect(self.on_invert_toggled)

        self.btn_reset = QPushButton("Reset Filters")
        self.btn_reset.setObjectName("ResetBtn")
        self.btn_reset.clicked.connect(self.reset_filters)

        self.btn_delete = QPushButton("Delete X-ray")
        self.btn_delete.setObjectName("DeleteBtn")
        self.btn_delete.clicked.connect(self.delete_current_xray)

        bottom_row.addWidget(self.chk_invert)
        bottom_row.addStretch()
        bottom_row.addWidget(self.btn_reset)
        bottom_row.addWidget(self.btn_delete)
        controls_layout.addLayout(bottom_row)

        display_layout.addWidget(self.controls_widget)
        self.splitter.addWidget(self.display_panel)

        # Set sizes for splitter: 200px list, 600px display
        self.splitter.setSizes([200, 600])

    def load_patient(self, patient_id):
        self.patient_id = patient_id
        self.clear_display()
        self.refresh_list()

    def refresh_list(self):
        # Clear old items in list layout
        while self.list_scroll_layout.count():
            item = self.list_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.patient_id:
            return

        details = database.get_patient_details(self.patient_id)
        xrays = details.get('xrays', [])

        if not xrays:
            lbl_none = QLabel("No X-rays uploaded yet.")
            lbl_none.setStyleSheet("color: #64748B; font-style: italic;")
            self.list_scroll_layout.addWidget(lbl_none)
            return

        for x in xrays:
            xray_id = x['id']
            img_type = x.get('image_type', 'X-Ray')
            desc = x['description'] or "Diagnostic Image"
            date_str = x['date_taken']

            btn_item = QPushButton(f"{date_str}\n[{img_type}] {desc}")
            btn_item.setObjectName("XrayListItem")
            btn_item.clicked.connect(lambda checked, xid=xray_id, itype=img_type: self.load_xray(xid, itype))
            self.list_scroll_layout.addWidget(btn_item)

    def load_xray(self, xray_id, image_type="X-Ray"):
        self.current_xray_id = xray_id
        self.current_image_type = image_type
        img_bytes = database.get_xray_image_data(xray_id)
        if not img_bytes:
            QMessageBox.critical(self, "Error", "Could not load image data from database.")
            return

        # Load QImage from binary bytes
        img = QImage.fromData(img_bytes)
        if img.isNull():
            QMessageBox.critical(self, "Error", "Invalid image format inside database BLOB.")
            return

        if image_type == "X-Ray":
            # Convert to 8-bit Indexed grayscale for instantaneous LUT filters.
            # First convert to Grayscale8 to get proper perception-weighted luminance,
            # then convert to Indexed8 using a linear grayscale color table.
            gray_table = [qRgb(i, i, i) for i in range(256)]
            gray_img = img.convertToFormat(QImage.Format.Format_Grayscale8)
            self.original_image = gray_img.convertToFormat(QImage.Format.Format_Indexed8, gray_table)
            self.controls_widget.setEnabled(True)
        else:
            # Clinical photographs stay in full color, disable diagnostic filters
            self.original_image = img.convertToFormat(QImage.Format.Format_RGB32)
            self.controls_widget.setEnabled(False)

        self.reset_filters() # Resets slider positions and updates display

    def update_image_display(self):
        if self.original_image is None:
            return

        if getattr(self, 'current_image_type', 'X-Ray') == "X-Ray":
            # Create a deep copy of the image to apply the modified color table
            self.filtered_image = self.original_image.copy()

        # Build custom LUT color table based on Brightness, Contrast, and Inversion
        # contrast factor: -100 to 100, where 0 is neutral.
        # factor ranges from 0.1 to 3.0
        contrast_factor = 1.0
        if self.contrast > 0:
            contrast_factor = 1.0 + (self.contrast / 50.0)
        elif self.contrast < 0:
            contrast_factor = 1.0 + (self.contrast / 110.0) # Down to ~0.1

        preset = getattr(self, 'preset_combo', None)
        preset_text = preset.currentText() if preset else "General"

        new_color_table = []
        for i in range(256):
            # 0. Apply Preset Base Curve (LUT)
            base_val = i
            if preset_text == "Endodontic":
                # Enhance mid-tones and darks (gamma < 1) to see root anatomy better
                base_val = 255.0 * ((i / 255.0) ** 0.65)
            elif preset_text == "Periodontal":
                # Enhance highlights/contrast for bone (gamma > 1) to see crestal bone loss
                base_val = 255.0 * ((i / 255.0) ** 1.35)

            # 1. Apply Contrast centering at 127
            v = contrast_factor * (base_val - 127) + 127
            # 2. Apply Brightness
            v += self.brightness
            # 3. Apply Inversion
            if self.inverted:
                v = 255 - v
            
            # Clamp value
            v_clamped = int(max(0, min(255, v)))
            new_color_table.append(qRgb(v_clamped, v_clamped, v_clamped))

        # Set LUT on image
        if getattr(self, 'current_image_type', 'X-Ray') == "X-Ray":
            self.filtered_image.setColorTable(new_color_table)
            pixmap = QPixmap.fromImage(self.filtered_image)
        else:
            pixmap = QPixmap.fromImage(self.original_image)

        # Scale pixmap for screen display keeping ratio
        scaled_pixmap = pixmap.scaled(
            self.img_label.width() - 10,
            self.img_label.height() - 10,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.img_label.setPixmap(scaled_pixmap)

    def on_brightness_changed(self, val):
        self.brightness = val
        self.val_brightness.setText(str(val))
        self.update_image_display()

    def on_contrast_changed(self, val):
        self.contrast = val
        self.val_contrast.setText(str(val))
        self.update_image_display()

    def on_invert_toggled(self, checked):
        self.inverted = checked
        self.update_image_display()

    def on_preset_changed(self, text):
        self.update_image_display()

    def reset_filters(self):
        # Block signals to avoid redrawing multiple times
        self.slider_brightness.blockSignals(True)
        self.slider_contrast.blockSignals(True)
        self.chk_invert.blockSignals(True)
        self.preset_combo.blockSignals(True)

        self.slider_brightness.setValue(0)
        self.slider_contrast.setValue(0)
        self.chk_invert.setChecked(False)
        self.preset_combo.setCurrentText("General")

        self.brightness = 0
        self.contrast = 0
        self.inverted = False

        self.val_brightness.setText("0")
        self.val_contrast.setText("0")

        self.slider_brightness.blockSignals(False)
        self.slider_contrast.blockSignals(False)
        self.chk_invert.blockSignals(False)
        self.preset_combo.blockSignals(False)

        self.update_image_display()

    def upload_xray(self):
        if not self.patient_id:
            QMessageBox.warning(self, "Warning", "Please open a patient file first.")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Upload Patient X-ray Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )

        if not file_path:
            return

        try:
            # Read file as raw binary bytes
            with open(file_path, 'rb') as f:
                img_bytes = f.read()

            filename = os.path.basename(file_path)
            
            # Custom dialog to ask for Image Type and Description
            from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
            dialog = QDialog(self)
            dialog.setWindowTitle("Image Details")
            dlg_layout = QFormLayout(dialog)
            
            type_combo = QComboBox()
            type_combo.addItems(["X-Ray", "Intraoral Photo", "Extraoral Photo"])
            dlg_layout.addRow("Image Type:", type_combo)
            
            desc_input = QLineEdit(filename)
            dlg_layout.addRow("Description:", desc_input)
            
            btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            btns.accepted.connect(dialog.accept)
            btns.rejected.connect(dialog.reject)
            dlg_layout.addWidget(btns)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                description = desc_input.text().strip() or filename
                image_type = type_combo.currentText()
            else:
                return

            from datetime import date
            today_str = date.today().isoformat()

            # Insert directly into SQLite BLOB
            database.add_patient_xray(self.patient_id, image_type, description, today_str, img_bytes)
            
            # Refresh list and notify
            self.refresh_list()
            self.xray_list_updated.emit()
            QMessageBox.information(self, "Success", f"{image_type} uploaded and securely stored in database. You may now delete the original file.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read/upload image file: {str(e)}")

    def delete_current_xray(self):
        if not self.current_xray_id:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to permanently delete this X-ray from the database?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            database.delete_xray(self.current_xray_id)
            self.clear_display()
            self.refresh_list()
            self.xray_list_updated.emit()

    def clear_display(self):
        self.current_xray_id = None
        self.original_image = None
        self.filtered_image = None
        self.img_label.setPixmap(QPixmap())
        self.img_label.setText("Select an X-ray to view diagnostic details")
        self.controls_widget.setEnabled(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image_display()
