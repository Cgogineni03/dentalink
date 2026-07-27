# DentaLink Referral Management Database Operations
from db.connection import get_db_connection


def add_referral(patient_id, referred_to_dept, referred_to_doctor_id, referral_reason, referral_status):
    """Creates a department or doctor referral record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO referrals (patient_id, referred_to_dept, referred_to_doctor_id, referral_reason, referral_status)
        VALUES (?, ?, ?, ?, ?);
    """, (patient_id, referred_to_dept, referred_to_doctor_id, referral_reason, referral_status))
    ref_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ref_id


save_referral = add_referral


def delete_referral(referral_id):
    """Deletes a referral record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM referrals WHERE id = ?;", (referral_id,))
    conn.commit()
    conn.close()
