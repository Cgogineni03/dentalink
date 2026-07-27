# DentaLink Clinical Examinations, Diagnoses, Treatments & Diagnostics Database Operations
import sqlite3

from db.connection import get_db_connection


def update_case_history(patient_id, chief_complaint, hpi, past_dental_history, past_medical_history, habits, clinical_findings,
                        other_chief_complaint="", family_history="", brushing_method="Normal", brushing_frequency="Once a day",
                        brushing_duration="2 minutes", brushing_change_frequency="3 months", dentifrice_type="Paste",
                        other_dentifrice="", diet="Veg", parafunctional_habits="Absent", sleep="Normal", other_personal_history=""):
    """Updates case history record for a patient."""
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


def save_deleterious_habits(patient_id, habits_list):
    """Saves deleterious habits list for a patient."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM deleterious_habits WHERE patient_id = ?;", (patient_id,))
    for h in habits_list:
        cursor.execute("""
            INSERT INTO deleterious_habits (patient_id, habit_type, is_present, details_type, duration, frequency)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (patient_id, h['habit_type'], h['is_present'], h['details_type'], h['duration'], h['frequency']))
    conn.commit()
    conn.close()


def save_extra_oral_exam(patient_id, d):
    """Saves extra-oral exam findings."""
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
    """, (patient_id, d.get('height', ''), d.get('weight', ''), d.get('gait', ''), d.get('built', ''), d.get('nourishment', ''),
          d.get('cyanosis', ''), d.get('clubbing', ''), d.get('icterus', ''), d.get('oedema', ''), d.get('pallor', ''), d.get('skin', ''),
          d.get('eyes', ''), d.get('others_general', ''), d.get('bp', ''), d.get('pulse', ''), d.get('rr', ''), d.get('temp', ''),
          d.get('mouth_opening', ''), d.get('face_symmetry', 'Symmetrical'), d.get('salivary_glands', 'Normal'),
          d.get('tmj_deviation', 0), d.get('tmj_tenderness', 0), d.get('tmj_others', ''),
          d.get('lymph_palpable', 'Non-palpable'), d.get('lymph_number', ''), d.get('lymph_group_name', ''), d.get('lymph_side_name', ''),
          d.get('lymph_left_size', ''), d.get('lymph_left_consistency', ''), d.get('lymph_left_tenderness', 0), d.get('lymph_left_fixity', ''), d.get('lymph_left_others', ''),
          d.get('lymph_right_size', ''), d.get('lymph_right_consistency', ''), d.get('lymph_right_tenderness', 0), d.get('lymph_right_fixity', ''), d.get('lymph_right_others', '')))
    conn.commit()
    conn.close()


def save_intra_oral_exam(patient_id, d):
    """Saves intra-oral exam findings."""
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
    """, (patient_id, d.get('occlusion_molar', ''), d.get('occlusion_center', ''), d.get('occlusion_others', ''),
          d.get('wasting_attrition', ''), d.get('wasting_abrasion', ''), d.get('wasting_erosion', ''), d.get('wasting_abfraction', ''),
          d.get('hypoplasia', 'Absent'), d.get('hypoplasia_details', ''), d.get('supernumerary', 'Absent'), d.get('supernumerary_details', ''), d.get('other_hard_tissue', ''),
          d.get('labial_mucosa', 'Apparently Normal'), d.get('labial_mucosa_details', ''),
          d.get('buccal_mucosa', 'Apparently Normal'), d.get('buccal_mucosa_details', ''),
          d.get('floor_mouth', 'Apparently Normal'), d.get('floor_mouth_details', ''),
          d.get('vestibular_mucosa', 'Apparently Normal'), d.get('vestibular_mucosa_details', ''),
          d.get('lingual_mucosa', 'Apparently Normal'), d.get('lingual_mucosa_details', ''),
          d.get('palatal_mucosa', 'Apparently Normal'), d.get('palatal_mucosa_details', ''),
          d.get('salivary_duct', 'Apparently Normal'), d.get('salivary_duct_details', ''),
          d.get('other_mucosa', 'Apparently Normal'), d.get('other_mucosa_details', ''),
          d.get('stain', 'Absent'), d.get('stain_details', ''), d.get('calculus', 'Absent'), d.get('calculus_details', ''),
          d.get('recession', 'Absent'), d.get('recession_details', ''), d.get('enlargement', 'Absent'), d.get('enlargement_details', ''),
          d.get('bop', 'Absent'), d.get('bop_details', ''), d.get('pockets', 'Absent'), d.get('pockets_details', ''),
          d.get('furcation', 'Absent'), d.get('furcation_details', ''), d.get('mucogingival', 'Absent'), d.get('mucogingival_details', '')))
    conn.commit()
    conn.close()


