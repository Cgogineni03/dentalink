# DentaLink Dental Chart Widget (widgets/dental_chart.py)
import os
import math
from PyQt6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QRadioButton, QButtonGroup, QCheckBox, 
                             QTextEdit, QPushButton, QMessageBox, QGroupBox,
                             QTabWidget, QComboBox, QLineEdit, QInputDialog)
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QFont, QPainterPath
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal

import database
from gui.styles import resolve_theme_name


class ToothEditDialog(QDialog):
    def __init__(self, tooth_num, existing_conditions, existing_notes, existing_perio, parent=None):
        super().__init__(parent)
        self.tooth_num = tooth_num
        self.notes = existing_notes
        self.result_data = None
        self.init_ui(existing_conditions, existing_perio)

    def init_ui(self, existing_conditions, existing_perio):
        self.setWindowTitle(f"Tooth #{self.tooth_num} Condition Editor")
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)

        # Title Label
        title = QLabel(f"Configure Tooth #{self.tooth_num}")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- TAB 1: TOOTH CONDITION ---
        tab_cond = QWidget()
        cond_layout = QVBoxLayout(tab_cond)

        whole_group = QGroupBox("Whole Tooth Condition")
        whole_layout = QVBoxLayout(whole_group)
        self.whole_btn_group = QButtonGroup(self)
        
        self.radio_healthy = QRadioButton("Normal / Healthy / Restored")
        self.radio_missing = QRadioButton("Missing (Extracted / Unerupted)")
        self.radio_implant = QRadioButton("Dental Implant")
        self.radio_crown = QRadioButton("Full Crown")
        self.radio_rct = QRadioButton("Root Canal Treated (RCT)")

        self.whole_btn_group.addButton(self.radio_healthy, 0)
        self.whole_btn_group.addButton(self.radio_missing, 1)
        self.whole_btn_group.addButton(self.radio_implant, 2)
        self.whole_btn_group.addButton(self.radio_crown, 3)
        self.whole_btn_group.addButton(self.radio_rct, 4)

        whole_layout.addWidget(self.radio_healthy)
        whole_layout.addWidget(self.radio_missing)
        whole_layout.addWidget(self.radio_implant)
        whole_layout.addWidget(self.radio_crown)
        whole_layout.addWidget(self.radio_rct)

        whole_condition = 'healthy'
        for cond in existing_conditions:
            if cond['surface'] == 'ALL':
                whole_condition = cond['condition']

        if whole_condition == 'missing':
            self.radio_missing.setChecked(True)
        elif whole_condition == 'implant':
            self.radio_implant.setChecked(True)
        elif whole_condition == 'crown':
            self.radio_crown.setChecked(True)
        elif whole_condition == 'root-canal':
            self.radio_rct.setChecked(True)
        else:
            self.radio_healthy.setChecked(True)

        cond_layout.addWidget(whole_group)

        self.surface_group = QGroupBox("Surface-Specific Conditions")
        surface_layout = QVBoxLayout(self.surface_group)
        
        self.surface_widgets = {}
        surfaces = [
            ('O', 'Occlusal / Incisal (Biting Surface)'),
            ('B', 'Buccal / Facial (Cheek / Lip Side)'),
            ('L', 'Lingual (Tongue Side)'),
            ('M', 'Mesial (Front Contact)'),
            ('D', 'Distal (Back Contact)')
        ]

        existing_surfs = {c['surface']: c['condition'] for c in existing_conditions if c['surface'] != 'ALL'}

        for code, label in surfaces:
            surf_row = QHBoxLayout()
            lbl = QLabel(label)
            
            grp = QButtonGroup(self)
            r_none = QRadioButton("Normal")
            r_decay = QRadioButton("Decay (Cavity)")
            r_fill = QRadioButton("Filled")
            
            grp.addButton(r_none, 0)
            grp.addButton(r_decay, 1)
            grp.addButton(r_fill, 2)
            
            curr_cond = existing_surfs.get(code, 'healthy')
            if curr_cond == 'decay':
                r_decay.setChecked(True)
            elif curr_cond == 'filled':
                r_fill.setChecked(True)
            else:
                r_none.setChecked(True)

            surf_row.addWidget(lbl, 4)
            surf_row.addWidget(r_none, 2)
            surf_row.addWidget(r_decay, 2)
            surf_row.addWidget(r_fill, 2)
            
            surface_layout.addLayout(surf_row)
            self.surface_widgets[code] = {
                'group': grp, 'none': r_none, 'decay': r_decay, 'filled': r_fill
            }

        cond_layout.addWidget(self.surface_group)

        self.radio_healthy.toggled.connect(self.toggle_surface_section)
        self.radio_rct.toggled.connect(self.toggle_surface_section) 
        self.toggle_surface_section()

        notes_lbl = QLabel("Clinical Notes:")
        cond_layout.addWidget(notes_lbl)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(self.notes)
        self.notes_edit.setMaximumHeight(80)
        cond_layout.addWidget(self.notes_edit)

        self.tabs.addTab(tab_cond, "Tooth Condition")

        # --- TAB 2: PERIODONTAL STATUS ---
        tab_perio = QWidget()
        perio_layout = QVBoxLayout(tab_perio)

        perio_info = QLabel("Record standard 6-point probing depths (in mm). Values >= 4mm will trigger a warning on the chart.")
        perio_info.setWordWrap(True)
        perio_info.setStyleSheet("color: #94A3B8; margin-bottom: 10px;")
        perio_layout.addWidget(perio_info)

        mob_layout = QHBoxLayout()
        mob_layout.addWidget(QLabel("Mobility Grade:"))
        self.combo_mobility = QComboBox()
        self.combo_mobility.addItems(["0 (Normal)", "1 (Slight)", "2 (Moderate)", "3 (Severe)"])
        if existing_perio:
            self.combo_mobility.setCurrentIndex(existing_perio.get('mobility', 0))
        mob_layout.addWidget(self.combo_mobility)
        mob_layout.addStretch()
        perio_layout.addLayout(mob_layout)
        
        pd_f_layout = QHBoxLayout()
        pd_f_layout.addWidget(QLabel("Facial PD (Distal, Mid, Mesial):"))
        self.pd_f_inputs = [QLineEdit(), QLineEdit(), QLineEdit()]
        pd_f_vals = existing_perio.get('pd_facial', '').split(',') if existing_perio and existing_perio.get('pd_facial') else ['', '', '']
        for i, val in enumerate(pd_f_vals):
            if i < 3:
                self.pd_f_inputs[i].setText(val)
                self.pd_f_inputs[i].setFixedWidth(40)
                pd_f_layout.addWidget(self.pd_f_inputs[i])
        pd_f_layout.addStretch()
        perio_layout.addLayout(pd_f_layout)
        
        pd_l_layout = QHBoxLayout()
        pd_l_layout.addWidget(QLabel("Lingual PD (Distal, Mid, Mesial):"))
        self.pd_l_inputs = [QLineEdit(), QLineEdit(), QLineEdit()]
        pd_l_vals = existing_perio.get('pd_lingual', '').split(',') if existing_perio and existing_perio.get('pd_lingual') else ['', '', '']
        for i, val in enumerate(pd_l_vals):
            if i < 3:
                self.pd_l_inputs[i].setText(val)
                self.pd_l_inputs[i].setFixedWidth(40)
                pd_l_layout.addWidget(self.pd_l_inputs[i])
        pd_l_layout.addStretch()
        perio_layout.addLayout(pd_l_layout)
        
        self.chk_bop = QCheckBox("Bleeding on Probing (BOP) Present")
        if existing_perio and existing_perio.get('bop'):
            self.chk_bop.setChecked(True)
        perio_layout.addWidget(self.chk_bop)
        perio_layout.addStretch()

        self.tabs.addTab(tab_perio, "Periodontal Status")

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save Data")
        btn_save.clicked.connect(self.on_save)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def toggle_surface_section(self):
        is_normal = self.radio_healthy.isChecked() or self.radio_rct.isChecked()
        self.surface_group.setEnabled(is_normal)

    def on_save(self):
        self.result_data = {
            'whole': 'healthy',
            'surfaces': {},
            'notes': self.notes_edit.toPlainText().strip(),
            'perio': {
                'mobility': self.combo_mobility.currentIndex(),
                'pd_facial': ','.join([i.text().strip() for i in self.pd_f_inputs]),
                'pd_lingual': ','.join([i.text().strip() for i in self.pd_l_inputs]),
                'bop': 1 if self.chk_bop.isChecked() else 0
            }
        }

        # Check whole status
        if self.radio_missing.isChecked():
            self.result_data['whole'] = 'missing'
        elif self.radio_implant.isChecked():
            self.result_data['whole'] = 'implant'
        elif self.radio_crown.isChecked():
            self.result_data['whole'] = 'crown'
        elif self.radio_rct.isChecked():
            self.result_data['whole'] = 'root-canal'
        else:
            self.result_data['whole'] = 'healthy'

        # If whole status is normal or RCT, read surface conditions
        if self.result_data['whole'] in ['healthy', 'root-canal']:
            for code, widgets in self.surface_widgets.items():
                if widgets['decay'].isChecked():
                    self.result_data['surfaces'][code] = 'decay'
                elif widgets['filled'].isChecked():
                    self.result_data['surfaces'][code] = 'filled'

        self.accept()


