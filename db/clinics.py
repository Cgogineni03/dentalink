# DentaLink Clinic & Doctor Authentication & Profile Management
import hashlib
import hmac
import os
import sqlite3

from db.connection import get_db_connection
from db.crypto import (
    compute_hmac,
    decrypt_payload,
    derive_key,
    encrypt_payload,
    get_active_session_cmk,
    hash_answer,
    normalize_answer,
    normalize_recovery_key,
    set_active_session_cmk,
)


def verify_password(username, password):
    """Verifies credentials for doctor or clinic admin."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Check doctors table
    cursor.execute("SELECT id, name, password_hash, salt FROM doctors WHERE username = ?;", (username,))
    row = cursor.fetchone()
    is_admin = False

    # 2. Check clinics table if not found in doctors
    if not row:
        cursor.execute("SELECT id, name, password_hash, salt FROM clinics WHERE username = ?;", (username,))
        row = cursor.fetchone()
        is_admin = True

    conn.close()

    if not row:
        return None

    salt = bytes.fromhex(row['salt'])
    stored_hash = row['password_hash']
    computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

    if hmac.compare_digest(computed_hash, stored_hash):
        display_name = f"{row['name']} (Admin)" if is_admin else row['name']
        return {'id': row['id'], 'name': display_name, 'username': username, 'is_admin': is_admin}
    return None


def verify_admin_password(password):
    """Verifies password for the clinic admin account in the clinics table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt FROM clinics ORDER BY id ASC LIMIT 1;")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    salt = bytes.fromhex(row['salt'])
    stored_hash = row['password_hash']
    computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()
    return hmac.compare_digest(computed_hash, stored_hash)


def get_clinic_profile(username):
    """Fetches basic clinic profile info."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, username FROM clinics WHERE username = ?;", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def has_doctors():
    """Checks if any doctor account exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM doctors;")
    result = cursor.fetchone()[0] > 0
    conn.close()
    return result


def has_clinics():
    """Checks if any clinic admin account exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clinics;")
    result = cursor.fetchone()[0] > 0
    conn.close()
    return result


def create_clinic(name, username, password, logo_path=""):
    """Registers a new clinic admin account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    salt = os.urandom(16).hex()
    hashed_pw = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100000).hex()
    try:
        cursor.execute("INSERT INTO clinics (name, username, password_hash, salt, logo_path) VALUES (?, ?, ?, ?, ?);",
                       (name, username, hashed_pw, salt, logo_path))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success


def update_clinic_profile(old_username, new_name, new_username, new_password=None):
    """Updates clinic profile details and optionally password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if new_password:
        salt = os.urandom(16).hex()
        hashed_pw = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), bytes.fromhex(salt), 100000).hex()
        cursor.execute("UPDATE clinics SET name = ?, username = ?, password_hash = ?, salt = ? WHERE username = ?;",
                       (new_name, new_username, hashed_pw, salt, old_username))
    else:
        cursor.execute("UPDATE clinics SET name = ?, username = ? WHERE username = ?;", (new_name, new_username, old_username))
    conn.commit()
    conn.close()


def get_doctors():
    """Retrieves list of all registered doctors."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, discount_pct FROM doctors ORDER BY name ASC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def create_doctor(name, username, password, discount_pct=0.0):
    """Registers a new doctor account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    salt = os.urandom(16).hex()
    hashed_pw = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100000).hex()
    try:
        cursor.execute("INSERT INTO doctors (name, username, password_hash, salt, discount_pct) VALUES (?, ?, ?, ?, ?);",
                       (name, username, hashed_pw, salt, discount_pct))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success


def update_patient_doctor(patient_id, doctor_id):
    """Assigns a doctor to a patient."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE patients SET assigned_doctor_id = ? WHERE id = ?;", (doctor_id, patient_id))
    conn.commit()
    conn.close()


def get_clinic_logo_path():
    """Gets clinic logo filepath."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT logo_path FROM clinics LIMIT 1;")
    row = cursor.fetchone()
    conn.close()
    return row['logo_path'] if row else ''


def save_clinic_logo_path(logo_path):
    """Saves clinic logo filepath."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clinics SET logo_path = ?;", (logo_path,))
    conn.commit()
    conn.close()


def unlock_database_with_login(username, password):
    """Unlocks the database session key upon user authentication."""
    user = verify_password(username, password)
    if not user:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    target_table = "doctors"
    cursor.execute("SELECT salt, master_key_wrapper FROM doctors WHERE username = ?;", (username,))
    row = cursor.fetchone()
    if not row:
        target_table = "clinics"
        cursor.execute("SELECT salt, master_key_wrapper FROM clinics WHERE username = ?;", (username,))
        row = cursor.fetchone()

    salt = bytes.fromhex(row['salt']) if (row and row['salt']) else b"DENTA_LINK_DEFAULT_SALT_256"
    user_key = derive_key(password, salt)

    if row and row['master_key_wrapper']:
        try:
            cmk_hex = decrypt_payload(row['master_key_wrapper'], user_key)
            if cmk_hex and isinstance(cmk_hex, str):
                set_active_session_cmk(bytes.fromhex(cmk_hex))
            else:
                set_active_session_cmk(user_key)
        except Exception:
            set_active_session_cmk(user_key)
    else:
        cmk_bytes = os.urandom(32)
        set_active_session_cmk(cmk_bytes)
        wrapper_str = encrypt_payload(cmk_bytes.hex(), user_key)
        if target_table == "doctors":
            cursor.execute("UPDATE doctors SET master_key_wrapper = ? WHERE username = ?;", (wrapper_str, username))
        else:
            cursor.execute("UPDATE clinics SET master_key_wrapper = ? WHERE username = ?;", (wrapper_str, username))
        conn.commit()

    conn.close()
    return True


