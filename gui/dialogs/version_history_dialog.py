# Full Patient Version History & Clinical Timeline Dialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

import database
from gui.styles import get_theme_stylesheet, load_theme_setting


class FullVersionHistoryDialog(QDialog):
    """Dialog showing Git-style immutable patient version history timeline and deltas."""

    def __init__(self, patient_id, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.setWindowTitle("Patient Visit History & Clinical Timeline")
        self.setMinimumSize(950, 650)
        self.resize(1100, 750)

        theme_name = load_theme_setting()
        self.setStyleSheet(get_theme_stylesheet(theme_name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        p = database.get_patient_details(patient_id)
        p_name = p.get('name', 'Patient') if p else 'Patient'

        lbl_title = QLabel(f"📜 Visit History — {p_name} (ID: {patient_id})")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #0371bb;")

        btn_close = QPushButton("✕ Close Window")
        btn_close.setObjectName("SecondaryBtn")
        btn_close.clicked.connect(self.accept)

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        layout.addLayout(header_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Panel: Timeline List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        lbl_versions = QLabel("Visits Timeline")
        lbl_versions.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_versions.setStyleSheet("color: #E2E8F0;")
        left_layout.addWidget(lbl_versions)

        self.list_commits = QListWidget()
        self.list_commits.setStyleSheet("""
            QListWidget {
                background-color: #161616;
                border: 1px solid #2D2D30;
                border-radius: 8px;
                padding: 6px;
                color: #E2E8F0;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2D2D30;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #0371bb;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #1a2032;
            }
        """)
        self.list_commits.currentRowChanged.connect(self.display_commit_details)
        left_layout.addWidget(self.list_commits)

        left_widget.setMinimumWidth(320)
        splitter.addWidget(left_widget)

        # Right Panel: Audit Details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)

        self.lbl_detail_title = QLabel("Select a visit from timeline to inspect details.")
        self.lbl_detail_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_detail_title.setStyleSheet("color: #0371bb;")
        right_layout.addWidget(self.lbl_detail_title)

        self.txt_full_audit = QTextBrowser()
        self.txt_full_audit.setOpenExternalLinks(True)
        self.txt_full_audit.setStyleSheet("""
            QTextBrowser {
                background-color: #161616;
                color: #E2E8F0;
                border: 1px solid #2D2D30;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
        """)
        right_layout.addWidget(self.txt_full_audit)

        splitter.addWidget(right_widget)
        splitter.setSizes([340, 750])

        layout.addWidget(splitter)

        self.commits = database.get_patient_history_commits(patient_id)
        self.populate_commit_list()

    def populate_commit_list(self):
        self.list_commits.clear()
        if not self.commits:
            self.list_commits.addItem("No patient visit commits recorded yet.")
            return

        for c in self.commits:
            v_num = c['version_number']
            v_hash = c['commit_hash']
            v_time = c['timestamp_formatted']
            v_msg = c['commit_message']
            status_icon = "✓" if c.get('is_verified', True) else "⚠"

            item_text = f"Visit {v_num} ({v_hash}) {status_icon}\n⏰ {v_time}\n📝 {v_msg}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, c)
            self.list_commits.addItem(item)

        if self.commits:
            self.list_commits.setCurrentRow(0)

    def display_commit_details(self, row):
        if row < 0 or not self.commits or row >= len(self.commits):
            return
        c = self.commits[row]

        v_num = c['version_number']
        v_hash = c['commit_hash']
        v_time = c['timestamp_formatted']
        doc = c.get('doctor_name') or 'Dr. Admin'
        msg = c['commit_message']
        verified = c.get('is_verified', True)

        self.lbl_detail_title.setText(f"Visit {v_num} Details — Commit [{v_hash}]")

        status_badge = '<span style="color:#10B981; font-weight:bold;">✓ Cryptographically Locked & Authentic</span>' if verified else '<span style="color:#EF4444; font-weight:bold;">⚠ Verification Failed</span>'

        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif;">
            <div style="background:#1a2032; padding:12px 15px; border-radius:8px; margin-bottom:15px; border:1px solid #2D2D30;">
                <div style="font-size:15px; font-weight:bold; color:#E2E8F0; margin-bottom:4px;">Visit {v_num} <span style="color:#94A3B8; font-size:12px;">({v_hash})</span></div>
                <div style="font-size:12px; color:#94A3B8;"><b>Recorded:</b> {v_time} &nbsp;|&nbsp; <b>Clinician / Author:</b> {doc}</div>
                <div style="font-size:12px; color:#E2E8F0; margin-top:4px;"><b>Note:</b> {msg}</div>
                <div style="font-size:11px; margin-top:6px;">{status_badge}</div>
            </div>
        """

        deltas = c.get('deltas', [])
        html += '<h3 style="color:#0371bb; margin-top:15px; border-bottom:1px solid #2D2D30; padding-bottom:6px; font-size:14px;">Recorded Field Modifications</h3>'
        if deltas and isinstance(deltas, list):
            for d in deltas:
                sec = d.get('section', '')
                subsec = d.get('subsection', '')
                title = d.get('title', '')
                old_val = str(d.get('old_val', '') or '').strip()
                new_val = str(d.get('new_val', '') or '').strip()

                if old_val in ('(Empty)', 'None'):
                    old_val = ''
                if new_val in ('(Empty)', 'None'):
                    new_val = ''

                if old_val and old_val != new_val:
                    html += f"""
                    <div style="background:#1a2032; border:1px solid #2D2D30; border-left:4px solid #0371bb; padding:8px 12px; margin-bottom:8px; border-radius:6px;">
                        <div style="font-size:11px; color:#94A3B8; font-weight:bold;">{sec} &gt; {subsec} &bull; {title}</div>
                        <div style="margin-top:4px; font-size:12px;">
                            <div style="color:#EF4444; margin-bottom:2px;"><b>- Previous:</b> <span style="text-decoration:line-through;">{old_val}</span></div>
                            <div style="color:#10B981; font-weight:500;"><b>+ Updated:</b> {new_val}</div>
                        </div>
                    </div>
                    """
                elif new_val:
                    html += f"""
                    <div style="background:#1a2032; border:1px solid #2D2D30; border-left:4px solid #10B981; padding:8px 12px; margin-bottom:8px; border-radius:6px;">
                        <div style="font-size:11px; color:#94A3B8; font-weight:bold;">{sec} &gt; {subsec} &bull; {title}</div>
                        <div style="font-size:12.5px; color:#E2E8F0; margin-top:3px; font-weight:500;">{new_val}</div>
                    </div>
                    """
        else:
            html += '<div style="color:#94A3B8; font-style:italic; padding:10px;">Visit 1 Baseline Record — Initial patient registration snapshot.</div>'

        snapshot = c.get('snapshot', {})
        if snapshot and isinstance(snapshot, dict):
            html += '<h3 style="color:#0371bb; margin-top:20px; border-bottom:1px solid #2D2D30; padding-bottom:6px; font-size:14px;">Full Clinical Snapshot at Visit ' + str(v_num) + '</h3>'
            html += '<table style="width:100%; border-collapse:collapse; font-size:12px; margin-top:10px;">'
            html += '<tr style="background:#1a2032; color:#94A3B8;"><th style="padding:8px; text-align:left; border:1px solid #2D2D30;">Field Name</th><th style="padding:8px; text-align:left; border:1px solid #2D2D30;">Recorded Clinical Data</th></tr>'

            for k, v in snapshot.items():
                if v:
                    field_title = k.replace('_', ' ').title()
                    html += f'<tr><td style="padding:8px; border:1px solid #2D2D30; font-weight:bold; color:#94A3B8; width:30%;">{field_title}</td><td style="padding:8px; border:1px solid #2D2D30; color:#E2E8F0;">{v}</td></tr>'
            html += '</table>'

        html += '</div>'
        self.txt_full_audit.setHtml(html)
