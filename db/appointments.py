# DentaLink Appointments Scheduling Database Operations
from db.connection import get_db_connection


def add_appointment(patient_id, app_date, app_time, reason, status="Yet to visit"):
    """Schedules a new appointment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments (patient_id, app_date, app_time, reason, status)
        VALUES (?, ?, ?, ?, ?);
    """, (patient_id, app_date, app_time, reason, status))
    conn.commit()
    conn.close()


def delete_appointment(app_id):
    """Deletes an appointment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?;", (app_id,))
    conn.commit()
    conn.close()


def update_appointment_status(app_id, status, visited_on=""):
    """Updates status (e.g. Visited, Cancelled, Yet to visit) for an appointment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments 
        SET status = ?, visited_on = ?
        WHERE id = ?;
    """, (status, visited_on, app_id))
    conn.commit()
    conn.close()


def get_upcoming_appointments(limit=10):
    """Retrieves upcoming 'Yet to visit' appointments across all patients."""
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
