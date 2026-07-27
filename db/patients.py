# DentaLink Patient Management & Demographic Database Operations
from db.connection import get_db_connection
from db.history import create_patient_history_commit


def register_patient(name, dob, gender, phone, email, address, allergies, medical_conditions, assigned_doctor_id=None):
    """Registers a new patient and creates initial baseline history commit."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (name, dob, gender, phone, email, address, allergies, medical_conditions, status, assigned_doctor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'NEW_OP', ?);
    """, (name, dob, gender, phone, email, address, allergies, medical_conditions, assigned_doctor_id))
    pid = cursor.lastrowid
    cursor.execute("INSERT INTO case_history (patient_id) VALUES (?);", (pid,))
    conn.commit()
    conn.close()

    initial_snapshot = {
        'allergies': allergies or 'None',
        'medical_conditions': medical_conditions or 'None',
        'chief_complaint': '',
        'hpi': '',
        'past_dental_history': '',
        'past_medical_history': '',
        'clinical_findings': '',
        'provisional_diagnosis': '',
        'differential_diagnosis': '',
        'final_diagnosis': '',
        'note': ''
    }
    create_patient_history_commit(pid, "Initial Patient Registration & Case Record Created", "Front Desk", initial_snapshot, force_commit=True)

    return pid


def get_new_op_patients():
    """Retrieves all patients currently in the NEW_OP queue."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE status = 'NEW_OP' ORDER BY created_at DESC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_active_patients(search_query=None, doctor_id=None):
    """Retrieves patients in the active Patient List with optional search filters."""
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
    """Transitions patient status from NEW_OP to PATIENT_LIST."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE patients SET status = 'PATIENT_LIST' WHERE id = ?;", (patient_id,))
    conn.commit()
    conn.close()
    return get_patient_details(patient_id)


def update_patient_banner_fields(patient_id, category=None, due_amt=None, case_record_no=None, allotted_to=None, validity_date=None):
    """Updates demographic header banner fields for a patient."""
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = []
    params = []

    if category is not None:
        fields.append("category = ?")
        params.append(category)
    if due_amt is not None:
        fields.append("due_amt = ?")
        params.append(due_amt)
    if case_record_no is not None:
        fields.append("case_record_no = ?")
        params.append(case_record_no)
    if allotted_to is not None:
        fields.append("allotted_to = ?")
        params.append(allotted_to)
    if validity_date is not None:
        fields.append("validity_date = ?")
        params.append(validity_date)

    if fields:
        params.append(patient_id)
        cursor.execute(f"UPDATE patients SET {', '.join(fields)} WHERE id = ?;", tuple(params))
        conn.commit()
    conn.close()


def get_patient_details(patient_id):
    """Fetches complete multi-tab clinical record for a patient."""
    conn = get_db_connection()
    cursor = conn.cursor()

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

    cursor.execute("SELECT * FROM case_history WHERE patient_id = ?;", (patient_id,))
    ch_row = cursor.fetchone()
    patient['case_history'] = dict(ch_row) if ch_row else {}

    cursor.execute("SELECT * FROM dental_chart WHERE patient_id = ?;", (patient_id,))
    patient['dental_chart'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM perio_chart WHERE patient_id = ?;", (patient_id,))
    patient['perio_chart'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT id, image_type, description, date_taken FROM xrays WHERE patient_id = ? ORDER BY date_taken DESC;", (patient_id,))
    patient['xrays'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM deleterious_habits WHERE patient_id = ?;", (patient_id,))
    patient['deleterious_habits'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM extra_oral_exam WHERE patient_id = ?;", (patient_id,))
    eoe_row = cursor.fetchone()
    patient['extra_oral_exam'] = dict(eoe_row) if eoe_row else {}

    cursor.execute("SELECT * FROM intra_oral_exam WHERE patient_id = ?;", (patient_id,))
    ioe_row = cursor.fetchone()
    patient['intra_oral_exam'] = dict(ioe_row) if ioe_row else {}

    cursor.execute("SELECT * FROM local_examinations WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['local_examinations'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM diagnoses WHERE patient_id = ?;", (patient_id,))
    diag_row = cursor.fetchone()
    patient['diagnoses'] = dict(diag_row) if diag_row else {}

    cursor.execute("SELECT * FROM investigations WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['investigations'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM pathology_requisitions WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['pathology_requisitions'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM investigation_reports WHERE patient_id = ?;", (patient_id,))
    rep_row = cursor.fetchone()
    patient['investigation_reports'] = dict(rep_row) if rep_row else {}

    cursor.execute("SELECT * FROM treatment_plans WHERE patient_id = ?;", (patient_id,))
    plan_row = cursor.fetchone()
    patient['treatment_plans'] = dict(plan_row) if plan_row else {}

    cursor.execute("SELECT * FROM prescriptions WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['prescriptions'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM treatments WHERE patient_id = ?;", (patient_id,))
    t_row = cursor.fetchone()
    patient['treatments'] = dict(t_row) if t_row else {}

    cursor.execute("SELECT * FROM treatments_needed WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['treatments_needed'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM treatments_done WHERE patient_id = ? ORDER BY created_at ASC;", (patient_id,))
    patient['treatments_done'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM appointments WHERE patient_id = ? ORDER BY app_date ASC, app_time ASC;", (patient_id,))
    patient['appointments'] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM referrals WHERE patient_id = ? ORDER BY id DESC;", (patient_id,))
    ref_rows = cursor.fetchall()
    patient['referrals'] = [dict(r) for r in ref_rows]
    patient['latest_referral'] = dict(ref_rows[0]) if ref_rows else {}

    conn.close()
    return patient


def add_patient_file(patient_id, file_category, file_name, file_data, upload_date, file_type):
    """Saves a binary patient document file."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patient_files (patient_id, file_category, file_name, file_data, upload_date, file_type)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (patient_id, file_category, file_name, file_data, upload_date, file_type))
    conn.commit()
    conn.close()


def get_patient_files(patient_id, file_category):
    """Retrieves metadata of files for a specific category."""
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
    """Retrieves full record (including BLOB data) for a file."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_files WHERE id = ?;", (file_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_patient_file(file_id):
    """Deletes a patient file record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patient_files WHERE id = ?;", (file_id,))
    conn.commit()
    conn.close()
