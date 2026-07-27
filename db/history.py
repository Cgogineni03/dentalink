# DentaLink Immutable Git-Style Patient Record Version Control
from datetime import datetime
import hashlib
import os

from db.connection import get_db_connection
from db.crypto import compute_hmac, decrypt_payload, encrypt_payload


def compute_structured_delta(old_snapshot, new_snapshot):
    """Calculates changes categorized under Section > Subsection > Title."""
    field_mappings = [
        ('medical_conditions', 'Demographics & Medical', 'Medical Conditions', 'Pre-existing Conditions'),
        ('allergies', 'Demographics & Medical', 'Medical Conditions', 'Allergies'),
        ('occupation', 'Demographics & Medical', 'Demographic Info', 'Occupation'),
        ('chief_complaint', 'Clinical Findings', 'History of Present Illness', 'Chief Complaint'),
        ('hpi', 'Clinical Findings', 'History of Present Illness', 'HPI Details'),
        ('past_dental_history', 'Clinical Findings', 'Dental History', 'Past Dental History'),
        ('past_medical_history', 'Clinical Findings', 'Medical History', 'Past Medical History'),
        ('clinical_findings', 'Clinical Findings', 'Examination', 'Clinical Findings'),
        ('provisional_diagnosis', 'Diagnoses & Plan', 'Clinical Diagnoses', 'Provisional Diagnosis'),
        ('differential_diagnosis', 'Diagnoses & Plan', 'Clinical Diagnoses', 'Differential Diagnosis'),
        ('final_diagnosis', 'Diagnoses & Plan', 'Clinical Diagnoses', 'Final Diagnosis'),
        ('note', 'Diagnoses & Plan', 'Clinical Diagnoses', 'Diagnosis Notes'),
    ]

    deltas = []
    for key, section, subsection, title in field_mappings:
        old_val = str(old_snapshot.get(key, '') or '').strip()
        new_val = str(new_snapshot.get(key, '') or '').strip()
        if old_val != new_val:
            deltas.append({
                'section': section,
                'subsection': subsection,
                'title': title,
                'old_val': old_val,
                'new_val': new_val
            })
    return deltas


def create_patient_history_commit(patient_id, commit_message, doctor_name, new_snapshot_data, force_commit=False):
    """Creates an immutable, signed, encrypted history commit with section hierarchy deltas."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM patient_history_commits 
        WHERE patient_id = ? 
        ORDER BY id DESC LIMIT 1;
    """, (patient_id,))
    last_row = cursor.fetchone()

    parent_commit_id = last_row['id'] if last_row else None
    version_number = (last_row['version_number'] + 1) if last_row else 1

    old_snapshot = {}
    if last_row and last_row['encrypted_snapshot']:
        old_snapshot = decrypt_payload(last_row['encrypted_snapshot'])

    deltas = compute_structured_delta(old_snapshot, new_snapshot_data)
    if not deltas and not force_commit and last_row:
        conn.close()
        return None

    timestamp_str = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    hash_raw = f"{patient_id}_{version_number}_{timestamp_str}_{os.urandom(8).hex()}"
    commit_hash = hashlib.sha256(hash_raw.encode('utf-8')).hexdigest()[:8]

    enc_deltas = encrypt_payload(deltas)
    enc_snapshot = encrypt_payload(new_snapshot_data)

    hmac_signature = compute_hmac(f"{commit_hash}:{patient_id}:{version_number}:{timestamp_str}")

    cursor.execute("""
        INSERT INTO patient_history_commits (
            commit_hash, patient_id, version_number, parent_commit_id,
            commit_message, doctor_name, timestamp_formatted,
            encrypted_delta_json, encrypted_snapshot, hmac_signature
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (commit_hash, patient_id, version_number, parent_commit_id,
          commit_message, doctor_name, timestamp_str,
          enc_deltas, enc_snapshot, hmac_signature))

    commit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return commit_id


def get_patient_history_commits(patient_id):
    """Retrieves all immutable history commits for a patient ordered by version number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM patient_history_commits 
        WHERE patient_id = ? 
        ORDER BY version_number ASC, id ASC;
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()

    commits = []
    for r in rows:
        c = dict(r)
        c['deltas'] = decrypt_payload(c['encrypted_delta_json'])
        c['snapshot'] = decrypt_payload(c['encrypted_snapshot'])
        expected_hmac = compute_hmac(f"{c['commit_hash']}:{c['patient_id']}:{c['version_number']}:{c['timestamp_formatted']}")
        c['is_verified'] = (c['hmac_signature'] == expected_hmac)
        commits.append(c)

    return commits
