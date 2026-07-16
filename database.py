# DentaLink Database Layer (database.py)
import os
import sqlite3
import hashlib
import hmac
from datetime import datetime
from PyQt6.QtGui import QImage, QPainter, QColor, QRadialGradient, QPen, QPainterPath, QFont
from PyQt6.QtCore import QBuffer, QIODevice, Qt

DB_NAME = "dental_clinic.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def initialize_database():
    db_exists = os.path.exists(DB_NAME)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 0. Create Clinics Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            logo_path TEXT DEFAULT ''
        );
    """)

    # Migration for clinics table
    cursor.execute("PRAGMA table_info(clinics);")
    c_cols = [c['name'] for c in cursor.fetchall()]
    if 'logo_path' not in c_cols:
        cursor.execute("ALTER TABLE clinics ADD COLUMN logo_path TEXT DEFAULT '';")
        conn.commit()

    # 0b. Create Doctors Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            discount_pct REAL DEFAULT 0.0
        );
    """)
    try:
        cursor.execute("ALTER TABLE doctors ADD COLUMN discount_pct REAL DEFAULT 0.0;")
    except sqlite3.OperationalError:
        pass

    # 1. Create Patients Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            allergies TEXT DEFAULT 'None',
            medical_conditions TEXT DEFAULT 'None',
            status TEXT DEFAULT 'NEW_OP', -- 'NEW_OP' or 'PATIENT_LIST'
            assigned_doctor_id INTEGER,
            occupation TEXT DEFAULT 'Other',
            village_town_city TEXT DEFAULT '',
            allotted_to TEXT DEFAULT '',
            validity_date TEXT DEFAULT '',
            category TEXT DEFAULT 'Regular',
            due_amt REAL DEFAULT 0.0,
            case_record_no TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assigned_doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
        );
    """)

    # Migration for patients table columns
    cursor.execute("PRAGMA table_info(patients);")
    cols = {c['name']: c['type'] for c in cursor.fetchall()}
    
    patient_columns = {
        'assigned_doctor_id': 'INTEGER REFERENCES doctors(id) ON DELETE SET NULL',
        'occupation': 'TEXT DEFAULT "Other"',
        'village_town_city': 'TEXT DEFAULT ""',
        'allotted_to': 'TEXT DEFAULT ""',
        'validity_date': 'TEXT DEFAULT ""',
        'category': 'TEXT DEFAULT "Regular"',
        'due_amt': 'REAL DEFAULT 0.0',
        'case_record_no': 'TEXT DEFAULT ""'
    }
    for col_name, col_def in patient_columns.items():
        if col_name not in cols:
            cursor.execute(f"ALTER TABLE patients ADD COLUMN {col_name} {col_def};")
            conn.commit()

    # 2. Create Case History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_history (
            patient_id INTEGER PRIMARY KEY,
            chief_complaint TEXT DEFAULT '',
            hpi TEXT DEFAULT '',
            past_dental_history TEXT DEFAULT '',
            past_medical_history TEXT DEFAULT '',
            habits TEXT DEFAULT '',
            clinical_findings TEXT DEFAULT '',
            other_chief_complaint TEXT DEFAULT '',
            family_history TEXT DEFAULT '',
            brushing_method TEXT DEFAULT 'Normal',
            brushing_frequency TEXT DEFAULT 'Once a day',
            brushing_duration TEXT DEFAULT '2 minutes',
            brushing_change_frequency TEXT DEFAULT '3 months',
            dentifrice_type TEXT DEFAULT 'Paste',
            other_dentifrice TEXT DEFAULT '',
            diet TEXT DEFAULT 'Veg',
            parafunctional_habits TEXT DEFAULT 'Absent',
            sleep TEXT DEFAULT 'Normal',
            other_personal_history TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # Migration for case_history table columns
    cursor.execute("PRAGMA table_info(case_history);")
    ch_cols = {c['name']: c['type'] for c in cursor.fetchall()}
    ch_columns = {
        'other_chief_complaint': 'TEXT DEFAULT ""',
        'family_history': 'TEXT DEFAULT ""',
        'brushing_method': 'TEXT DEFAULT "Normal"',
        'brushing_frequency': 'TEXT DEFAULT "Once a day"',
        'brushing_duration': 'TEXT DEFAULT "2 minutes"',
        'brushing_change_frequency': 'TEXT DEFAULT "3 months"',
        'dentifrice_type': 'TEXT DEFAULT "Paste"',
        'other_dentifrice': 'TEXT DEFAULT ""',
        'diet': 'TEXT DEFAULT "Veg"',
        'parafunctional_habits': 'TEXT DEFAULT "Absent"',
        'sleep': 'TEXT DEFAULT "Normal"',
        'other_personal_history': 'TEXT DEFAULT ""'
    }
    for col_name, col_def in ch_columns.items():
        if col_name not in ch_cols:
            cursor.execute(f"ALTER TABLE case_history ADD COLUMN {col_name} {col_def};")
            conn.commit()

    # Check if migration is needed for tooth_number constraint in dental_chart
    cursor.execute("PRAGMA table_info(dental_chart);")
    columns = cursor.fetchall()
    tooth_number_type = ""
    for col in columns:
        if col['name'] == 'tooth_number':
            tooth_number_type = col['type'].upper()
            break

    if tooth_number_type and 'INT' in tooth_number_type:
        # Migration is needed!
        cursor.execute("ALTER TABLE dental_chart RENAME TO dental_chart_old;")
        cursor.execute("""
            CREATE TABLE dental_chart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                tooth_number TEXT,
                surface TEXT,
                condition TEXT,
                notes TEXT DEFAULT '',
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                UNIQUE(patient_id, tooth_number, surface)
            );
        """)
        cursor.execute("""
            INSERT INTO dental_chart (id, patient_id, tooth_number, surface, condition, notes)
            SELECT id, patient_id, CAST(tooth_number AS TEXT), surface, condition, notes FROM dental_chart_old;
        """)
        cursor.execute("DROP TABLE dental_chart_old;")

        # Migrate perio_chart
        cursor.execute("ALTER TABLE perio_chart RENAME TO perio_chart_old;")
        cursor.execute("""
            CREATE TABLE perio_chart (
                patient_id INTEGER,
                tooth_number TEXT,
                pd_facial TEXT DEFAULT '',
                pd_lingual TEXT DEFAULT '',
                mobility INTEGER DEFAULT 0,
                bop BOOLEAN DEFAULT 0,
                PRIMARY KEY (patient_id, tooth_number),
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("""
            INSERT INTO perio_chart (patient_id, tooth_number, pd_facial, pd_lingual, mobility, bop)
            SELECT patient_id, CAST(tooth_number AS TEXT), pd_facial, pd_lingual, mobility, bop FROM perio_chart_old;
        """)
        cursor.execute("DROP TABLE perio_chart_old;")
        conn.commit()

    # Create tables with correct schema if they do not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dental_chart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            tooth_number TEXT,
            surface TEXT, -- 'O', 'M', 'D', 'B', 'L' or 'ALL'
            condition TEXT, -- 'decay', 'filled', 'crown', 'missing', 'implant', 'root-canal', etc.
            notes TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            UNIQUE(patient_id, tooth_number, surface)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perio_chart (
            patient_id INTEGER,
            tooth_number TEXT,
            pd_facial TEXT DEFAULT '',
            pd_lingual TEXT DEFAULT '',
            mobility INTEGER DEFAULT 0,
            bop BOOLEAN DEFAULT 0,
            PRIMARY KEY (patient_id, tooth_number),
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 4. Create X-Rays Table (BLOB storage)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS xrays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            image_type TEXT DEFAULT 'X-Ray',
            description TEXT,
            date_taken TEXT,
            image_data BLOB,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # --- NEW TABLES FOR 14-TAB CASE SHEET SYSTEM ---

    # 5. deleterious_habits
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deleterious_habits (
            patient_id INTEGER,
            habit_type TEXT, -- 'tobacco', 'alcohol', 'quid', 'others'
            is_present BOOLEAN DEFAULT 0,
            details_type TEXT DEFAULT '',
            duration TEXT DEFAULT '',
            frequency TEXT DEFAULT '',
            PRIMARY KEY (patient_id, habit_type),
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 6. extra_oral_exam
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extra_oral_exam (
            patient_id INTEGER PRIMARY KEY,
            height TEXT DEFAULT '',
            weight TEXT DEFAULT '',
            gait TEXT DEFAULT '',
            built TEXT DEFAULT '',
            nourishment TEXT DEFAULT '',
            cyanosis TEXT DEFAULT '',
            clubbing TEXT DEFAULT '',
            icterus TEXT DEFAULT '',
            oedema TEXT DEFAULT '',
            pallor TEXT DEFAULT '',
            skin TEXT DEFAULT '',
            eyes TEXT DEFAULT '',
            others_general TEXT DEFAULT '',
            bp TEXT DEFAULT '',
            pulse TEXT DEFAULT '',
            rr TEXT DEFAULT '',
            temp TEXT DEFAULT '',
            mouth_opening TEXT DEFAULT '',
            face_symmetry TEXT DEFAULT 'Symmetrical',
            salivary_glands TEXT DEFAULT 'Normal',
            tmj_deviation BOOLEAN DEFAULT 0,
            tmj_tenderness BOOLEAN DEFAULT 0,
            tmj_others TEXT DEFAULT '',
            lymph_palpable TEXT DEFAULT 'Non-palpable',
            lymph_number TEXT DEFAULT '',
            lymph_group_name TEXT DEFAULT '',
            lymph_side_name TEXT DEFAULT '',
            lymph_left_size TEXT DEFAULT '',
            lymph_left_consistency TEXT DEFAULT '',
            lymph_left_tenderness BOOLEAN DEFAULT 0,
            lymph_left_fixity TEXT DEFAULT '',
            lymph_left_others TEXT DEFAULT '',
            lymph_right_size TEXT DEFAULT '',
            lymph_right_consistency TEXT DEFAULT '',
            lymph_right_tenderness BOOLEAN DEFAULT 0,
            lymph_right_fixity TEXT DEFAULT '',
            lymph_right_others TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 7. intra_oral_exam
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intra_oral_exam (
            patient_id INTEGER PRIMARY KEY,
            occlusion_molar TEXT DEFAULT '',
            occlusion_center TEXT DEFAULT '',
            occlusion_others TEXT DEFAULT '',
            wasting_attrition TEXT DEFAULT '',
            wasting_abrasion TEXT DEFAULT '',
            wasting_erosion TEXT DEFAULT '',
            wasting_abfraction TEXT DEFAULT '',
            hypoplasia TEXT DEFAULT 'Absent',
            hypoplasia_details TEXT DEFAULT '',
            supernumerary TEXT DEFAULT 'Absent',
            supernumerary_details TEXT DEFAULT '',
            other_hard_tissue TEXT DEFAULT '',
            labial_mucosa TEXT DEFAULT 'Apparently Normal',
            labial_mucosa_details TEXT DEFAULT '',
            buccal_mucosa TEXT DEFAULT 'Apparently Normal',
            buccal_mucosa_details TEXT DEFAULT '',
            floor_mouth TEXT DEFAULT 'Apparently Normal',
            floor_mouth_details TEXT DEFAULT '',
            vestibular_mucosa TEXT DEFAULT 'Apparently Normal',
            vestibular_mucosa_details TEXT DEFAULT '',
            lingual_mucosa TEXT DEFAULT 'Apparently Normal',
            lingual_mucosa_details TEXT DEFAULT '',
            palatal_mucosa TEXT DEFAULT 'Apparently Normal',
            palatal_mucosa_details TEXT DEFAULT '',
            salivary_duct TEXT DEFAULT 'Apparently Normal',
            salivary_duct_details TEXT DEFAULT '',
            other_mucosa TEXT DEFAULT 'Apparently Normal',
            other_mucosa_details TEXT DEFAULT '',
            stain TEXT DEFAULT 'Absent',
            stain_details TEXT DEFAULT '',
            calculus TEXT DEFAULT 'Absent',
            calculus_details TEXT DEFAULT '',
            recession TEXT DEFAULT 'Absent',
            recession_details TEXT DEFAULT '',
            enlargement TEXT DEFAULT 'Absent',
            enlargement_details TEXT DEFAULT '',
            bop TEXT DEFAULT 'Absent',
            bop_details TEXT DEFAULT '',
            pockets TEXT DEFAULT 'Absent',
            pockets_details TEXT DEFAULT '',
            furcation TEXT DEFAULT 'Absent',
            furcation_details TEXT DEFAULT '',
            mucogingival TEXT DEFAULT 'Absent',
            mucogingival_details TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 8. local_examinations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS local_examinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            header TEXT DEFAULT '',
            extra_oral_inspection TEXT DEFAULT '',
            extra_oral_palpation TEXT DEFAULT '',
            soft_tissue_inspection TEXT DEFAULT '',
            soft_tissue_palpation TEXT DEFAULT '',
            hard_tissue_inspection TEXT DEFAULT '',
            hard_tissue_percussion TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 9. diagnoses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            patient_id INTEGER PRIMARY KEY,
            provisional_diagnosis TEXT DEFAULT '',
            differential_diagnosis TEXT DEFAULT '',
            note TEXT DEFAULT '',
            final_diagnosis TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 10. investigations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            service_type TEXT DEFAULT '',
            group_name TEXT DEFAULT '',
            service_name TEXT DEFAULT '',
            teeth_no TEXT DEFAULT '',
            qty INTEGER DEFAULT 1,
            rate REAL DEFAULT 0.0,
            amount REAL DEFAULT 0.0,
            disc_pct REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 11. pathology_requisitions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pathology_requisitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            category TEXT DEFAULT '', -- 'biochemistry', 'haematology', 'cytology', 'biopsy', 'microbiology'
            service_name TEXT DEFAULT '',
            teeth_no TEXT DEFAULT '',
            qty INTEGER DEFAULT 1,
            rate REAL DEFAULT 0.0,
            amount REAL DEFAULT 0.0,
            disc_pct REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 12. investigation_reports
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigation_reports (
            patient_id INTEGER PRIMARY KEY,
            radiology_reports TEXT DEFAULT '',
            pathology_reports TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 13. treatment_plans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS treatment_plans (
            patient_id INTEGER PRIMARY KEY,
            treatment_plan TEXT DEFAULT '',
            prognosis TEXT DEFAULT '',
            physician_note TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 14. prescriptions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            drug_name TEXT DEFAULT '',
            dosage TEXT DEFAULT '',
            frequency TEXT DEFAULT '',
            duration TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 15. treatments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS treatments (
            patient_id INTEGER PRIMARY KEY,
            procedure TEXT DEFAULT '',
            progress TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 16. treatments_done
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS treatments_done (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date_done TEXT DEFAULT '',
            student_name TEXT DEFAULT '',
            doctor_name TEXT DEFAULT '',
            details TEXT DEFAULT '',
            status TEXT DEFAULT 'Completed',
            treatment_needed_id INTEGER,
            doctor_notes TEXT DEFAULT '',
            treatment_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)
    try:
        cursor.execute("ALTER TABLE treatments_done ADD COLUMN treatment_needed_id INTEGER;")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE treatments_done ADD COLUMN doctor_notes TEXT DEFAULT '';")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE treatments_done ADD COLUMN treatment_status TEXT DEFAULT 'Pending';")
    except sqlite3.OperationalError:
        pass

    # 16.5 treatments_needed (billing for needed treatments)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS treatments_needed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            procedure_name TEXT DEFAULT '',
            teeth_no TEXT DEFAULT '',
            qty INTEGER DEFAULT 1,
            rate REAL DEFAULT 0.0,
            discount REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0,
            billing_status TEXT DEFAULT 'Unpaid',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 17. appointments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            app_date TEXT DEFAULT '',
            app_time TEXT DEFAULT '',
            reason TEXT DEFAULT '',
            status TEXT DEFAULT 'Yet to visit',
            visited_on TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 18. Create Referrals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            patient_id INTEGER PRIMARY KEY,
            referred_to_dept TEXT DEFAULT '',
            referred_to_doctor_id INTEGER,
            referral_reason TEXT DEFAULT '',
            referral_status TEXT DEFAULT 'Pending',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)
    # 19. Create Patient Files Table (Attachment storage)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            file_category TEXT,
            file_name TEXT,
            file_data BLOB,
            upload_date TEXT,
            file_type TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # Seed default doctor if doctors table is empty
    cursor.execute("SELECT COUNT(*) FROM doctors;")
    if cursor.fetchone()[0] == 0:
        salt = os.urandom(16).hex()
        hashed_pw = hashlib.pbkdf2_hmac('sha256', b'admin123', bytes.fromhex(salt), 100000).hex()
        cursor.execute("""
            INSERT INTO doctors (name, username, password_hash, salt)
            VALUES (?, ?, ?, ?);
        """, ("Dr. Admin", "dr_admin", hashed_pw, salt))
        conn.commit()

    # Seed default clinic if clinics table is empty
    cursor.execute("SELECT COUNT(*) FROM clinics;")
    if cursor.fetchone()[0] == 0:
        salt = os.urandom(16).hex()
        hashed_pw = hashlib.pbkdf2_hmac('sha256', b'admin123', bytes.fromhex(salt), 100000).hex()
        cursor.execute("""
            INSERT INTO clinics (name, username, password_hash, salt)
            VALUES (?, ?, ?, ?);
        """, ("Main Dental Clinic", "admin", hashed_pw, salt))
        conn.commit()

    conn.commit()

    # Seed mock data if patients table is empty
    cursor.execute("SELECT COUNT(*) FROM patients;")
    if cursor.fetchone()[0] == 0:
        seed_detailed_mock_data(conn)

    conn.close()

def generate_procedural_xray_bytes():
    """Generates a realistic grey-level dental jaw X-ray using QImage and QPainter, returning binary bytes."""
    width, height = 400, 300
    img = QImage(width, height, QImage.Format.Format_Grayscale8)
    img.fill(QColor(15, 15, 15))  # Dark background

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw simulated jaw bone (soft curved gray band)
    gradient = QRadialGradient(width / 2, height + 50, 350)
    gradient.setColorAt(0, QColor(90, 90, 90))
    gradient.setColorAt(0.6, QColor(50, 50, 50))
    gradient.setColorAt(1, QColor(15, 15, 15))
    painter.setBrush(gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(50, 80, 300, 300)

    # Draw teeth outlines (roots and crowns) in a curve
    painter.setBrush(QColor(160, 160, 160)) # Root/tooth structure
    painter.setPen(QPen(QColor(30, 30, 30), 1))
    
    teeth_x = [70, 110, 150, 190, 230, 270, 310]
    for x in teeth_x:
        # Draw tooth crown
        painter.drawRoundedRect(x, 140, 25, 30, 5, 5)
        # Draw tooth root extending down
        painter.drawEllipse(x + 5, 170, 15, 35)

    # Draw some white metal fillings (highly radio-opaque - bright white)
    painter.setBrush(QColor(245, 245, 245))
    painter.drawRect(120, 140, 10, 12) # Filling on tooth 2
    painter.drawRect(235, 140, 12, 10) # Filling on tooth 5

    # Draw dark fuzzy decay cavity (radiolucent - dark spot)
    painter.setBrush(QColor(35, 35, 35))
    painter.setPen(QPen(QColor(50, 50, 50), 1))
    painter.drawEllipse(192, 148, 8, 8) # Cavity on tooth 4

    # Draw dental crown (distinct metallic shape)
    painter.setBrush(QColor(220, 220, 220))
    painter.drawRoundedRect(270, 136, 25, 34, 3, 3)

    painter.end()

    # Convert QImage to bytes (PNG format)
    ba = QBuffer()
    ba.open(QBuffer.OpenModeFlag.WriteOnly)
    img.save(ba, "PNG")
    return ba.data().data()

def generate_procedural_intraoral_photo_bytes(has_decay=False, has_inflamed_gums=False):
    """Generates a realistic color intraoral tooth/gum photo using QImage and QPainter, returning binary bytes."""
    width, height = 400, 300
    img = QImage(width, height, QImage.Format.Format_ARGB32)
    # Fill gums color: light pink (#FFC0CB) or inflamed red-pink (#E65C5C)
    gum_color = QColor(230, 92, 92) if has_inflamed_gums else QColor(255, 180, 185)
    img.fill(gum_color)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw dark mouth opening/shadow
    painter.setBrush(QColor(40, 10, 15))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(50, 90, 300, 120)

    # Draw teeth in a curve
    teeth_x = [75, 115, 155, 195, 235, 275, 315]
    for i, x in enumerate(teeth_x):
        # Teeth color: slightly ivory/warm white
        painter.setBrush(QColor(250, 248, 235))
        painter.setPen(QPen(QColor(180, 175, 160), 1))
        # Draw tooth crown
        painter.drawRoundedRect(x, 110, 28, 35, 6, 6)

        # Draw details like shading
        painter.setBrush(QColor(235, 230, 210))
        painter.drawEllipse(x + 4, 132, 20, 10)

    # If has_decay, draw a realistic brown/black decay spot on tooth 4 (x = 195)
    if has_decay:
        painter.setBrush(QColor(65, 35, 15)) # Dark brown decay
        painter.setPen(QPen(QColor(40, 20, 10), 1))
        painter.drawEllipse(204, 122, 10, 12)
        # Inner black spot
        painter.setBrush(QColor(10, 5, 0))
        painter.drawEllipse(206, 124, 6, 8)

    painter.end()

    ba = QBuffer()
    ba.open(QBuffer.OpenModeFlag.WriteOnly)
    img.save(ba, "PNG")
    return ba.data().data()

def generate_procedural_extraoral_photo_bytes():
    """Generates a realistic color extraoral smiling photo using QImage and QPainter, returning binary bytes."""
    width, height = 400, 300
    img = QImage(width, height, QImage.Format.Format_ARGB32)
    img.fill(QColor(240, 240, 245)) # Soft background

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw face outline (skin tone)
    painter.setBrush(QColor(245, 215, 190))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(80, 20, 240, 260)

    # Draw red lips outline
    painter.setBrush(QColor(210, 60, 80))
    painter.drawEllipse(130, 150, 140, 60)

    # Draw smiling mouth opening (dark)
    painter.setBrush(QColor(50, 10, 15))
    painter.drawEllipse(140, 160, 120, 40)

    # Draw upper teeth smiling
    painter.setBrush(QColor(255, 255, 255))
    teeth_x = [152, 166, 180, 194, 208, 222, 236]
    for x in teeth_x:
        painter.drawRoundedRect(x, 160, 12, 16, 2, 2)

    painter.end()

    ba = QBuffer()
    ba.open(QBuffer.OpenModeFlag.WriteOnly)
    img.save(ba, "PNG")
    return ba.data().data()

def generate_procedural_opg_fracture_bytes():
    """Generates a realistic panoramic dental X-ray (OPG) showing a mandibular parasymphysis fracture."""
    width, height = 500, 250
    img = QImage(width, height, QImage.Format.Format_Grayscale8)
    img.fill(QColor(10, 10, 10))  # Dark background

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw panoramic jaw bone (large curved band representing mandible)
    path = QPainterPath()
    path.moveTo(60, 60)
    path.quadTo(width / 2, height + 40, width - 60, 60)
    
    pen = QPen(QColor(95, 95, 95), 45)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawPath(path)

    # Draw step deformity/fracture line in the mandible around right parasymphysis (x = 180-200)
    painter.setPen(QPen(QColor(10, 10, 10), 4))
    painter.drawLine(185, 120, 195, 195) # Fracture line through mandible body
    
    # Draw teeth in a panoramic curve along the jaw path
    painter.setPen(QPen(QColor(30, 30, 30), 1))
    
    # Left teeth
    for i in range(10):
        t_x = 70 + i * 14
        dx = (t_x - 250) / 190.0
        t_y = 175 - 110 * (1.0 - dx*dx)
        
        painter.setBrush(QColor(175, 175, 175))
        painter.drawRoundedRect(t_x, int(t_y), 11, 14, 2, 2)
        painter.setBrush(QColor(140, 140, 140))
        painter.drawEllipse(t_x + 2, int(t_y) + 14, 7, 18)

    # Right teeth (with displacement step around x = 200)
    for i in range(10):
        t_x = 210 + i * 14
        dx = (t_x - 250) / 190.0
        t_y = 175 - 110 * (1.0 - dx*dx)
        
        # Displacement step - offset slightly upwards on the right side
        t_y -= 8 
        
        painter.setBrush(QColor(175, 175, 175))
        painter.drawRoundedRect(t_x, int(t_y), 11, 14, 2, 2)
        painter.setBrush(QColor(140, 140, 140))
        painter.drawEllipse(t_x + 2, int(t_y) + 14, 7, 18)

    # Draw dark fracture gap between roots (between #26 and #27)
    painter.setBrush(QColor(10, 10, 10))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(185, 130, 8, 25)

    # Label on OPG
    painter.setPen(QColor(200, 200, 200))
    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    painter.drawText(20, 30, "L")
    painter.drawText(width - 30, 30, "R")
    painter.drawText(20, height - 20, "PANORAMIC OPG")

    painter.end()

    ba = QBuffer()
    ba.open(QBuffer.OpenModeFlag.WriteOnly)
    img.save(ba, "PNG")
    return ba.data().data()

def seed_detailed_mock_data(conn):
    cursor = conn.cursor()

    # 1. Patients Table
    cursor.execute("""
        INSERT INTO patients (name, dob, gender, phone, email, address, allergies, medical_conditions, status, assigned_doctor_id, occupation, village_town_city, allotted_to, validity_date, category, case_record_no)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, ("Arthur Dent", "1984-05-15", "Male", "(555) 012-3456", "adent@hitchhiker.co.uk", "Country Lane, Cottington", "Penicillin", "Mild Asthma", "PATIENT_LIST", 1, "Reporter", "Cottington", "Dr. Admin", "2027-07-15", "Regular", "CRN-2026-0001"))
    arthur_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO patients (name, dob, gender, phone, email, address, allergies, medical_conditions, status, assigned_doctor_id, occupation, village_town_city, allotted_to, validity_date, category, case_record_no)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, ("Hermione Granger", "1998-09-19", "Female", "(555) 987-6543", "hgranger@ministry.magic", "Flat 4B, Diagon Alley", "Latex", "Pregnancy (2nd Trimester)", "NEW_OP", 1, "Researcher", "London", "Dr. Admin", "2027-07-15", "Regular", "CRN-2026-0002"))
    hermione_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO patients (name, dob, gender, phone, email, address, allergies, medical_conditions, status, assigned_doctor_id, occupation, village_town_city, allotted_to, validity_date, category, case_record_no)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, ("John Watson", "1990-07-07", "Male", "(555) 321-7654", "jwatson@bakerstreet.com", "221B Baker St, London", "None", "PTSD, gunshot scar in left shoulder", "PATIENT_LIST", 1, "Medical Writer", "London", "Dr. Admin", "2027-07-15", "Regular", "CRN-2026-0003"))
    john_id = cursor.lastrowid

    # 2. Case History Table
    cursor.execute("""
        INSERT INTO case_history (patient_id, chief_complaint, hpi, past_dental_history, past_medical_history, habits, clinical_findings, other_chief_complaint, family_history, brushing_method, brushing_frequency, brushing_duration, brushing_change_frequency, dentifrice_type, other_dentifrice, diet, parafunctional_habits, sleep, other_personal_history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (arthur_id,
          "Severe pain in lower right back tooth for the past 3 days.",
          "Pain started as a dull ache 2 weeks ago, became sharp, throbbing, and continuous 3 days ago. Disturbs sleep. Relieved temporarily by ibuprofen.",
          "Regular scaling and simple composite fillings 2 years ago.",
          "Mild asthma, uses albuterol inhaler. Stable.",
          "Brushing once daily with paste, normal diet, no parafunctional habits.",
          "Deep distal-occlusal caries on tooth #30, extremely tender to percussion.",
          "", "No history of diabetes or cardiac disorders in family.",
          "Normal", "Once a day", "2 minutes", "3 months", "Paste", "", "Veg", "Absent", "Normal", ""))

    cursor.execute("""
        INSERT INTO case_history (patient_id, chief_complaint, hpi, past_dental_history, past_medical_history, habits, clinical_findings, other_chief_complaint, family_history, brushing_method, brushing_frequency, brushing_duration, brushing_change_frequency, dentifrice_type, other_dentifrice, diet, parafunctional_habits, sleep, other_personal_history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (hermione_id,
          "Bleeding from gums during brushing and mild swelling for the past month.",
          "Generalized bleeding from gums during brushing and eating hard foods. Gums feel swollen and tender.",
          "Scaling and polishing done 6 months ago.",
          "Currently 18 weeks pregnant. Obstetrician cleared for routine dental prophylaxis.",
          "Brushing twice daily, veg diet, no parafunctional habits.",
          "Generalized moderate calculus, marginal gingival redness and swelling, bleeding on probing.",
          "", "No significant family medical history.",
          "Normal", "Twice a day", "2 minutes", "3 months", "Paste", "", "Veg", "Absent", "Normal", ""))

    cursor.execute("""
        INSERT INTO case_history (patient_id, chief_complaint, hpi, past_dental_history, past_medical_history, habits, clinical_findings, other_chief_complaint, family_history, brushing_method, brushing_frequency, brushing_duration, brushing_change_frequency, dentifrice_type, other_dentifrice, diet, parafunctional_habits, sleep, other_personal_history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (john_id,
          "Severe pain, swelling, and inability to close teeth properly after a fall yesterday.",
          "Patient fell face-first yesterday evening following an assault. Immediate severe pain in the lower anterior jaw, swelling, and intraoral bleeding. Noticed upper and lower teeth do not align properly.",
          "Routine extractions under local anesthesia years ago.",
          "History of stable PTSD. Gunshot wound to left shoulder (healed, stable).",
          "Brushing once daily, mixed diet, no parafunctional habits.",
          "Gingival laceration and sublingual hematoma near right lower canine. Step deformity in dental arch between #26 and #27. Anterior open bite.",
          "", "No family history of bleeding disorders.",
          "Normal", "Once a day", "2 minutes", "3 months", "Paste", "", "Mixed", "Absent", "Normal", ""))

    # 3. Deleterious Habits Table
    for pid in [arthur_id, hermione_id, john_id]:
        for htype in ['tobacco', 'alcohol', 'quid', 'others']:
            cursor.execute("""
                INSERT INTO deleterious_habits (patient_id, habit_type, is_present, details_type, duration, frequency)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (pid, htype, 0, "", "", ""))

    # 4. Extra-Oral Exam Table
    cursor.execute("""
        INSERT INTO extra_oral_exam (patient_id, height, weight, gait, built, nourishment, cyanosis, clubbing, icterus, oedema, pallor, skin, eyes, others_general, bp, pulse, rr, temp, mouth_opening, face_symmetry, salivary_glands, tmj_deviation, tmj_tenderness, tmj_others, lymph_palpable, lymph_number, lymph_group_name, lymph_side_name, lymph_left_size, lymph_left_consistency, lymph_left_tenderness, lymph_left_fixity, lymph_left_others, lymph_right_size, lymph_right_consistency, lymph_right_tenderness, lymph_right_fixity, lymph_right_others)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (arthur_id, "178 cm", "74 kg", "Normal", "Average", "Good", "Absent", "Absent", "Absent", "Absent", "Absent", "Normal", "Normal", "", "120/80 mmHg", "72 bpm", "16 cpm", "98.6 F", "40 mm", "Symmetrical", "Normal", 0, 0, "", "Non-palpable", "", "", "", "", "", 0, "", "", "", "", 0, "", ""))

    cursor.execute("""
        INSERT INTO extra_oral_exam (patient_id, height, weight, gait, built, nourishment, cyanosis, clubbing, icterus, oedema, pallor, skin, eyes, others_general, bp, pulse, rr, temp, mouth_opening, face_symmetry, salivary_glands, tmj_deviation, tmj_tenderness, tmj_others, lymph_palpable, lymph_number, lymph_group_name, lymph_side_name, lymph_left_size, lymph_left_consistency, lymph_left_tenderness, lymph_left_fixity, lymph_left_others, lymph_right_size, lymph_right_consistency, lymph_right_tenderness, lymph_right_fixity, lymph_right_others)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (hermione_id, "165 cm", "62 kg", "Normal", "Average", "Good", "Absent", "Absent", "Absent", "Absent", "Absent", "Normal", "Normal", "", "115/75 mmHg", "68 bpm", "18 cpm", "98.4 F", "42 mm", "Symmetrical", "Normal", 0, 0, "", "Non-palpable", "", "", "", "", "", 0, "", "", "", "", 0, "", ""))

    cursor.execute("""
        INSERT INTO extra_oral_exam (patient_id, height, weight, gait, built, nourishment, cyanosis, clubbing, icterus, oedema, pallor, skin, eyes, others_general, bp, pulse, rr, temp, mouth_opening, face_symmetry, salivary_glands, tmj_deviation, tmj_tenderness, tmj_others, lymph_palpable, lymph_number, lymph_group_name, lymph_side_name, lymph_left_size, lymph_left_consistency, lymph_left_tenderness, lymph_left_fixity, lymph_left_others, lymph_right_size, lymph_right_consistency, lymph_right_tenderness, lymph_right_fixity, lymph_right_others)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (john_id, "175 cm", "78 kg", "Normal", "Average", "Good", "Absent", "Absent", "Absent", "Absent", "Absent", "Normal", "Normal", "", "130/85 mmHg", "80 bpm", "18 cpm", "98.6 F", "20 mm (Trismus due to pain)", "Asymmetrical (swelling over right chin)", "Normal", 1, 1, "Mandibular movement severely restricted by pain", "Palpable", "2", "Submandibular", "Right", "", "", 0, "", "", "1.5cm", "Firm", 1, "Fixed", "Tender on palpation"))

    # 5. Intra-Oral Exam Table
    cursor.execute("""
        INSERT INTO intra_oral_exam (patient_id, occlusion_molar, occlusion_center, occlusion_others, wasting_attrition, wasting_abrasion, wasting_erosion, wasting_abfraction, hypoplasia, hypoplasia_details, supernumerary, supernumerary_details, other_hard_tissue, labial_mucosa, labial_mucosa_details, buccal_mucosa, buccal_mucosa_details, floor_mouth, floor_mouth_details, vestibular_mucosa, vestibular_mucosa_details, lingual_mucosa, lingual_mucosa_details, palatal_mucosa, palatal_mucosa_details, salivary_duct, salivary_duct_details, other_mucosa, other_mucosa_details, stain, stain_details, calculus, calculus_details, recession, recession_details, enlargement, enlargement_details, bop, bop_details, pockets, pockets_details, furcation, furcation_details, mucogingival, mucogingival_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (arthur_id, "Class I", "Coincident", "", "Absent", "Absent", "Absent", "Absent", "Absent", "", "Absent", "", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Absent", "", "Present", "Mild supragingival calculus on lower anteriors", "Absent", "", "Absent", "", "Absent", "", "Absent", "", "Absent", "", "Absent", ""))

    cursor.execute("""
        INSERT INTO intra_oral_exam (patient_id, occlusion_molar, occlusion_center, occlusion_others, wasting_attrition, wasting_abrasion, wasting_erosion, wasting_abfraction, hypoplasia, hypoplasia_details, supernumerary, supernumerary_details, other_hard_tissue, labial_mucosa, labial_mucosa_details, buccal_mucosa, buccal_mucosa_details, floor_mouth, floor_mouth_details, vestibular_mucosa, vestibular_mucosa_details, lingual_mucosa, lingual_mucosa_details, palatal_mucosa, palatal_mucosa_details, salivary_duct, salivary_duct_details, other_mucosa, other_mucosa_details, stain, stain_details, calculus, calculus_details, recession, recession_details, enlargement, enlargement_details, bop, bop_details, pockets, pockets_details, furcation, furcation_details, mucogingival, mucogingival_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (hermione_id, "Class I", "Coincident", "", "Absent", "Absent", "Absent", "Absent", "Absent", "", "Absent", "", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Present", "Mild extrinsic stains", "Present", "Generalized moderate supragingival and subgingival calculus", "Present", "Mild localized recession (1mm) on lower anteriors", "Present", "Mild gingival enlargement on marginal gums", "Present", "Generalized BOP during periodontal examination", "Absent", "", "Absent", "", "Absent", ""))

    cursor.execute("""
        INSERT INTO intra_oral_exam (patient_id, occlusion_molar, occlusion_center, occlusion_others, wasting_attrition, wasting_abrasion, wasting_erosion, wasting_abfraction, hypoplasia, hypoplasia_details, supernumerary, supernumerary_details, other_hard_tissue, labial_mucosa, labial_mucosa_details, buccal_mucosa, buccal_mucosa_details, floor_mouth, floor_mouth_details, vestibular_mucosa, vestibular_mucosa_details, lingual_mucosa, lingual_mucosa_details, palatal_mucosa, palatal_mucosa_details, salivary_duct, salivary_duct_details, other_mucosa, other_mucosa_details, stain, stain_details, calculus, calculus_details, recession, recession_details, enlargement, enlargement_details, bop, bop_details, pockets, pockets_details, furcation, furcation_details, mucogingival, mucogingival_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (john_id, "Deranged", "Shifted to right by 3mm", "Anterior open bite, severe malocclusion", "Absent", "Absent", "Absent", "Absent", "Absent", "", "Absent", "", "", "Apparently Normal", "", "Apparently Normal", "", "Present", "Sublingual hematoma in the right anterior floor of mouth", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Apparently Normal", "", "Absent", "", "Absent", "", "Absent", "", "Absent", "", "Present", "Active bleeding from gingival tear at #26-27 site", "Absent", "", "Absent", "", "Absent", ""))

    # 6. Local Examinations Table
    cursor.execute("""
        INSERT INTO local_examinations (patient_id, header, extra_oral_inspection, extra_oral_palpation, soft_tissue_inspection, soft_tissue_palpation, hard_tissue_inspection, hard_tissue_percussion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (arthur_id, "Right Mandibular Quadrant Examination", "No external swelling or asymmetry noted.", "No lymph nodes palpable, TMJ movements smooth.", "Mild localized redness of free gingival margin on tooth #30.", "Gingiva is soft, slightly tender on pressure.", "Deep disto-occlusal carious lesion on #30.", "Extremely tender to vertical percussion."))

    cursor.execute("""
        INSERT INTO local_examinations (patient_id, header, extra_oral_inspection, extra_oral_palpation, soft_tissue_inspection, soft_tissue_palpation, hard_tissue_inspection, hard_tissue_percussion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (hermione_id, "Generalized Periodontal Assessment", "No extraoral swellings, normal lymph node exam.", "No TMJ tenderness or muscle tenderness.", "Generalized marginal gingival enlargement, deep pink/red color.", "Gingiva soft, edematous, bleeds easily on touch.", "Moderate calculus deposits present on all teeth.", "No tenderness to percussion on any teeth."))

    cursor.execute("""
        INSERT INTO local_examinations (patient_id, header, extra_oral_inspection, extra_oral_palpation, soft_tissue_inspection, soft_tissue_palpation, hard_tissue_inspection, hard_tissue_percussion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (john_id, "Symphysis/Parasymphysis Fracture Site", "Swelling and ecchymosis over the right parasymphysis body region.", "Tenderness on palpation of right lower border of mandible; step felt.", "Tear in the labial sulcus mucosa between #26 and #27. Sublingual hematoma.", "Tenderness on palpation, bleeding on manipulation.", "Visible step deformity in occlusion between #26 and #27.", "Extremely tender to percussion on #26 and #27."))

    # 7. Diagnoses Table
    cursor.execute("""
        INSERT INTO diagnoses (patient_id, provisional_diagnosis, differential_diagnosis, note, final_diagnosis)
        VALUES (?, ?, ?, ?, ?);
    """, (arthur_id, "Symptomatic Irreversible Pulpitis #30", "Reversible Pulpitis, Acute Apical Abscess", "Confirm with IOPA x-ray.", "Symptomatic Irreversible Pulpitis with Symptomatic Apical Periodontitis #30"))

    cursor.execute("""
        INSERT INTO diagnoses (patient_id, provisional_diagnosis, differential_diagnosis, note, final_diagnosis)
        VALUES (?, ?, ?, ?, ?);
    """, (hermione_id, "Pregnancy-Induced Gingivitis", "Plaque-Induced Chronic Gingivitis", "Patient is in 2nd trimester.", "Pregnancy Gingivitis"))

    cursor.execute("""
        INSERT INTO diagnoses (patient_id, provisional_diagnosis, differential_diagnosis, note, final_diagnosis)
        VALUES (?, ?, ?, ?, ?);
    """, (john_id, "Right Mandibular Parasymphysis Fracture", "Mandibular Symphysis Fracture, Right Condyle Fracture", "Urgent OPG and CT Mandible ordered.", "Displaced Right Mandibular Parasymphysis Fracture with associated malocclusion and gingival laceration"))

    # 8. Investigations Table
    cursor.execute("""
        INSERT INTO investigations (patient_id, service_type, group_name, service_name, teeth_no, qty, rate, amount, disc_pct, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (arthur_id, "Radiology", "IOPA", "Intraoral Periapical X-Ray #30", "30", 1, 150.0, 150.0, 0.0, 150.0, "Completed"))

    cursor.execute("""
        INSERT INTO investigations (patient_id, service_type, group_name, service_name, teeth_no, qty, rate, amount, disc_pct, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (john_id, "Radiology", "OPG", "Orthopantomogram (OPG) Panoramic X-Ray", "Mandible", 1, 500.0, 500.0, 0.0, 500.0, "Completed"))

    # 9. Pathology Requisitions Table
    cursor.execute("""
        INSERT INTO pathology_requisitions (patient_id, category, service_name, teeth_no, qty, rate, amount, disc_pct, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (hermione_id, "haematology", "Complete Blood Count (CBC)", "", 1, 250.0, 250.0, 0.0, 250.0))

    cursor.execute("""
        INSERT INTO pathology_requisitions (patient_id, category, service_name, teeth_no, qty, rate, amount, disc_pct, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (john_id, "haematology", "Routine Pre-op Profile (CBC, BT, CT, HIV, HBsAg)", "", 1, 1200.0, 1200.0, 0.0, 1200.0))

    # 10. Investigation Reports Table
    cursor.execute("""
        INSERT INTO investigation_reports (patient_id, radiology_reports, pathology_reports)
        VALUES (?, ?, ?);
    """, (arthur_id, "IOPA of #30 shows deep carious radiolucency involving the pulp chamber. Periodontal ligament space widening at the mesial and distal root apices.", ""))

    cursor.execute("""
        INSERT INTO investigation_reports (patient_id, radiology_reports, pathology_reports)
        VALUES (?, ?, ?);
    """, (hermione_id, "No radiographs taken due to pregnancy.", "CBC report: Hb 11.5 g/dl, Platelets 2.2L, WBC 7,800. All values within normal range for pregnancy."))

    cursor.execute("""
        INSERT INTO investigation_reports (patient_id, radiology_reports, pathology_reports)
        VALUES (?, ?, ?);
    """, (john_id, "OPG OPG Mandible: A radiolucent line is noted traversing the right mandibular parasymphysis region between the roots of #26 and #27. Bony segments show displacement (step deformity of 3mm). No condyle or angle fractures seen.", "Pre-op Profile: Hb 14.2 g/dl, BT 2m 10s, CT 4m 30s. HIV/HBsAg Non-reactive. All parameters within normal limits for GA."))

    # 11. Treatment Plans Table
    cursor.execute("""
        INSERT INTO treatment_plans (patient_id, treatment_plan, prognosis, physician_note)
        VALUES (?, ?, ?, ?);
    """, (arthur_id, "1. Root Canal Therapy (RCT) for #30. 2. Post & Core build-up. 3. Full coverage PFM Crown on #30.", "Good", "Patient is stable, asthma well controlled."))

    cursor.execute("""
        INSERT INTO treatment_plans (patient_id, treatment_plan, prognosis, physician_note)
        VALUES (?, ?, ?, ?);
    """, (hermione_id, "1. Full mouth scaling and root planing. 2. Oral hygiene instructions. 3. Re-evaluation in 4 weeks.", "Excellent", "Cleared by Obstetrician. Avoid NSAIDs."))

    cursor.execute("""
        INSERT INTO treatment_plans (patient_id, treatment_plan, prognosis, physician_note)
        VALUES (?, ?, ?, ?);
    """, (john_id, "1. Open Reduction and Internal Fixation (ORIF) of Mandibular Parasymphysis Fracture under GA. 2. Placement of two 2.0 mm miniplates and screws. 3. Soft diet for 6 weeks.", "Good", "Psychiatry clearance for GA obtained (PTSD stable). Cleared for surgery."))

    # 12. Prescriptions Table
    cursor.execute("""
        INSERT INTO prescriptions (patient_id, drug_name, dosage, frequency, duration)
        VALUES (?, ?, ?, ?, ?);
    """, (arthur_id, "Amoxicillin 500mg", "1 capsule", "Three times a day", "5 days"))
    cursor.execute("""
        INSERT INTO prescriptions (patient_id, drug_name, dosage, frequency, duration)
        VALUES (?, ?, ?, ?, ?);
    """, (arthur_id, "Ibuprofen 400mg", "1 tablet", "Three times a day (PRN)", "3 days"))

    cursor.execute("""
        INSERT INTO prescriptions (patient_id, drug_name, dosage, frequency, duration)
        VALUES (?, ?, ?, ?, ?);
    """, (hermione_id, "Chlorhexidine 0.2% Mouthwash", "10 ml rinse", "Twice a day", "14 days"))

    cursor.execute("""
        INSERT INTO prescriptions (patient_id, drug_name, dosage, frequency, duration)
        VALUES (?, ?, ?, ?, ?);
    """, (john_id, "Amoxicillin + Clavulanic Acid 625mg", "1 tablet", "Twice a day", "7 days"))
    cursor.execute("""
        INSERT INTO prescriptions (patient_id, drug_name, dosage, frequency, duration)
        VALUES (?, ?, ?, ?, ?);
    """, (john_id, "Tramadol 50mg + Paracetamol 325mg", "1 tablet", "Three times a day", "5 days"))
    cursor.execute("""
        INSERT INTO prescriptions (patient_id, drug_name, dosage, frequency, duration)
        VALUES (?, ?, ?, ?, ?);
    """, (john_id, "Betadine Mouthwash 2%", "10 ml rinse", "Three times a day", "7 days"))

    # 13. Treatments Table
    cursor.execute("""
        INSERT INTO treatments (patient_id, procedure, progress)
        VALUES (?, ?, ?);
    """, (arthur_id, "Root Canal Therapy", "Access cavity prepared, working length determined, canals clean and shaped."))

    cursor.execute("""
        INSERT INTO treatments (patient_id, procedure, progress)
        VALUES (?, ?, ?);
    """, (hermione_id, "Scaling & Polishing", "Full-mouth scaling completed. Oral hygiene demonstrated."))

    cursor.execute("""
        INSERT INTO treatments (patient_id, procedure, progress)
        VALUES (?, ?, ?);
    """, (john_id, "ORIF Mandible", "Surgical ORIF completed under General Anesthesia. Postop recovery uneventful."))

    # 14. Treatments Needed Table (Billing & planned procedures)
    cursor.execute("""
        INSERT INTO treatments_needed (patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (arthur_id, "Root Canal Treatment", "30", 1, 4500.0, 0.0, 4500.0, "Unpaid"))
    arthur_need_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO treatments_needed (patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (arthur_id, "PFM Crown", "30", 1, 3500.0, 0.0, 3500.0, "Unpaid"))

    cursor.execute("""
        INSERT INTO treatments_needed (patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (hermione_id, "Scaling and Polishing", "Generalized", 1, 1200.0, 100.0, 1100.0, "Paid"))
    hermione_need_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO treatments_needed (patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (john_id, "ORIF Mandible Fracture (Under GA)", "Mandible", 1, 45000.0, 0.0, 45000.0, "Paid"))
    john_need_id = cursor.lastrowid

    # 15. Treatments Done Table
    cursor.execute("""
        INSERT INTO treatments_done (patient_id, date_done, student_name, doctor_name, details, status, treatment_needed_id, doctor_notes, treatment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (arthur_id, "2026-07-14", "Dr. Student", "Dr. Admin", "Access opening, extirpation of pulp, canals irrigated and dried. Temporary Cavit dressing placed.", "Completed", arthur_need_id, "Canals very narrow, require caution. Patient tolerated procedure well.", "Completed"))

    cursor.execute("""
        INSERT INTO treatments_done (patient_id, date_done, student_name, doctor_name, details, status, treatment_needed_id, doctor_notes, treatment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (hermione_id, "2026-07-14", "Dr. Student", "Dr. Admin", "Full mouth ultrasonic scaling completed, polished with pumice paste.", "Completed", hermione_need_id, "Patient comfortable, minimal bleeding during scaling.", "Completed"))

    cursor.execute("""
        INSERT INTO treatments_done (patient_id, date_done, student_name, doctor_name, details, status, treatment_needed_id, doctor_notes, treatment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (john_id, "2026-07-14", "Dr. Student", "Dr. Admin", 
          "ORIF of Mandibular Parasymphysis Fracture under GA. Standard intraoral vestibular incision made from #24 to #29. Fracture exposed, reduced to normal occlusion, and fixed using two 2.0 mm titanium miniplates and screws. Hemostasis achieved. Copious irrigation. Wound closed in layers with 3-0 Vicryl.", 
          "Completed", john_need_id, 
          "POST-OP NOTES: Patient extubated successfully. Checked occlusion; matches preoperative centric relation. Liquid diet for 2 weeks. Ceftriaxone and Metronidazole IV post-op. Strict mouth rinses with Betadine. Review in 1 week for suture check.", 
          "Completed"))

    # 16. Appointments Table
    cursor.execute("""
        INSERT INTO appointments (patient_id, app_date, app_time, reason, status)
        VALUES (?, ?, ?, ?, ?);
    """, (arthur_id, "2026-07-17", "10:00 AM", "Obturation & Permanent filling #30", "Yet to visit"))

    cursor.execute("""
        INSERT INTO appointments (patient_id, app_date, app_time, reason, status)
        VALUES (?, ?, ?, ?, ?);
    """, (hermione_id, "2026-08-14", "11:30 AM", "Periodontal review & plaque index", "Yet to visit"))

    cursor.execute("""
        INSERT INTO appointments (patient_id, app_date, app_time, reason, status)
        VALUES (?, ?, ?, ?, ?);
    """, (john_id, "2026-07-21", "09:30 AM", "Post-op review, suture removal, occlusion check", "Yet to visit"))

    # 17. Referrals Table
    cursor.execute("""
        INSERT INTO referrals (patient_id, referred_to_dept, referred_to_doctor_id, referral_reason, referral_status)
        VALUES (?, ?, ?, ?, ?);
    """, (arthur_id, "Prosthodontics", 1, "PFM crown evaluation post-obturation.", "Pending"))

    # 18. Dental Chart Table
    cursor.execute("INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes) VALUES (?, ?, ?, ?, ?);", (arthur_id, '30', 'O', 'decay', 'Deep disto-occlusal decay'))
    cursor.execute("INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes) VALUES (?, ?, ?, ?, ?);", (arthur_id, '30', 'D', 'decay', 'Approaching pulp'))
    cursor.execute("INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes) VALUES (?, ?, ?, ?, ?);", (arthur_id, '3', 'O', 'filled', 'Composite filling in good condition'))
    cursor.execute("INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes) VALUES (?, ?, ?, ?, ?);", (arthur_id, '19', 'ALL', 'crown', 'Existing porcelain crown'))

    cursor.execute("INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes) VALUES (?, ?, ?, ?, ?);", (hermione_id, '14', 'O', 'filled', 'Restoration intact'))
    cursor.execute("INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes) VALUES (?, ?, ?, ?, ?);", (hermione_id, '19', 'O', 'decay', 'Superficial enamel decay'))

    cursor.execute("INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes) VALUES (?, ?, ?, ?, ?);", (john_id, '26', 'ALL', 'decay', 'Mobile segment tooth'))
    cursor.execute("INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes) VALUES (?, ?, ?, ?, ?);", (john_id, '27', 'ALL', 'decay', 'Mobile segment tooth'))

    # 19. Perio Chart Table
    cursor.execute("INSERT INTO perio_chart (patient_id, tooth_number, pd_facial, pd_lingual, mobility, bop) VALUES (?, ?, ?, ?, ?, ?);", (arthur_id, '30', '3 2 3', '3 2 3', 0, 0))

    cursor.execute("INSERT INTO perio_chart (patient_id, tooth_number, pd_facial, pd_lingual, mobility, bop) VALUES (?, ?, ?, ?, ?, ?);", (hermione_id, '3', '3 3 4', '3 3 4', 0, 1))
    cursor.execute("INSERT INTO perio_chart (patient_id, tooth_number, pd_facial, pd_lingual, mobility, bop) VALUES (?, ?, ?, ?, ?, ?);", (hermione_id, '14', '3 2 3', '3 3 3', 0, 1))

    cursor.execute("INSERT INTO perio_chart (patient_id, tooth_number, pd_facial, pd_lingual, mobility, bop) VALUES (?, ?, ?, ?, ?, ?);", (john_id, '26', '3 3 3', '3 3 3', 2, 1))
    cursor.execute("INSERT INTO perio_chart (patient_id, tooth_number, pd_facial, pd_lingual, mobility, bop) VALUES (?, ?, ?, ?, ?, ?);", (john_id, '27', '3 3 3', '3 3 3', 2, 1))

    # 20. X-Rays / Photographs (BLOB storage)
    xray_bytes = generate_procedural_xray_bytes()
    opg_bytes = generate_procedural_opg_fracture_bytes()
    intraoral_photo_decay_bytes = generate_procedural_intraoral_photo_bytes(has_decay=True, has_inflamed_gums=False)
    intraoral_photo_gums_bytes = generate_procedural_intraoral_photo_bytes(has_decay=False, has_inflamed_gums=True)
    extraoral_photo_bytes = generate_procedural_extraoral_photo_bytes()

    # Arthur Dent: 1 X-Ray, 1 Intraoral Photo
    cursor.execute("""
        INSERT INTO xrays (patient_id, image_type, description, date_taken, image_data)
        VALUES (?, ?, ?, ?, ?);
    """, (arthur_id, "X-Ray", "IOPA of #30 showing deep disto-occlusal decay.", "2026-07-14", sqlite3.Binary(xray_bytes)))

    cursor.execute("""
        INSERT INTO xrays (patient_id, image_type, description, date_taken, image_data)
        VALUES (?, ?, ?, ?, ?);
    """, (arthur_id, "Intraoral Photo", "Clinical photograph of lower right quadrant showing carious lesion on #30.", "2026-07-14", sqlite3.Binary(intraoral_photo_decay_bytes)))

    # Hermione Granger: 1 Intraoral Photo, 1 Extraoral Photo
    cursor.execute("""
        INSERT INTO xrays (patient_id, image_type, description, date_taken, image_data)
        VALUES (?, ?, ?, ?, ?);
    """, (hermione_id, "Intraoral Photo", "Clinical photograph showing generalized gingival inflammation and calculus deposits.", "2026-07-14", sqlite3.Binary(intraoral_photo_gums_bytes)))

    cursor.execute("""
        INSERT INTO xrays (patient_id, image_type, description, date_taken, image_data)
        VALUES (?, ?, ?, ?, ?);
    """, (hermione_id, "Extraoral Photo", "Pre-treatment frontal smile aesthetic photograph.", "2026-07-14", sqlite3.Binary(extraoral_photo_bytes)))

    # John Watson: 1 OPG, 1 Extraoral Photo
    cursor.execute("""
        INSERT INTO xrays (patient_id, image_type, description, date_taken, image_data)
        VALUES (?, ?, ?, ?, ?);
    """, (john_id, "X-Ray", "OPG Mandible showing parasymphysis fracture between roots of #26 and #27.", "2026-07-14", sqlite3.Binary(opg_bytes)))

    cursor.execute("""
        INSERT INTO xrays (patient_id, image_type, description, date_taken, image_data)
        VALUES (?, ?, ?, ?, ?);
    """, (john_id, "Extraoral Photo", "Clinical facial view showing right chin parasymphysis swelling.", "2026-07-14", sqlite3.Binary(extraoral_photo_bytes)))

    conn.commit()

# --- AUTHENTICATION SERVICES ---

def verify_password(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password_hash, salt FROM doctors WHERE username = ?;", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    salt = bytes.fromhex(row['salt'])
    stored_hash = row['password_hash']
    
    # Compute hash of provided password
    computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()
    
    # Compare hashes safely (prevent timing attacks)
    if hmac.compare_digest(computed_hash, stored_hash):
        return {'id': row['id'], 'name': row['name'], 'username': username}
    return None

# --- PATIENT SERVICES ---

def register_patient(name, dob, gender, phone, email, address, allergies, medical_conditions, assigned_doctor_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (name, dob, gender, phone, email, address, allergies, medical_conditions, status, assigned_doctor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'NEW_OP', ?);
    """, (name, dob, gender, phone, email, address, allergies, medical_conditions, assigned_doctor_id))
    pid = cursor.lastrowid
    # Create empty case history
    cursor.execute("INSERT INTO case_history (patient_id) VALUES (?);", (pid,))
    conn.commit()
    conn.close()
    return pid

def get_new_op_patients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE status = 'NEW_OP' ORDER BY created_at DESC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_active_patients(search_query=None, doctor_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query_parts = ["status = 'PATIENT_LIST'"]
    params = []
    
    if doctor_id is not None:
        query_parts.append("assigned_doctor_id = ?")
        params.append(doctor_id)
        
    if search_query:
        query_parts.append("(name LIKE ? OR phone LIKE ? OR id LIKE ?)")
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
        
    sql = f"SELECT * FROM patients WHERE {' AND '.join(query_parts)} ORDER BY name ASC;"
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def open_patient_file(patient_id):
    """Moves patient from NEW_OP to PATIENT_LIST and returns their record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE patients SET status = 'PATIENT_LIST' WHERE id = ?;", (patient_id,))
    conn.commit()
    conn.close()
    return get_patient_details(patient_id)

def get_patient_details(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get demographic details joined with doctors
    cursor.execute("""
        SELECT p.*, d.name as assigned_doctor_name, d.discount_pct as assigned_doctor_discount
        FROM patients p 
        LEFT JOIN doctors d ON p.assigned_doctor_id = d.id 
        WHERE p.id = ?;
    """, (patient_id,))
    p_row = cursor.fetchone()
    if not p_row:
        conn.close()
        return None
    patient = dict(p_row)

    # Get case history
    cursor.execute("SELECT * FROM case_history WHERE patient_id = ?;", (patient_id,))
    ch_row = cursor.fetchone()
    patient['case_history'] = dict(ch_row) if ch_row else {}

    # Get dental chart
    cursor.execute("SELECT * FROM dental_chart WHERE patient_id = ?;", (patient_id,))
    chart_rows = cursor.fetchall()
    patient['dental_chart'] = [dict(r) for r in chart_rows]

    # Get perio chart
    cursor.execute("SELECT * FROM perio_chart WHERE patient_id = ?;", (patient_id,))
    perio_rows = cursor.fetchall()
    patient['perio_chart'] = [dict(r) for r in perio_rows]

    # Get X-rays (without heavy BLOB bytes in basic lookup to save memory, fetching separately when needed)
    cursor.execute("SELECT id, image_type, description, date_taken FROM xrays WHERE patient_id = ? ORDER BY date_taken DESC;", (patient_id,))
    patient['xrays'] = [dict(r) for r in cursor.fetchall()]

    # Get deleterious_habits
    cursor.execute("SELECT * FROM deleterious_habits WHERE patient_id = ?;", (patient_id,))
    patient['deleterious_habits'] = [dict(r) for r in cursor.fetchall()]

    # Get extra_oral_exam
    cursor.execute("SELECT * FROM extra_oral_exam WHERE patient_id = ?;", (patient_id,))
    eoe_row = cursor.fetchone()
    patient['extra_oral_exam'] = dict(eoe_row) if eoe_row else {}

    # Get intra_oral_exam
    cursor.execute("SELECT * FROM intra_oral_exam WHERE patient_id = ?;", (patient_id,))
    ioe_row = cursor.fetchone()
    patient['intra_oral_exam'] = dict(ioe_row) if ioe_row else {}

    # Get local_examinations
    cursor.execute("SELECT * FROM local_examinations WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['local_examinations'] = [dict(r) for r in cursor.fetchall()]

    # Get diagnoses
    cursor.execute("SELECT * FROM diagnoses WHERE patient_id = ?;", (patient_id,))
    diag_row = cursor.fetchone()
    patient['diagnoses'] = dict(diag_row) if diag_row else {}

    # Get investigations
    cursor.execute("SELECT * FROM investigations WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['investigations'] = [dict(r) for r in cursor.fetchall()]

    # Get pathology_requisitions
    cursor.execute("SELECT * FROM pathology_requisitions WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['pathology_requisitions'] = [dict(r) for r in cursor.fetchall()]

    # Get investigation_reports
    cursor.execute("SELECT * FROM investigation_reports WHERE patient_id = ?;", (patient_id,))
    rep_row = cursor.fetchone()
    patient['investigation_reports'] = dict(rep_row) if rep_row else {}

    # Get treatment_plans
    cursor.execute("SELECT * FROM treatment_plans WHERE patient_id = ?;", (patient_id,))
    plan_row = cursor.fetchone()
    patient['treatment_plans'] = dict(plan_row) if plan_row else {}

    # Get prescriptions
    cursor.execute("SELECT * FROM prescriptions WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['prescriptions'] = [dict(r) for r in cursor.fetchall()]

    # Get treatments
    cursor.execute("SELECT * FROM treatments WHERE patient_id = ?;", (patient_id,))
    t_row = cursor.fetchone()
    patient['treatments'] = dict(t_row) if t_row else {}

    # Get treatments_needed
    cursor.execute("SELECT * FROM treatments_needed WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['treatments_needed'] = [dict(r) for r in cursor.fetchall()]

    # Get treatments_done
    cursor.execute("SELECT * FROM treatments_done WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['treatments_done'] = [dict(r) for r in cursor.fetchall()]

    # Get appointments
    cursor.execute("SELECT * FROM appointments WHERE patient_id = ? ORDER BY app_date ASC, app_time ASC;", (patient_id,))
    patient['appointments'] = [dict(r) for r in cursor.fetchall()]

    # Get referrals
    cursor.execute("SELECT * FROM referrals WHERE patient_id = ?;", (patient_id,))
    ref_row = cursor.fetchone()
    patient['referrals'] = dict(ref_row) if ref_row else {}

    conn.close()
    return patient

# --- CLINICAL OPERATIONS ---

def update_case_history(patient_id, chief_complaint, hpi, past_dental_history, past_medical_history, habits, clinical_findings,
                        other_chief_complaint="", family_history="", brushing_method="Normal", brushing_frequency="Once a day",
                        brushing_duration="2 minutes", brushing_change_frequency="3 months", dentifrice_type="Paste",
                        other_dentifrice="", diet="Veg", parafunctional_habits="Absent", sleep="Normal", other_personal_history=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO case_history (
            patient_id, chief_complaint, hpi, past_dental_history, past_medical_history, habits, clinical_findings,
            other_chief_complaint, family_history, brushing_method, brushing_frequency, brushing_duration,
            brushing_change_frequency, dentifrice_type, other_dentifrice, diet, parafunctional_habits, sleep,
            other_personal_history, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, CURRENT_TIMESTAMP
        )
        ON CONFLICT(patient_id) DO UPDATE SET
            chief_complaint = excluded.chief_complaint,
            hpi = excluded.hpi,
            past_dental_history = excluded.past_dental_history,
            past_medical_history = excluded.past_medical_history,
            habits = excluded.habits,
            clinical_findings = excluded.clinical_findings,
            other_chief_complaint = excluded.other_chief_complaint,
            family_history = excluded.family_history,
            brushing_method = excluded.brushing_method,
            brushing_frequency = excluded.brushing_frequency,
            brushing_duration = excluded.brushing_duration,
            brushing_change_frequency = excluded.brushing_change_frequency,
            dentifrice_type = excluded.dentifrice_type,
            other_dentifrice = excluded.other_dentifrice,
            diet = excluded.diet,
            parafunctional_habits = excluded.parafunctional_habits,
            sleep = excluded.sleep,
            other_personal_history = excluded.other_personal_history,
            updated_at = CURRENT_TIMESTAMP;
    """, (patient_id, chief_complaint, hpi, past_dental_history, past_medical_history, habits, clinical_findings,
          other_chief_complaint, family_history, brushing_method, brushing_frequency, brushing_duration,
          brushing_change_frequency, dentifrice_type, other_dentifrice, diet, parafunctional_habits, sleep, other_personal_history))
    conn.commit()
    conn.close()

def update_patient_banner_fields(patient_id, occupation, village_town_city, allotted_to, validity_date, category, due_amt, case_record_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patients 
        SET occupation = ?, village_town_city = ?, allotted_to = ?, validity_date = ?, category = ?, due_amt = ?, case_record_no = ?
        WHERE id = ?;
    """, (occupation, village_town_city, allotted_to, validity_date, category, due_amt, case_record_no, patient_id))
    conn.commit()
    conn.close()

def save_deleterious_habits(patient_id, habits_list):
    conn = get_db_connection()
    cursor = conn.cursor()
    # first clear existing
    cursor.execute("DELETE FROM deleterious_habits WHERE patient_id = ?;", (patient_id,))
    for h in habits_list:
        cursor.execute("""
            INSERT INTO deleterious_habits (patient_id, habit_type, is_present, details_type, duration, frequency)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (patient_id, h['habit_type'], h['is_present'], h['details_type'], h['duration'], h['frequency']))
    conn.commit()
    conn.close()

def save_extra_oral_exam(patient_id, d):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO extra_oral_exam (
            patient_id, height, weight, gait, built, nourishment, cyanosis, clubbing, icterus, oedema, pallor, skin, eyes, others_general,
            bp, pulse, rr, temp, mouth_opening, face_symmetry, salivary_glands, tmj_deviation, tmj_tenderness, tmj_others,
            lymph_palpable, lymph_number, lymph_group_name, lymph_side_name,
            lymph_left_size, lymph_left_consistency, lymph_left_tenderness, lymph_left_fixity, lymph_left_others,
            lymph_right_size, lymph_right_consistency, lymph_right_tenderness, lymph_right_fixity, lymph_right_others
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?
        )
        ON CONFLICT(patient_id) DO UPDATE SET
            height = excluded.height, weight = excluded.weight, gait = excluded.gait, built = excluded.built,
            nourishment = excluded.nourishment, cyanosis = excluded.cyanosis, clubbing = excluded.clubbing,
            icterus = excluded.icterus, oedema = excluded.oedema, pallor = excluded.pallor, skin = excluded.skin,
            eyes = excluded.eyes, others_general = excluded.others_general, bp = excluded.bp, pulse = excluded.pulse,
            rr = excluded.rr, temp = excluded.temp, mouth_opening = excluded.mouth_opening,
            face_symmetry = excluded.face_symmetry, salivary_glands = excluded.salivary_glands,
            tmj_deviation = excluded.tmj_deviation, tmj_tenderness = excluded.tmj_tenderness, tmj_others = excluded.tmj_others,
            lymph_palpable = excluded.lymph_palpable, lymph_number = excluded.lymph_number,
            lymph_group_name = excluded.lymph_group_name, lymph_side_name = excluded.lymph_side_name,
            lymph_left_size = excluded.lymph_left_size, lymph_left_consistency = excluded.lymph_left_consistency,
            lymph_left_tenderness = excluded.lymph_left_tenderness, lymph_left_fixity = excluded.lymph_left_fixity,
            lymph_left_others = excluded.lymph_left_others,
            lymph_right_size = excluded.lymph_right_size, lymph_right_consistency = excluded.lymph_right_consistency,
            lymph_right_tenderness = excluded.lymph_right_tenderness, lymph_right_fixity = excluded.lymph_right_fixity,
            lymph_right_others = excluded.lymph_right_others;
    """, (patient_id, d.get('height',''), d.get('weight',''), d.get('gait',''), d.get('built',''), d.get('nourishment',''),
          d.get('cyanosis',''), d.get('clubbing',''), d.get('icterus',''), d.get('oedema',''), d.get('pallor',''), d.get('skin',''),
          d.get('eyes',''), d.get('others_general',''), d.get('bp',''), d.get('pulse',''), d.get('rr',''), d.get('temp',''),
          d.get('mouth_opening',''), d.get('face_symmetry','Symmetrical'), d.get('salivary_glands','Normal'),
          d.get('tmj_deviation',0), d.get('tmj_tenderness',0), d.get('tmj_others',''),
          d.get('lymph_palpable','Non-palpable'), d.get('lymph_number',''), d.get('lymph_group_name',''), d.get('lymph_side_name',''),
          d.get('lymph_left_size',''), d.get('lymph_left_consistency',''), d.get('lymph_left_tenderness',0), d.get('lymph_left_fixity',''), d.get('lymph_left_others',''),
          d.get('lymph_right_size',''), d.get('lymph_right_consistency',''), d.get('lymph_right_tenderness',0), d.get('lymph_right_fixity',''), d.get('lymph_right_others','')))
    conn.commit()
    conn.close()

def save_intra_oral_exam(patient_id, d):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO intra_oral_exam (
            patient_id, occlusion_molar, occlusion_center, occlusion_others,
            wasting_attrition, wasting_abrasion, wasting_erosion, wasting_abfraction,
            hypoplasia, hypoplasia_details, supernumerary, supernumerary_details, other_hard_tissue,
            labial_mucosa, labial_mucosa_details, buccal_mucosa, buccal_mucosa_details,
            floor_mouth, floor_mouth_details, vestibular_mucosa, vestibular_mucosa_details,
            lingual_mucosa, lingual_mucosa_details, palatal_mucosa, palatal_mucosa_details,
            salivary_duct, salivary_duct_details, other_mucosa, other_mucosa_details,
            stain, stain_details, calculus, calculus_details, recession, recession_details,
            enlargement, enlargement_details, bop, bop_details, pockets, pockets_details,
            furcation, furcation_details, mucogingival, mucogingival_details
        ) VALUES (
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?
        )
        ON CONFLICT(patient_id) DO UPDATE SET
            occlusion_molar = excluded.occlusion_molar, occlusion_center = excluded.occlusion_center, occlusion_others = excluded.occlusion_others,
            wasting_attrition = excluded.wasting_attrition, wasting_abrasion = excluded.wasting_abrasion,
            wasting_erosion = excluded.wasting_erosion, wasting_abfraction = excluded.wasting_abfraction,
            hypoplasia = excluded.hypoplasia, hypoplasia_details = excluded.hypoplasia_details,
            supernumerary = excluded.supernumerary, supernumerary_details = excluded.supernumerary_details,
            other_hard_tissue = excluded.other_hard_tissue,
            labial_mucosa = excluded.labial_mucosa, labial_mucosa_details = excluded.labial_mucosa_details,
            buccal_mucosa = excluded.buccal_mucosa, buccal_mucosa_details = excluded.buccal_mucosa_details,
            floor_mouth = excluded.floor_mouth, floor_mouth_details = excluded.floor_mouth_details,
            vestibular_mucosa = excluded.vestibular_mucosa, vestibular_mucosa_details = excluded.vestibular_mucosa_details,
            lingual_mucosa = excluded.lingual_mucosa, lingual_mucosa_details = excluded.lingual_mucosa_details,
            palatal_mucosa = excluded.palatal_mucosa, palatal_mucosa_details = excluded.palatal_mucosa_details,
            salivary_duct = excluded.salivary_duct, salivary_duct_details = excluded.salivary_duct_details,
            other_mucosa = excluded.other_mucosa, other_mucosa_details = excluded.other_mucosa_details,
            stain = excluded.stain, stain_details = excluded.stain_details,
            calculus = excluded.calculus, calculus_details = excluded.calculus_details,
            recession = excluded.recession, recession_details = excluded.recession_details,
            enlargement = excluded.enlargement, enlargement_details = excluded.enlargement_details,
            bop = excluded.bop, bop_details = excluded.bop_details,
            pockets = excluded.pockets, pockets_details = excluded.pockets_details,
            furcation = excluded.furcation, furcation_details = excluded.furcation_details,
            mucogingival = excluded.mucogingival, mucogingival_details = excluded.mucogingival_details;
    """, (patient_id, d.get('occlusion_molar',''), d.get('occlusion_center',''), d.get('occlusion_others',''),
          d.get('wasting_attrition',''), d.get('wasting_abrasion',''), d.get('wasting_erosion',''), d.get('wasting_abfraction',''),
          d.get('hypoplasia','Absent'), d.get('hypoplasia_details',''), d.get('supernumerary','Absent'), d.get('supernumerary_details',''), d.get('other_hard_tissue',''),
          d.get('labial_mucosa','Apparently Normal'), d.get('labial_mucosa_details',''),
          d.get('buccal_mucosa','Apparently Normal'), d.get('buccal_mucosa_details',''),
          d.get('floor_mouth','Apparently Normal'), d.get('floor_mouth_details',''),
          d.get('vestibular_mucosa','Apparently Normal'), d.get('vestibular_mucosa_details',''),
          d.get('lingual_mucosa','Apparently Normal'), d.get('lingual_mucosa_details',''),
          d.get('palatal_mucosa','Apparently Normal'), d.get('palatal_mucosa_details',''),
          d.get('salivary_duct','Apparently Normal'), d.get('salivary_duct_details',''),
          d.get('other_mucosa','Apparently Normal'), d.get('other_mucosa_details',''),
          d.get('stain','Absent'), d.get('stain_details',''), d.get('calculus','Absent'), d.get('calculus_details',''),
          d.get('recession','Absent'), d.get('recession_details',''), d.get('enlargement','Absent'), d.get('enlargement_details',''),
          d.get('bop','Absent'), d.get('bop_details',''), d.get('pockets','Absent'), d.get('pockets_details',''),
          d.get('furcation','Absent'), d.get('furcation_details',''), d.get('mucogingival','Absent'), d.get('mucogingival_details','')))
    conn.commit()
    conn.close()

def add_local_examination(patient_id, header, eo_i, eo_p, io_s_i, io_s_p, io_h_i, io_h_p):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO local_examinations (
            patient_id, header, extra_oral_inspection, extra_oral_palpation,
            soft_tissue_inspection, soft_tissue_palpation, hard_tissue_inspection, hard_tissue_percussion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (patient_id, header, eo_i, eo_p, io_s_i, io_s_p, io_h_i, io_h_p))
    conn.commit()
    conn.close()

def delete_local_examination(exam_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM local_examinations WHERE id = ?;", (exam_id,))
    conn.commit()
    conn.close()

def save_diagnosis(patient_id, provisional_diagnosis, differential_diagnosis, note, final_diagnosis=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO diagnoses (patient_id, provisional_diagnosis, differential_diagnosis, note, final_diagnosis)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(patient_id) DO UPDATE SET
            provisional_diagnosis = excluded.provisional_diagnosis,
            differential_diagnosis = excluded.differential_diagnosis,
            note = excluded.note,
            final_diagnosis = excluded.final_diagnosis;
    """, (patient_id, provisional_diagnosis, differential_diagnosis, note, final_diagnosis))
    conn.commit()
    conn.close()

def add_investigation(patient_id, service_type, group_name, service_name, teeth_no, qty, rate, amount, disc_pct, total, status="Pending"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO investigations (patient_id, service_type, group_name, service_name, teeth_no, qty, rate, amount, disc_pct, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (patient_id, service_type, group_name, service_name, teeth_no, qty, rate, amount, disc_pct, total, status))
    conn.commit()
    conn.close()

def delete_investigation(inv_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM investigations WHERE id = ?;", (inv_id,))
    conn.commit()
    conn.close()

def add_pathology_requisition(patient_id, category, service_name, teeth_no, qty, rate, amount, disc_pct, total):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pathology_requisitions (patient_id, category, service_name, teeth_no, qty, rate, amount, disc_pct, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (patient_id, category, service_name, teeth_no, qty, rate, amount, disc_pct, total))
    conn.commit()
    conn.close()

def delete_pathology_requisition(req_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pathology_requisitions WHERE id = ?;", (req_id,))
    conn.commit()
    conn.close()

def save_investigation_reports(patient_id, radiology_reports, pathology_reports):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO investigation_reports (patient_id, radiology_reports, pathology_reports)
        VALUES (?, ?, ?)
        ON CONFLICT(patient_id) DO UPDATE SET
            radiology_reports = excluded.radiology_reports,
            pathology_reports = excluded.pathology_reports;
    """, (patient_id, radiology_reports, pathology_reports))
    conn.commit()
    conn.close()

def save_treatment_plan(patient_id, treatment_plan, prognosis, physician_note):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO treatment_plans (patient_id, treatment_plan, prognosis, physician_note)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(patient_id) DO UPDATE SET
            treatment_plan = excluded.treatment_plan,
            prognosis = excluded.prognosis,
            physician_note = excluded.physician_note;
    """, (patient_id, treatment_plan, prognosis, physician_note))
    conn.commit()
    conn.close()

def add_prescription(patient_id, drug_name, dosage, frequency, duration):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO prescriptions (patient_id, drug_name, dosage, frequency, duration)
        VALUES (?, ?, ?, ?, ?);
    """, (patient_id, drug_name, dosage, frequency, duration))
    conn.commit()
    conn.close()

def delete_prescription(presc_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prescriptions WHERE id = ?;", (presc_id,))
    conn.commit()
    conn.close()

def save_treatment(patient_id, procedure, progress):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO treatments (patient_id, procedure, progress)
        VALUES (?, ?, ?)
        ON CONFLICT(patient_id) DO UPDATE SET
            procedure = excluded.procedure,
            progress = excluded.progress;
    """, (patient_id, procedure, progress))
    conn.commit()
    conn.close()

def add_treatment_done(patient_id, date_done, student_name, doctor_name, details, status="Completed", treatment_needed_id=None, doctor_notes="", treatment_status="Pending"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO treatments_done (patient_id, date_done, student_name, doctor_name, details, status, treatment_needed_id, doctor_notes, treatment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (patient_id, date_done, student_name, doctor_name, details, status, treatment_needed_id, doctor_notes, treatment_status))
    conn.commit()
    conn.close()

def delete_treatment_done(td_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM treatments_done WHERE id = ?;", (td_id,))
    conn.commit()
    conn.close()

def add_treatment_needed(patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status='Unpaid'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO treatments_needed (patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status))
    conn.commit()
    conn.close()

def delete_treatment_needed(needed_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM treatments_needed WHERE id = ?;", (needed_id,))
    conn.commit()
    conn.close()

def pay_treatment_needed_bill(needed_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE treatments_needed SET billing_status = 'Paid' WHERE id = ?;", (needed_id,))
    conn.commit()
    conn.close()

def add_appointment(patient_id, app_date, app_time, reason, status="Yet to visit"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments (patient_id, app_date, app_time, reason, status)
        VALUES (?, ?, ?, ?, ?);
    """, (patient_id, app_date, app_time, reason, status))
    conn.commit()
    conn.close()

def delete_appointment(app_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?;", (app_id,))
    conn.commit()
    conn.close()

def update_appointment_status(app_id, status, visited_on=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments 
        SET status = ?, visited_on = ?
        WHERE id = ?;
    """, (status, visited_on, app_id))
    conn.commit()
    conn.close()

# Existing dental conditions services
def save_tooth_condition(patient_id, tooth_number, surface, condition, notes=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    if condition == 'healthy':
        cursor.execute("DELETE FROM dental_chart WHERE patient_id = ? AND tooth_number = ? AND surface = ?;", (patient_id, tooth_number, surface))
    else:
        cursor.execute("""
            INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(patient_id, tooth_number, surface) DO UPDATE SET
                condition = excluded.condition,
                notes = excluded.notes;
        """, (patient_id, tooth_number, surface, condition, notes))
    conn.commit()
    conn.close()

def save_perio_status(patient_id, tooth_number, pd_facial, pd_lingual, mobility, bop):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO perio_chart (patient_id, tooth_number, pd_facial, pd_lingual, mobility, bop)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(patient_id, tooth_number) DO UPDATE SET
            pd_facial = excluded.pd_facial,
            pd_lingual = excluded.pd_lingual,
            mobility = excluded.mobility,
            bop = excluded.bop;
    """, (patient_id, tooth_number, pd_facial, pd_lingual, mobility, bop))
    conn.commit()
    conn.close()

# Existing X-Ray blob services
def add_patient_xray(patient_id, image_type, description, date_taken, image_bytes):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO xrays (patient_id, image_type, description, date_taken, image_data)
        VALUES (?, ?, ?, ?, ?);
    """, (patient_id, image_type, description, date_taken, sqlite3.Binary(image_bytes)))
    xray_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return xray_id

def get_xray_image_data(xray_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_data FROM xrays WHERE id = ?;", (xray_id,))
    row = cursor.fetchone()
    conn.close()
    return row['image_data'] if row else None

def delete_xray(xray_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM xrays WHERE id = ?;", (xray_id,))
    conn.commit()
    conn.close()
    return True

# Settings and profiles
def get_clinic_profile(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, username FROM clinics WHERE username = ?;", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_clinic_profile(old_username, new_name, new_username, new_password=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if new_password:
        salt = os.urandom(16).hex()
        hashed_pw = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), bytes.fromhex(salt), 100000).hex()
        cursor.execute("UPDATE clinics SET name = ?, username = ?, password_hash = ?, salt = ? WHERE username = ?;", (new_name, new_username, hashed_pw, salt, old_username))
    else:
        cursor.execute("UPDATE clinics SET name = ?, username = ? WHERE username = ?;", (new_name, new_username, old_username))
    conn.commit()
    conn.close()

def vacuum_database():
    conn = get_db_connection()
    conn.execute("VACUUM;")
    conn.close()

def get_doctors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, discount_pct FROM doctors ORDER BY name ASC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def create_doctor(name, username, password, discount_pct=0.0):
    conn = get_db_connection()
    cursor = conn.cursor()
    salt = os.urandom(16).hex()
    hashed_pw = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100000).hex()
    try:
        cursor.execute("INSERT INTO doctors (name, username, password_hash, salt, discount_pct) VALUES (?, ?, ?, ?, ?);", (name, username, hashed_pw, salt, discount_pct))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def update_patient_doctor(patient_id, doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE patients SET assigned_doctor_id = ? WHERE id = ?;", (doctor_id, patient_id))
    conn.commit()
    conn.close()

def get_clinic_logo_path():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT logo_path FROM clinics LIMIT 1;")
    row = cursor.fetchone()
    conn.close()
    return row['logo_path'] if row else ''

def save_clinic_logo_path(logo_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clinics SET logo_path = ?;", (logo_path,))
    conn.commit()
    conn.close()

def get_upcoming_appointments(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, p.name as patient_name, p.phone as patient_phone 
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.status = 'Yet to visit'
        ORDER BY a.app_date ASC, a.app_time ASC
        LIMIT ?;
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def save_referral(patient_id, referred_to_dept, referred_to_doctor_id, referral_reason, referral_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO referrals (patient_id, referred_to_dept, referred_to_doctor_id, referral_reason, referral_status)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(patient_id) DO UPDATE SET
            referred_to_dept = excluded.referred_to_dept,
            referred_to_doctor_id = excluded.referred_to_doctor_id,
            referral_reason = excluded.referral_reason,
            referral_status = excluded.referral_status;
    """, (patient_id, referred_to_dept, referred_to_doctor_id, referral_reason, referral_status))
    conn.commit()
    conn.close()

save_local_examination = add_local_examination
save_investigation = add_investigation
save_pathology_requisition = add_pathology_requisition
save_prescription = add_prescription
save_treatment_done = add_treatment_done
save_appointment = add_appointment


def add_patient_file(patient_id, file_category, file_name, file_data, upload_date, file_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patient_files (patient_id, file_category, file_name, file_data, upload_date, file_type)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (patient_id, file_category, file_name, file_data, upload_date, file_type))
    conn.commit()
    conn.close()

def get_patient_files(patient_id, file_category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, patient_id, file_category, file_name, upload_date, file_type 
        FROM patient_files 
        WHERE patient_id = ? AND file_category = ?
        ORDER BY upload_date DESC, id DESC;
    """, (patient_id, file_category))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_patient_file(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM patient_files WHERE id = ?;
    """, (file_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_patient_file(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM patient_files WHERE id = ?;
    """, (file_id,))
    conn.commit()
    conn.close()