def add_local_examination(patient_id, header, eo_i, eo_p, io_s_i, io_s_p, io_h_i, io_h_p):
    """Adds a local examination finding."""
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
    """Deletes a local examination entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM local_examinations WHERE id = ?;", (exam_id,))
    conn.commit()
    conn.close()


def save_diagnosis(patient_id, provisional_diagnosis, differential_diagnosis, note, final_diagnosis=""):
    """Saves clinical diagnosis information."""
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
    """Adds a diagnostic investigation item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO investigations (patient_id, service_type, group_name, service_name, teeth_no, qty, rate, amount, disc_pct, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (patient_id, service_type, group_name, service_name, teeth_no, qty, rate, amount, disc_pct, total, status))
    conn.commit()
    conn.close()


def delete_investigation(inv_id):
    """Deletes an investigation item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM investigations WHERE id = ?;", (inv_id,))
    conn.commit()
    conn.close()


def add_pathology_requisition(patient_id, category, service_name, teeth_no, qty, rate, amount, disc_pct, total):
    """Adds a pathology test requisition."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pathology_requisitions (patient_id, category, service_name, teeth_no, qty, rate, amount, disc_pct, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (patient_id, category, service_name, teeth_no, qty, rate, amount, disc_pct, total))
    conn.commit()
    conn.close()


def delete_pathology_requisition(req_id):
    """Deletes a pathology test requisition."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pathology_requisitions WHERE id = ?;", (req_id,))
    conn.commit()
    conn.close()


def save_investigation_reports(patient_id, radiology_reports, pathology_reports):
    """Saves radiology and pathology report notes."""
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
    """Saves overall treatment plan and prognosis."""
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
    """Adds a drug prescription."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO prescriptions (patient_id, drug_name, dosage, frequency, duration)
        VALUES (?, ?, ?, ?, ?);
    """, (patient_id, drug_name, dosage, frequency, duration))
    conn.commit()
    conn.close()


def delete_prescription(presc_id):
    """Deletes a prescription item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prescriptions WHERE id = ?;", (presc_id,))
    conn.commit()
    conn.close()


def save_treatment(patient_id, procedure, progress):
    """Saves active treatment notes."""
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
    """Logs completed treatment procedure."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO treatments_done (patient_id, date_done, student_name, doctor_name, details, status, treatment_needed_id, doctor_notes, treatment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (patient_id, date_done, student_name, doctor_name, details, status, treatment_needed_id, doctor_notes, treatment_status))
    conn.commit()
    conn.close()


def delete_treatment_done(td_id):
    """Deletes a treatment done log entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM treatments_done WHERE id = ?;", (td_id,))
    conn.commit()
    conn.close()


def add_treatment_needed(patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status='Unpaid'):
    """Adds a required treatment item for billing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO treatments_needed (patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (patient_id, procedure_name, teeth_no, qty, rate, discount, total, billing_status))
    conn.commit()
    conn.close()


def delete_treatment_needed(needed_id):
    """Deletes a treatment needed billing item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM treatments_needed WHERE id = ?;", (needed_id,))
    conn.commit()
    conn.close()


def pay_treatment_needed_bill(needed_id):
    """Marks a treatment needed line item as Paid."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE treatments_needed SET billing_status = 'Paid' WHERE id = ?;", (needed_id,))
    conn.commit()
    conn.close()


def save_tooth_condition(patient_id, tooth_number, surface, condition, notes=""):
    """Saves surface or tooth condition on the dental chart."""
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
    """Saves periodontal probing and mobility findings for a tooth."""
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


def add_patient_xray(patient_id, image_type, description, date_taken, image_bytes):
    """Saves an X-ray binary BLOB image record."""
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
    """Retrieves binary BLOB data for an X-ray."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_data FROM xrays WHERE id = ?;", (xray_id,))
    row = cursor.fetchone()
    conn.close()
    return row['image_data'] if row else None


def delete_xray(xray_id):
    """Deletes an X-ray record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM xrays WHERE id = ?;", (xray_id,))
    conn.commit()
    conn.close()
    return True
