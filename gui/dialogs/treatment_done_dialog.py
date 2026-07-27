# View Clinical Session Details Dialog
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from gui.styles import get_theme_stylesheet, load_theme_setting


class ViewTreatmentDoneDialog(QDialog):
    """Dialog to inspect details of a completed treatment session."""

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
