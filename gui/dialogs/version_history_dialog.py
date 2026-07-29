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
from gui.styles import get_theme_stylesheet, load_theme_setting, detect_system_accent_colors, get_effective_theme_name


class FullVersionHistoryDialog(QDialog):
    """Dialog showing Git-style immutable patient version history timeline and deltas."""

    def __init__(self, patient_id, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.setWindowTitle("Patient Visit History & Clinical Timeline")
        self.setMinimumSize(950, 650)
        self.resize(1100, 750)

        theme_name = load_theme_setting()
        self.effective_theme = get_effective_theme_name(theme_name)
        self.primary_accent, self.hover_accent = detect_system_accent_colors(self.effective_theme)
        self.setStyleSheet(get_theme_stylesheet(theme_name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        p = database.get_patient_details(patient_id)
        p_name = p.get('name', 'Patient') if p else 'Patient'

        lbl_title = QLabel(f"📜 Visit History — {p_name} (ID: {patient_id})")
        lbl_title.setFont(QFont("Ubuntu", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {self.primary_accent};")

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
        lbl_versions.setFont(QFont("Ubuntu", 11, QFont.Weight.Bold))
        lbl_versions.setStyleSheet("color: #0F172A;" if self.effective_theme == "light" else "color: #E2E8F0;")
        left_layout.addWidget(lbl_versions)

        self.list_commits = QListWidget()
        bg_color = "#FFFFFF" if self.effective_theme == "light" else "#161616"
        border_color = "#E2E8F0" if self.effective_theme == "light" else "#2D2D30"
        text_color = "#0F172A" if self.effective_theme == "light" else "#E2E8F0"
        hover_bg = "#F1F5F9" if self.effective_theme == "light" else "#1a2032"

        self.list_commits.setStyleSheet(f"""
            QListWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 6px;
                color: {text_color};
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {border_color};
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {self.primary_accent};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {hover_bg};
            }}
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
        self.lbl_detail_title.setFont(QFont("Ubuntu", 12, QFont.Weight.Bold))
        self.lbl_detail_title.setStyleSheet(f"color: {self.primary_accent};")
        right_layout.addWidget(self.lbl_detail_title)

        self.txt_full_audit = QTextBrowser()
        self.txt_full_audit.setOpenExternalLinks(True)
        self.txt_full_audit.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 15px;
                font-family: 'Ubuntu', 'Cantarell', 'Inter', sans-serif;
                font-size: 13px;
            }}
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

        card_bg = "#F8FAFC" if self.effective_theme == "light" else "#1a2032"
        border_col = "#E2E8F0" if self.effective_theme == "light" else "#2D2D30"
        text_main = "#0F172A" if self.effective_theme == "light" else "#E2E8F0"
        text_sub = "#64748B" if self.effective_theme == "light" else "#94A3B8"
        accent_col = self.primary_accent

        self.lbl_detail_title.setText(f"Visit {v_num} Details — Commit [{v_hash}]")

        status_badge = '<span style="color:#10B981; font-weight:bold;">✓ Cryptographically Locked & Authentic</span>' if verified else '<span style="color:#EF4444; font-weight:bold;">⚠ Verification Failed</span>'

        html = f"""
        <div style="font-family: 'Ubuntu', 'Cantarell', 'Inter', sans-serif;">
            <div style="background:{card_bg}; padding:12px 15px; border-radius:8px; margin-bottom:15px; border:1px solid {border_col};">
                <div style="font-size:15px; font-weight:bold; color:{text_main}; margin-bottom:4px;">Visit {v_num} <span style="color:{text_sub}; font-size:12px;">({v_hash})</span></div>
                <div style="font-size:12px; color:{text_sub};"><b>Recorded:</b> {v_time} &nbsp;|&nbsp; <b>Clinician / Author:</b> {doc}</div>
                <div style="font-size:12px; color:{text_main}; margin-top:4px;"><b>Note:</b> {msg}</div>
                <div style="font-size:11px; margin-top:6px;">{status_badge}</div>
            </div>
        """

        deltas = c.get('deltas', [])
        html += f'<h3 style="color:{accent_col}; margin-top:15px; border-bottom:1px solid {border_col}; padding-bottom:6px; font-size:14px;">Recorded Field Modifications</h3>'
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
                    <div style="background:{card_bg}; border:1px solid {border_col}; border-left:4px solid {accent_col}; padding:8px 12px; margin-bottom:8px; border-radius:6px;">
                        <div style="font-size:11px; color:{text_sub}; font-weight:bold;">{sec} &gt; {subsec} &bull; {title}</div>
                        <div style="margin-top:4px; font-size:12px;">
                            <div style="color:#EF4444; margin-bottom:2px;"><b>- Previous:</b> <span style="text-decoration:line-through;">{old_val}</span></div>
                            <div style="color:#10B981; font-weight:500;"><b>+ Updated:</b> {new_val}</div>
                        </div>
                    </div>
                    """
                elif new_val:
                    html += f"""
                    <div style="background:{card_bg}; border:1px solid {border_col}; border-left:4px solid #10B981; padding:8px 12px; margin-bottom:8px; border-radius:6px;">
                        <div style="font-size:11px; color:{text_sub}; font-weight:bold;">{sec} &gt; {subsec} &bull; {title}</div>
                        <div style="font-size:12.5px; color:{text_main}; margin-top:3px; font-weight:500;">{new_val}</div>
                    </div>
                    """
        else:
            html += f'<div style="color:{text_sub}; font-style:italic; padding:10px;">Visit 1 Baseline Record — Initial patient registration snapshot.</div>'

        snapshot = c.get('snapshot', {})
        if snapshot and isinstance(snapshot, dict):
            html += f'<h3 style="color:{accent_col}; margin-top:20px; border-bottom:1px solid {border_col}; padding-bottom:6px; font-size:14px;">Full Clinical Snapshot at Visit {v_num}</h3>'
            html += '<table style="width:100%; border-collapse:collapse; font-size:12px; margin-top:10px;">'
            html += f'<tr style="background:{card_bg}; color:{text_sub};"><th style="padding:8px; text-align:left; border:1px solid {border_col};">Field Name</th><th style="padding:8px; text-align:left; border:1px solid {border_col};">Recorded Clinical Data</th></tr>'

            for k, v in snapshot.items():
                if v:
                    field_title = k.replace('_', ' ').title()
                    html += f'<tr><td style="padding:8px; border:1px solid {border_col}; font-weight:bold; color:{text_sub}; width:30%;">{field_title}</td><td style="padding:8px; border:1px solid {border_col}; color:{text_main};">{v}</td></tr>'
            html += '</table>'

        html += '</div>'
        self.txt_full_audit.setHtml(html)
