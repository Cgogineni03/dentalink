# DentaLink Database Layer (database.py Facade)
"""
Root facade for database operations. Re-exports all public API functions from
the modular `db` package to ensure 100% backward compatibility.
"""

from db.appointments import (
    add_appointment,
    delete_appointment,
    get_upcoming_appointments,
    update_appointment_status,
)
from db.clinical import (
    add_investigation,
    add_local_examination,
    add_pathology_requisition,
    add_patient_xray,
    add_prescription,
    add_treatment_done,
    add_treatment_needed,
    delete_investigation,
    delete_local_examination,
    delete_pathology_requisition,
    delete_prescription,
    delete_treatment_done,
    delete_treatment_needed,
    delete_xray,
    get_xray_image_data,
    pay_treatment_needed_bill,
    save_deleterious_habits,
    save_diagnosis,
    save_extra_oral_exam,
    save_intra_oral_exam,
    save_investigation_reports,
    save_perio_status,
    save_tooth_condition,
    save_treatment,
    save_treatment_plan,
    update_case_history,
)
from db.clinics import (
    create_clinic,
    create_doctor,
    get_clinic_details,
    get_clinic_logo_path,
    get_clinic_profile,
    get_doctor_security_questions,
    get_doctors,
    has_clinics,
    has_doctors,
    reset_password_with_recovery,
    save_clinic_details,
    save_clinic_logo_path,
    setup_doctor_security_and_recovery,
    unlock_database_with_login,
    unlock_database_with_recovery_keys,
    update_clinic_profile,
    update_patient_doctor,
    verify_admin_password,
    verify_password,
)
from db.connection import (
    DB_NAME,
    get_db_connection,
    initialize_database,
    vacuum_database,
)
from db.crypto import (
    ACTIVE_SESSION_CMK,
    compute_hmac,
    decrypt_payload,
    derive_key,
    encrypt_payload,
    generate_universal_recovery_key,
    hash_answer,
    normalize_answer,
    normalize_recovery_key,
    xor_crypt,
)
from db.history import (
    compute_structured_delta,
    create_patient_history_commit,
    get_patient_history_commits,
)
from db.patients import (
    add_patient_file,
    delete_patient_file,
    get_active_patients,
    get_new_op_patients,
    get_patient_details,
    get_patient_file,
    get_patient_files,
    open_patient_file,
    register_patient,
    update_patient_banner_fields,
)
from db.procedural_graphics import (
    generate_procedural_extraoral_photo_bytes,
    generate_procedural_intraoral_photo_bytes,
    generate_procedural_opg_fracture_bytes,
    generate_procedural_xray_bytes,
)
from db.referrals import (
    add_referral,
    delete_referral,
)
from db.seeding import (
    seed_demo_data,
    seed_detailed_mock_data,
)

# Function Aliases for Backward Compatibility
save_referral = add_referral
save_local_examination = add_local_examination
save_investigation = add_investigation
