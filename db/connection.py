# DentaLink Database Connection & Initialization Manager
import os
import sqlite3
import sys

DB_NAME = "dental_clinic.db"


def get_current_db_name():
    """Returns current active DB_NAME, resolving overrides in database module facade."""
    if 'database' in sys.modules and hasattr(sys.modules['database'], 'DB_NAME'):
        return sys.modules['database'].DB_NAME
    return DB_NAME


def get_db_connection():
    """Establishes a connection to the SQLite database with foreign keys enabled."""
    conn = sqlite3.connect(get_current_db_name())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database():
    """Initializes schema and runs necessary table migrations."""
    db_name = get_current_db_name()
    db_exists = os.path.exists(db_name)
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

    cursor.execute("PRAGMA table_info(clinics);")
    c_cols = [c['name'] for c in cursor.fetchall()]
    for col in ['logo_path', 'address', 'phone', 'email', 'department', 'tagline']:
        if col not in c_cols:
            try:
                cursor.execute(f"ALTER TABLE clinics ADD COLUMN {col} TEXT DEFAULT '';")
            except sqlite3.OperationalError:
                pass
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
            status TEXT DEFAULT 'NEW_OP',
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

    # Check migration for dental_chart and perio_chart
    cursor.execute("PRAGMA table_info(dental_chart);")
    columns = cursor.fetchall()
    tooth_number_type = ""
    for col in columns:
        if col['name'] == 'tooth_number':
            tooth_number_type = col['type'].upper()
            break

    if tooth_number_type and 'INT' in tooth_number_type:
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dental_chart (
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deleterious_habits (
            patient_id INTEGER,
            habit_type TEXT,
            is_present BOOLEAN DEFAULT 0,
            details_type TEXT DEFAULT '',
            duration TEXT DEFAULT '',
            frequency TEXT DEFAULT '',
            PRIMARY KEY (patient_id, habit_type),
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pathology_requisitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            category TEXT DEFAULT '',
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigation_reports (
            patient_id INTEGER PRIMARY KEY,
            radiology_reports TEXT DEFAULT '',
            pathology_reports TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS treatment_plans (
            patient_id INTEGER PRIMARY KEY,
            treatment_plan TEXT DEFAULT '',
            prognosis TEXT DEFAULT '',
            physician_note TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS treatments (
            patient_id INTEGER PRIMARY KEY,
            procedure TEXT DEFAULT '',
            progress TEXT DEFAULT '',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

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

    cursor.execute("PRAGMA table_info(referrals);")
    ref_cols = {c['name']: c['pk'] for c in cursor.fetchall()}
    if 'patient_id' in ref_cols and ref_cols['patient_id'] == 1 and 'id' not in ref_cols:
        cursor.execute("ALTER TABLE referrals RENAME TO referrals_old;")
        cursor.execute("""
            CREATE TABLE referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                referred_to_dept TEXT DEFAULT '',
                referred_to_doctor_id INTEGER,
                referral_reason TEXT DEFAULT '',
                referral_status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("""
            INSERT INTO referrals (patient_id, referred_to_dept, referred_to_doctor_id, referral_reason, referral_status)
            SELECT patient_id, referred_to_dept, referred_to_doctor_id, referral_reason, referral_status FROM referrals_old;
        """)
        cursor.execute("DROP TABLE referrals_old;")
        conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            referred_to_dept TEXT DEFAULT '',
            referred_to_doctor_id INTEGER,
            referral_reason TEXT DEFAULT '',
            referral_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_history_commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            commit_hash TEXT UNIQUE NOT NULL,
            patient_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            parent_commit_id INTEGER,
            commit_message TEXT NOT NULL,
            doctor_name TEXT DEFAULT '',
            timestamp_formatted TEXT NOT NULL,
            encrypted_delta_json TEXT NOT NULL,
            encrypted_snapshot TEXT NOT NULL,
            hmac_signature TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            file_category TEXT DEFAULT '',
            file_name TEXT DEFAULT '',
            file_data BLOB,
            upload_date TEXT DEFAULT '',
            file_type TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    cursor.execute("PRAGMA table_info(doctors);")
    doc_cols = [c['name'] for c in cursor.fetchall()]
    for col, col_def in [
        ('master_key_wrapper', "TEXT DEFAULT ''"),
        ('security_q1', "TEXT DEFAULT ''"),
        ('security_a1', "TEXT DEFAULT ''"),
        ('security_q2', "TEXT DEFAULT ''"),
        ('security_a2', "TEXT DEFAULT ''"),
        ('universal_recovery_wrapper', "TEXT DEFAULT ''")
    ]:
        if col not in doc_cols:
            cursor.execute(f"ALTER TABLE doctors ADD COLUMN {col} {col_def};")
            conn.commit()

    cursor.execute("PRAGMA table_info(clinics);")
    c_cols = [c['name'] for c in cursor.fetchall()]
    for col, col_def in [
        ('universal_recovery_key_hash', "TEXT DEFAULT ''"),
        ('universal_recovery_wrapper', "TEXT DEFAULT ''"),
        ('master_key_wrapper', "TEXT DEFAULT ''")
    ]:
        if col not in c_cols:
            cursor.execute(f"ALTER TABLE clinics ADD COLUMN {col} {col_def};")
            conn.commit()

    conn.close()


def vacuum_database():
    """Reclaims unused SQLite storage space."""
    conn = get_db_connection()
    conn.execute("VACUUM;")
    conn.close()