def setup_doctor_security_and_recovery(username, q1, a1, q2, a2, universal_key):
    """Sets up doctor security questions and wraps Master CMK with Universal Key."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT salt, master_key_wrapper FROM doctors WHERE username = ?;", (username,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    salt = bytes.fromhex(row['salt'])
    hash_a1 = hash_answer(a1, salt)
    hash_a2 = hash_answer(a2, salt)

    clean_ukey = normalize_recovery_key(universal_key)
    rec_secret = f"{clean_ukey}:{normalize_answer(a1)}:{normalize_answer(a2)}"
    recovery_key = derive_key(rec_secret, salt)

    cmk = get_active_session_cmk()
    cmk_hex = cmk.hex() if cmk else b"DENTA_LINK_MASTER_CMK_SESSION_256".hex()
    rec_wrapper = encrypt_payload(cmk_hex, recovery_key)

    cursor.execute("""
        UPDATE doctors 
        SET security_q1 = ?, security_a1 = ?, security_q2 = ?, security_a2 = ?, universal_recovery_wrapper = ?
        WHERE username = ?;
    """, (q1, hash_a1, q2, hash_a2, rec_wrapper, username))

    uk_hash = hashlib.sha256(clean_ukey.encode('utf-8')).hexdigest()
    cursor.execute("UPDATE clinics SET universal_recovery_key_hash = ?;", (uk_hash,))

    conn.commit()
    conn.close()
    return True


def get_doctor_security_questions(username):
    """Retrieves configured security questions for a doctor username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT security_q1, security_q2 FROM doctors WHERE username = ?;", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row['security_q1'] and row['security_q2']:
        return (row['security_q1'], row['security_q2'])
    return ("What was the name of your first school/college?", "What city were you born in?")


def unlock_database_with_recovery_keys(username, a1, a2, universal_key):
    """Unlocks CMK using Case-Insensitive Security Answers + Universal Key."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT salt, security_a1, security_a2, universal_recovery_wrapper FROM doctors WHERE username = ?;", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    salt = bytes.fromhex(row['salt'])
    if row['security_a1'] and row['security_a1'] != hash_answer(a1, salt):
        return False
    if row['security_a2'] and row['security_a2'] != hash_answer(a2, salt):
        return False

    clean_ukey = normalize_recovery_key(universal_key)
    rec_secret = f"{clean_ukey}:{normalize_answer(a1)}:{normalize_answer(a2)}"
    recovery_key = derive_key(rec_secret, salt)

    if row['universal_recovery_wrapper']:
        try:
            cmk_hex = decrypt_payload(row['universal_recovery_wrapper'], recovery_key)
            if cmk_hex and isinstance(cmk_hex, str):
                set_active_session_cmk(bytes.fromhex(cmk_hex))
                return True
        except Exception:
            pass

    set_active_session_cmk(recovery_key)
    return True


def reset_password_with_recovery(username, a1, a2, universal_key, new_password):
    """Resets doctor password and re-wraps Master CMK without data loss."""
    if not unlock_database_with_recovery_keys(username, a1, a2, universal_key):
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    new_salt = os.urandom(16).hex()
    new_hash = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), bytes.fromhex(new_salt), 100000).hex()

    user_key = derive_key(new_password, bytes.fromhex(new_salt))
    cmk = get_active_session_cmk()
    cmk_hex = cmk.hex() if cmk else b"DENTA_LINK_MASTER_CMK_SESSION_256".hex()
    new_doc_wrapper = encrypt_payload(cmk_hex, user_key)

    cursor.execute("""
        UPDATE doctors 
        SET password_hash = ?, salt = ?, master_key_wrapper = ?
        WHERE username = ?;
    """, (new_hash, new_salt, new_doc_wrapper, username))

    conn.commit()
    conn.close()
    return True


def get_clinic_details():
    """Fetches clinic setup information."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, logo_path, address, phone, email, department, tagline FROM clinics ORDER BY id ASC LIMIT 1;")
        row = cursor.fetchone()
    except sqlite3.OperationalError:
        row = None
    conn.close()

    if row:
        d = dict(row)
        return {
            "name": d.get("name") or "Dental Care & Specialty Clinic",
            "logo_path": d.get("logo_path") or "",
            "address": d.get("address") or "Main Road, Medical District, City - 520002",
            "phone": d.get("phone") or "+91 98480 12345",
            "email": d.get("email") or "info@dentalclinic.com",
            "department": d.get("department") or "Department of Dental Surgery & Diagnostics",
            "tagline": d.get("tagline") or "Advanced Dental Care & Patient Management"
        }
    return {
        "name": "Dental Care & Specialty Clinic",
        "logo_path": "",
        "address": "Main Road, Medical District, City - 520002",
        "phone": "+91 98480 12345",
        "email": "info@dentalclinic.com",
        "department": "Department of Dental Surgery & Diagnostics",
        "tagline": "Advanced Dental Care & Patient Management"
    }


def save_clinic_details(name=None, address=None, phone=None, email=None, department=None, tagline=None, logo_path=None):
    """Updates active clinic profile setup details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clinics ORDER BY id ASC LIMIT 1;")
    row = cursor.fetchone()
    if row:
        cid = row['id']
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if address is not None:
            updates.append("address = ?")
            params.append(address)
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if department is not None:
            updates.append("department = ?")
            params.append(department)
        if tagline is not None:
            updates.append("tagline = ?")
            params.append(tagline)
        if logo_path is not None:
            updates.append("logo_path = ?")
            params.append(logo_path)

        if updates:
            params.append(cid)
            sql = f"UPDATE clinics SET {', '.join(updates)} WHERE id = ?;"
            cursor.execute(sql, tuple(params))
            conn.commit()
    conn.close()