class ChartDrawingCanvas(QWidget):
    def __init__(self, parent_chart):
        super().__init__(parent_chart)
        self.parent_chart = parent_chart
        self.setMinimumSize(820, 260)

    def paintEvent(self, event):
        self.parent_chart.paint_chart_view(event, self)

    def mousePressEvent(self, event):
        self.parent_chart.handle_mouse_press(event)


class DentalChartWidget(QWidget):
    chart_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_id = None
        self.conditions = [] 
        self.perio = []
        self.dentition_type = 'Permanent Universal'
        self.supernumerary_teeth = []
        self.theme_name = "classic"
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Control Bar
        control_bar = QHBoxLayout()
        control_bar.addWidget(QLabel("Dentition:"))
        self.combo_dentition = QComboBox()
        self.combo_dentition.addItems([
            "Permanent (Universal 1-32)", 
            "Permanent (FDI Two-Digit)", 
            "Primary (Universal A-T)", 
            "Primary (FDI Two-Digit)"
        ])
        self.combo_dentition.currentTextChanged.connect(self.on_dentition_changed)
        control_bar.addWidget(self.combo_dentition)
        
        control_bar.addSpacing(20)
        
        self.btn_add_supernumerary = QPushButton("+ Add Supernumerary Tooth")
        self.btn_add_supernumerary.clicked.connect(self.add_supernumerary_clicked)
        control_bar.addWidget(self.btn_add_supernumerary)
        
        control_bar.addStretch()
        self.main_layout.addLayout(control_bar, 0)
        
        # The visual chart part
        self.chart_view = ChartDrawingCanvas(self)
        self.main_layout.addWidget(self.chart_view, 1)
        
        # Add DMFT Panel
        self.dmft_panel = QGroupBox("Clinical Indices")
        dmft_layout = QHBoxLayout(self.dmft_panel)
        
        self.lbl_dmft = QLabel("DMFT Score: D=0, M=0, F=0 (Total: 0)")
        self.lbl_dmft.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.lbl_dmft.setStyleSheet("color: #38BDF8;")
        
        dmft_layout.addWidget(self.lbl_dmft)
        dmft_layout.addStretch()
        self.main_layout.addWidget(self.dmft_panel, 0)
        
        self.init_dimensions()

    def update_theme(self, theme_name):
        resolved = resolve_theme_name(theme_name)
        self.theme_name = resolved
        
        # Also update DMFT score styling color based on theme
        if resolved == "light":
            self.lbl_dmft.setStyleSheet("color: #0371bb;")
        else:
            self.lbl_dmft.setStyleSheet("color: #38BDF8;")
            
        self.chart_view.update()


    def update_canvas_size(self):
        if self.supernumerary_teeth:
            self.chart_view.setMinimumSize(820, 360)
        else:
            self.chart_view.setMinimumSize(820, 260)

    def on_dentition_changed(self, text):
        if "Permanent" in text:
            if "FDI" in text:
                self.dentition_type = 'Permanent FDI'
            else:
                self.dentition_type = 'Permanent Universal'
        else:
            if "FDI" in text:
                self.dentition_type = 'Primary FDI'
            else:
                self.dentition_type = 'Primary Universal'
        self.init_dimensions()
        self.calculate_dmft()
        self.chart_view.update()

    def add_supernumerary_clicked(self):
        if not self.patient_id:
            QMessageBox.warning(self, "No Patient", "Please open a patient case file first.")
            return
            
        text, ok = QInputDialog.getText(self, "Add Supernumerary Tooth", "Enter tooth label (e.g., 99, 51, S1):")
        if ok and text.strip():
            label = text.strip().upper()
            if label in self.teeth_layout:
                QMessageBox.warning(self, "Duplicate", f"Tooth {label} is already on the chart.")
                return
                
            self.supernumerary_teeth.append(label)
            # Save default healthy condition so it gets initialized in DB
            database.save_tooth_condition(self.patient_id, label, 'ALL', 'healthy', 'Supernumerary tooth')
            
            self.update_canvas_size()
            self.init_dimensions()
            # Reload from DB to sync lists
            self.load_patient(self.patient_id)

    def init_dimensions(self):
        self.margin_y = 45
        self.tooth_w = 36
        self.tooth_h = 36
        self.tooth_gap = 10
        self.row_gap = 80

        self.teeth_layout = {}
        
        if self.dentition_type == 'Permanent Universal':
            self.margin_x = 40
            for i in range(16):
                tooth_num = str(i + 1)
                x = self.margin_x + i * (self.tooth_w + self.tooth_gap)
                y = self.margin_y
                self.teeth_layout[tooth_num] = {'x': x, 'y': y, 'row': 'upper'}

            for i in range(16):
                tooth_num = str(32 - i)
                x = self.margin_x + i * (self.tooth_w + self.tooth_gap)
                y = self.margin_y + self.tooth_h + self.row_gap
                self.teeth_layout[tooth_num] = {'x': x, 'y': y, 'row': 'lower'}
        elif self.dentition_type == 'Permanent FDI':
            self.margin_x = 40
            upper_fdi = ['18', '17', '16', '15', '14', '13', '12', '11', '21', '22', '23', '24', '25', '26', '27', '28']
            lower_fdi = ['48', '47', '46', '45', '44', '43', '42', '41', '31', '32', '33', '34', '35', '36', '37', '38']
            for i, label in enumerate(upper_fdi):
                x = self.margin_x + i * (self.tooth_w + self.tooth_gap)
                y = self.margin_y
                self.teeth_layout[label] = {'x': x, 'y': y, 'row': 'upper'}
            for i, label in enumerate(lower_fdi):
                x = self.margin_x + i * (self.tooth_w + self.tooth_gap)
                y = self.margin_y + self.tooth_h + self.row_gap
                self.teeth_layout[label] = {'x': x, 'y': y, 'row': 'lower'}
        elif self.dentition_type == 'Primary Universal':
            self.margin_x = 185 # Center 10 teeth
            upper_primary = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            lower_primary = ['T', 'S', 'R', 'Q', 'P', 'O', 'N', 'M', 'L', 'K']
            for i, label in enumerate(upper_primary):
                x = self.margin_x + i * (self.tooth_w + self.tooth_gap)
                y = self.margin_y
                self.teeth_layout[label] = {'x': x, 'y': y, 'row': 'upper'}
            for i, label in enumerate(lower_primary):
                x = self.margin_x + i * (self.tooth_w + self.tooth_gap)
                y = self.margin_y + self.tooth_h + self.row_gap
                self.teeth_layout[label] = {'x': x, 'y': y, 'row': 'lower'}
        else: # Primary FDI
            self.margin_x = 185 # Center 10 teeth
            upper_primary_fdi = ['55', '54', '53', '52', '51', '61', '62', '63', '64', '65']
            lower_primary_fdi = ['85', '84', '83', '82', '81', '71', '72', '73', '74', '75']
            for i, label in enumerate(upper_primary_fdi):
                x = self.margin_x + i * (self.tooth_w + self.tooth_gap)
                y = self.margin_y
                self.teeth_layout[label] = {'x': x, 'y': y, 'row': 'upper'}
            for i, label in enumerate(lower_primary_fdi):
                x = self.margin_x + i * (self.tooth_w + self.tooth_gap)
                y = self.margin_y + self.tooth_h + self.row_gap
                self.teeth_layout[label] = {'x': x, 'y': y, 'row': 'lower'}

        # Draw supernumerary teeth at the bottom
        if self.supernumerary_teeth:
            sup_row_y = self.margin_y + 2 * self.tooth_h + self.row_gap + 30
            num_sup = len(self.supernumerary_teeth)
            total_sup_w = num_sup * self.tooth_w + (num_sup - 1) * self.tooth_gap
            start_x = (820 - total_sup_w) / 2
            for i, label in enumerate(self.supernumerary_teeth):
                x = start_x + i * (self.tooth_w + self.tooth_gap)
                self.teeth_layout[label] = {'x': x, 'y': sup_row_y, 'row': 'supernumerary'}

    def load_patient(self, patient_id):
        self.patient_id = patient_id
        self.supernumerary_teeth = []
        if patient_id:
            details = database.get_patient_details(patient_id)
            if details:
                self.conditions = details.get('dental_chart', [])
                self.perio = details.get('perio_chart', [])
                
                # Check for any saved supernumerary teeth (non-standard labels)
                standard_permanent = [str(i) for i in range(1, 33)]
                standard_primary = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
                
                for row in self.conditions:
                    t_num = str(row['tooth_number'])
                    if t_num not in standard_permanent and t_num not in standard_primary:
                        if t_num not in self.supernumerary_teeth:
                            self.supernumerary_teeth.append(t_num)
                            
                for row in self.perio:
                    t_num = str(row['tooth_number'])
                    if t_num not in standard_permanent and t_num not in standard_primary:
                        if t_num not in self.supernumerary_teeth:
                            self.supernumerary_teeth.append(t_num)
            else:
                self.conditions = []
                self.perio = []
        else:
            self.conditions = []
            self.perio = []
            
        self.update_canvas_size()
        self.init_dimensions()
        self.calculate_dmft()
        self.chart_view.update()

    def calculate_dmft(self):
        tooth_states = {}
        for row in self.conditions:
            t = str(row['tooth_number'])
            if t not in tooth_states:
                tooth_states[t] = {'whole': None, 'surfaces': {}}
            
            if row['surface'] == 'ALL':
                tooth_states[t]['whole'] = row['condition']
            else:
                tooth_states[t]['surfaces'][row['surface']] = row['condition']
                
        d, m, f = 0, 0, 0
        if 'Permanent' in self.dentition_type:
            if 'FDI' in self.dentition_type:
                active_set = ['18', '17', '16', '15', '14', '13', '12', '11', '21', '22', '23', '24', '25', '26', '27', '28',
                              '48', '47', '46', '45', '44', '43', '42', '41', '31', '32', '33', '34', '35', '36', '37', '38']
            else:
                active_set = [str(i) for i in range(1, 33)]
            label_prefix = "DMFT Score (Permanent)"
        else:
            if 'FDI' in self.dentition_type:
                active_set = ['55', '54', '53', '52', '51', '61', '62', '63', '64', '65',
                              '85', '84', '83', '82', '81', '71', '72', '73', '74', '75']
            else:
                active_set = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
            label_prefix = "dmft Score (Primary)"
            
        for t in active_set:
            state = tooth_states.get(t, {'whole': None, 'surfaces': {}})
            if state.get('whole') == 'missing':
                m += 1
            elif state.get('whole') in ['implant', 'crown']:
                f += 1
            else:
                has_decay = False
                has_filling = False
                for surf_code, cond in state.get('surfaces', {}).items():
                    if cond == 'decay':
                        has_decay = True
                    elif cond == 'filled':
                        has_filling = True
                
                if has_decay:
                    d += 1
                elif has_filling or state.get('whole') == 'root-canal':
                    f += 1
                    
        total = d + m + f
        self.lbl_dmft.setText(f"{label_prefix}: d={d}, m={m}, f={f}  (Total: {total})")

    def get_tooth_paths(self, tooth_num, x, y):
        w, h = self.tooth_w, self.tooth_h
        d = 10 
        
        paths = {}
        # Anterior teeth (circular shape)
        is_anterior = self.is_anterior_tooth(tooth_num)
            
        if is_anterior:
            cx, cy = x + w/2, y + h/2
            r_inner = w/2 - d
            
            path_o = QPainterPath()
            path_o.addEllipse(QPointF(cx, cy), r_inner, r_inner)
            paths['O'] = path_o
            
            def get_sector(start_angle, span_angle):
                p = QPainterPath()
                p.moveTo(cx + r_inner * math.cos(math.radians(-start_angle)), cy + r_inner * math.sin(math.radians(-start_angle)))
                p.arcTo(QRectF(x, y, w, h), start_angle, span_angle)
                p.arcTo(QRectF(x+d, y+d, w-2*d, h-2*d), start_angle + span_angle, -span_angle)
                p.closeSubpath()
                return p
                
            paths['B'] = get_sector(45, 90)   # Top quadrant
            paths['L'] = get_sector(225, 90)  # Bottom quadrant
            paths['M'] = get_sector(135, 90)  # Left quadrant
            paths['D'] = get_sector(315, 90)  # Right quadrant
            
        else:
            # Posterior teeth (rounded rectangle outer boundaries, geometric compartments)
            buccal = QPolygonF([QPointF(x, y), QPointF(x + w, y), QPointF(x + w - d, y + d), QPointF(x + d, y + d)])
            lingual = QPolygonF([QPointF(x + d, y + h - d), QPointF(x + w - d, y + h - d), QPointF(x + w, y + h), QPointF(x, y + h)])
            mesial = QPolygonF([QPointF(x, y), QPointF(x + d, y + d), QPointF(x + d, y + h - d), QPointF(x, y + h)])
            distal = QPolygonF([QPointF(x + w - d, y + d), QPointF(x + w, y), QPointF(x + w, y + h), QPointF(x + w - d, y + h - d)])
            occlusal = QPolygonF([QPointF(x + d, y + d), QPointF(x + w - d, y + d), QPointF(x + w - d, y + h - d), QPointF(x + d, y + h - d)])
            
            for key, poly in [('B', buccal), ('L', lingual), ('M', mesial), ('D', distal), ('O', occlusal)]:
                p = QPainterPath()
                p.addPolygon(poly)
                paths[key] = p
                
        return paths

    def is_anterior_tooth(self, tooth_num):
        if tooth_num in ['6','7','8','9','10','11', '22','23','24','25','26','27']:
            return True
        if tooth_num in ['C','D','E','F','G','H', 'M','N','O','P','Q','R']:
            return True
        if tooth_num in ['13','12','11','21','22','23','33','32','31','41','42','43']:
            return True
        if tooth_num in ['53','52','51','61','62','63','73','72','71','81','82','83']:
            return True
        return False

    def draw_tooth_silhouette(self, painter, tx, ty, w, h, tooth_num, row_type):
        is_molar = not self.is_anterior_tooth(tooth_num)
        is_upper = (row_type == 'upper')
                
        painter.save()
        
        # Determine colors from active theme (populated in paint_chart_view)
        outline_color = getattr(self, 'active_silhouette_outline', QColor(148, 163, 184, 120))
        fill_color = getattr(self, 'active_silhouette_fill', QColor(71, 85, 105, 20))
        
        painter.setPen(QPen(outline_color, 1.2)) 
        painter.setBrush(QBrush(fill_color)) 
        
        path = QPainterPath()
        cx = tx + w/2
        
        if is_upper:
            # Upper teeth: roots point UP (y decreases)
            crown_top = ty
            crown_bottom = ty + h
            root_tip_y = ty - 22
            
            if is_molar:
                path.moveTo(tx, crown_bottom)
                path.cubicTo(tx - 3, crown_top + 5, tx, crown_top, tx + 4, crown_top)
                
                # Left root
                path.lineTo(tx + 2, root_tip_y)
                path.cubicTo(tx + 4, root_tip_y - 2, tx + 6, root_tip_y - 2, tx + 8, crown_top)
                
                # Center root
                path.lineTo(cx, root_tip_y + 4)
                path.cubicTo(cx + 2, root_tip_y + 2, cx + 4, root_tip_y + 2, cx + 6, crown_top)
                
                # Right root
                path.lineTo(tx + w - 8, root_tip_y)
                path.cubicTo(tx + w - 6, root_tip_y - 2, tx + w - 4, root_tip_y - 2, tx + w - 2, crown_top)
                
                path.cubicTo(tx + w, crown_top, tx + w + 3, crown_top + 5, tx + w, crown_bottom)
                path.closeSubpath()
            else:
                path.moveTo(tx + 4, crown_bottom)
                path.cubicTo(tx, crown_top + 8, tx + 2, crown_top, tx + 10, crown_top)
                
                # Single root tip
                path.lineTo(cx - 3, root_tip_y)
                path.cubicTo(cx - 1, root_tip_y - 3, cx + 1, root_tip_y - 3, cx + 3, root_tip_y)
                path.lineTo(tx + w - 10, crown_top)
                
                path.cubicTo(tx + w - 2, crown_top, tx + w, crown_top + 8, tx + w - 4, crown_bottom)
                path.closeSubpath()
        else:
            # Lower teeth: roots point DOWN (y increases)
            crown_top = ty
            crown_bottom = ty + h
            root_tip_y = ty + h + 22
            
            if is_molar:
                path.moveTo(tx, crown_top)
                path.cubicTo(tx - 3, crown_bottom - 5, tx, crown_bottom, tx + 6, crown_bottom)
                
                # Left root
                path.lineTo(tx + 4, root_tip_y)
                path.cubicTo(tx + 6, root_tip_y + 2, tx + 8, root_tip_y + 2, tx + 10, crown_bottom)
                
                # Right root
                path.lineTo(tx + w - 10, root_tip_y)
                path.cubicTo(tx + w - 8, root_tip_y + 2, tx + w - 6, root_tip_y + 2, tx + w - 4, crown_bottom)
                
                path.cubicTo(tx + w, crown_bottom, tx + w + 3, crown_bottom - 5, tx + w, crown_top)
                path.closeSubpath()
            else:
                path.moveTo(tx + 4, crown_top)
                path.cubicTo(tx, crown_bottom - 8, tx + 2, crown_bottom, tx + 10, crown_bottom)
                
                # Single root tip
                path.lineTo(cx - 3, root_tip_y)
                path.cubicTo(cx - 1, root_tip_y + 3, cx + 1, root_tip_y + 3, cx + 3, root_tip_y)
                path.lineTo(tx + w - 10, crown_bottom)
                
                path.cubicTo(tx + w - 2, crown_bottom, tx + w, crown_bottom - 8, tx + w - 4, crown_top)
                path.closeSubpath()
                
        painter.drawPath(path)
        painter.restore()

    def paint_chart_view(self, event, canvas):
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Theme-aware colors
        if self.theme_name == "light":
            bg_color = QColor(255, 255, 255)
            border_color = QColor(209, 213, 219)
            midline_color = QColor(156, 163, 175)
            title_color = QColor(71, 85, 105)
            label_color = QColor(15, 23, 42)
            
            self.active_silhouette_outline = QColor(156, 163, 175, 150)
            self.active_silhouette_fill = QColor(243, 244, 246, 180)
            
            color_missing = QColor(209, 213, 219, 240)
            color_normal_brush = QColor(255, 255, 255)
            color_normal_pen = QPen(QColor(156, 163, 175), 1.2)
            implant_base_bg = QColor(243, 244, 246)
        else:
            # Custom Dark theme
            bg_color = QColor(22, 22, 22)
            border_color = QColor(45, 45, 48)
            midline_color = QColor(70, 80, 110)
            title_color = QColor(140, 150, 180)
            label_color = QColor(226, 232, 240)
            
            self.active_silhouette_outline = QColor(148, 163, 184, 120)
            self.active_silhouette_fill = QColor(71, 85, 105, 20)
            
            color_missing = QColor(50, 55, 70, 240)
            color_normal_brush = QColor(240, 244, 248)
            color_normal_pen = QPen(QColor(100, 116, 139), 1)
            implant_base_bg = QColor(40, 45, 55)

        painter.setBrush(bg_color)
        painter.setPen(QPen(border_color, 1.5))
        painter.drawRoundedRect(0, 0, canvas.width(), canvas.height(), 10, 10)

        font_label = QFont("Arial", 8, QFont.Weight.Bold)
        font_title = QFont("Arial", 9, QFont.Weight.Bold)

        midline_x = self.margin_x + (8 * (self.tooth_w + self.tooth_gap) if 'Permanent' in self.dentition_type else 5 * (self.tooth_w + self.tooth_gap)) - (self.tooth_gap / 2)
        painter.setPen(QPen(midline_color, 1, Qt.PenStyle.DashLine))
        painter.drawLine(int(midline_x), 10, int(midline_x), canvas.height() - 10)

        painter.setPen(title_color)
        painter.setFont(font_title)
        
        if 'Permanent' in self.dentition_type:
            painter.drawText(15, 20, "UPPER JAW (Permanent)")
            painter.drawText(15, 230 if not self.supernumerary_teeth else 340, "LOWER JAW (Permanent)")
        else:
            painter.drawText(15, 20, "UPPER JAW (Primary)")
            painter.drawText(15, 230 if not self.supernumerary_teeth else 340, "LOWER JAW (Primary)")

        if self.supernumerary_teeth:
            painter.drawText(15, 260, "EXTRA / SUPERNUMERARY TEETH")

        tooth_states = {}
        for row in self.conditions:
            t = str(row['tooth_number'])
            if t not in tooth_states:
                tooth_states[t] = {'whole': None, 'surfaces': {}, 'notes': ''}
            if row['surface'] == 'ALL':
                tooth_states[t]['whole'] = row['condition']
                tooth_states[t]['notes'] = row['notes']
            else:
                tooth_states[t]['surfaces'][row['surface']] = row['condition']
                if row['notes']:
                    tooth_states[t]['notes'] = row['notes']
                    
        perio_states = {}
        for row in self.perio:
            perio_states[str(row['tooth_number'])] = row

        color_decay = QColor(239, 68, 68, 220)  
        color_filled = QColor(16, 185, 129, 220) 
        color_crown = QColor(245, 158, 11, 200)  
        color_implant = QColor(6, 182, 212, 220) 
        color_rct_line = QColor(239, 68, 68)     
        color_warning = QColor(220, 38, 38)

        for tooth_num, pos in self.teeth_layout.items():
            tx, ty = pos['x'], pos['y']
            row_type = pos['row']
            
            state = tooth_states.get(tooth_num, {'whole': None, 'surfaces': {}, 'notes': ''})
            whole_cond = state['whole']
            surf_conds = state['surfaces']

            # 1. Draw anatomical silhouette background first
            self.draw_tooth_silhouette(painter, tx, ty, self.tooth_w, self.tooth_h, tooth_num, row_type)

            painter.setPen(label_color)
            painter.setFont(font_label)
            num_str = str(tooth_num)
            
            if row_type == 'upper':
                label_y = int(ty - 26)
            elif row_type == 'lower':
                label_y = int(ty + self.tooth_h + 32)
            else: # supernumerary
                label_y = int(ty + self.tooth_h + 20)
            
            painter.drawText(int(tx + (self.tooth_w / 2) - 4), label_y, num_str)
            
            # 2. Check for periodontal warnings (PD >= 4 or BOP)
            p_state = perio_states.get(tooth_num)
            has_warning = False
            if p_state:
                if p_state['bop']:
                    has_warning = True
                else:
                    for pd_str in [p_state['pd_facial'], p_state['pd_lingual']]:
                        for pd in pd_str.split(','):
                            if pd.strip().isdigit() and int(pd.strip()) >= 4:
                                has_warning = True
                                break
            
            if has_warning:
                warn_x = int(tx + self.tooth_w - 6)
                warn_y = int(label_y - 10)
                poly = QPolygonF([QPointF(warn_x, warn_y+8), QPointF(warn_x+8, warn_y+8), QPointF(warn_x+4, warn_y)])
                painter.setBrush(color_warning)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawPolygon(poly)

            # 3. Draw Condition Overlays (interactive grids)
            paths = self.get_tooth_paths(tooth_num, tx, ty)

            if whole_cond == 'missing':
                painter.setBrush(color_missing)
                painter.setPen(QPen(border_color, 1))
                if self.is_anterior_tooth(tooth_num):
                    painter.drawEllipse(QRectF(tx, ty, self.tooth_w, self.tooth_h))
                else:
                    painter.drawRect(QRectF(tx, ty, self.tooth_w, self.tooth_h))
                painter.setPen(QPen(border_color, 2))
                painter.drawLine(int(tx), int(ty), int(tx + self.tooth_w), int(ty + self.tooth_h))
                painter.drawLine(int(tx + self.tooth_w), int(ty), int(tx), int(ty + self.tooth_h))
                continue

            elif whole_cond == 'implant':
                painter.setBrush(implant_base_bg)
                painter.setPen(QPen(color_implant, 1.5))
                if self.is_anterior_tooth(tooth_num):
                    painter.drawEllipse(QRectF(tx, ty, self.tooth_w, self.tooth_h))
                else:
                    painter.drawRect(QRectF(tx, ty, self.tooth_w, self.tooth_h))
                painter.setPen(QPen(color_implant, 2))
                mid = int(tx + self.tooth_w / 2)
                painter.drawLine(mid, int(ty + 5), mid, int(ty + self.tooth_h - 5))
                for dy in range(10, int(self.tooth_h - 5), 6):
                    painter.drawLine(mid - 6, int(ty + dy), mid + 6, int(ty + dy))
                continue

            elif whole_cond == 'crown':
                painter.setBrush(color_crown)
                painter.setPen(QPen(QColor(217, 119, 6), 1.5))
                if self.is_anterior_tooth(tooth_num):
                    painter.drawEllipse(QRectF(tx, ty, self.tooth_w, self.tooth_h))
                else:
                    painter.drawRect(QRectF(tx, ty, self.tooth_w, self.tooth_h))
                painter.setPen(QPen(QColor(255, 255, 255, 150), 1.5))
                painter.drawLine(int(tx + 4), int(ty + 4), int(tx + 12), int(ty + 4))
                painter.drawLine(int(tx + 4), int(ty + 4), int(tx + 4), int(ty + 12))
                continue

            # Draw 5 individual surface segments
            for surf_code, path in paths.items():
                cond = surf_conds.get(surf_code, 'healthy')
                if cond == 'decay':
                    brush = QBrush(color_decay)
                elif cond == 'filled':
                    brush = QBrush(color_filled)
                else:
                    brush = QBrush(color_normal_brush)
                painter.setBrush(brush)
                painter.setPen(color_normal_pen)
                painter.drawPath(path)

            if whole_cond == 'root-canal':
                painter.setPen(QPen(color_rct_line, 2.5))
                mid_x = int(tx + self.tooth_w / 2)
                painter.drawLine(mid_x, int(ty + 4), mid_x, int(ty + self.tooth_h - 4))
                painter.drawLine(mid_x - 4, int(ty + self.tooth_h - 4), mid_x + 4, int(ty + self.tooth_h - 4))

    def handle_mouse_press(self, event):
        if not self.patient_id:
            return
            
        pos = event.position()
        clicked_tooth = None

        for tooth_num, coords in self.teeth_layout.items():
            tx, ty = coords['x'], coords['y']
            rect = QRectF(tx, ty, self.tooth_w, self.tooth_h)
            if rect.contains(pos):
                clicked_tooth = tooth_num
                break

        if clicked_tooth:
            self.open_tooth_editor(clicked_tooth)

    def open_tooth_editor(self, tooth_num):
        existing_conditions = [row for row in self.conditions if str(row['tooth_number']) == str(tooth_num)]
        
        existing_notes = ""
        for r in existing_conditions:
            if r['notes']:
                existing_notes = r['notes']
                break

        existing_perio = None
        for r in getattr(self, 'perio', []):
            if str(r['tooth_number']) == str(tooth_num):
                existing_perio = r
                break
                
        dialog = ToothEditDialog(tooth_num, existing_conditions, existing_notes, existing_perio, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.result_data
            
            if result['whole'] != 'healthy':
                database.save_tooth_condition(self.patient_id, tooth_num, 'B', 'healthy')
                database.save_tooth_condition(self.patient_id, tooth_num, 'L', 'healthy')
                database.save_tooth_condition(self.patient_id, tooth_num, 'M', 'healthy')
                database.save_tooth_condition(self.patient_id, tooth_num, 'D', 'healthy')
                database.save_tooth_condition(self.patient_id, tooth_num, 'O', 'healthy')
                database.save_tooth_condition(self.patient_id, tooth_num, 'ALL', result['whole'], result['notes'])
            else:
                database.save_tooth_condition(self.patient_id, tooth_num, 'ALL', 'healthy')
                surfaces = ['B', 'L', 'M', 'D', 'O']
                for s in surfaces:
                    cond = result['surfaces'].get(s, 'healthy')
                    database.save_tooth_condition(self.patient_id, tooth_num, s, cond, result['notes'] if s == 'O' else "")
            
            perio = result['perio']
            database.save_perio_status(
                self.patient_id, tooth_num, 
                perio['pd_facial'], perio['pd_lingual'], 
                perio['mobility'], perio['bop']
            )

            self.load_patient(self.patient_id)
            self.chart_updated.emit()
