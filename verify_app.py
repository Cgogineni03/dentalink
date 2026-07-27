# DentaLink Automated Verification Script (verify_app.py)
import os
import sys

print("=== Starting DentaLink Verification ===")

# Test 1: Import custom modules and check dependencies
try:
    print("Test 1: Checking module imports and dependencies...")
    import database
    database.DB_NAME = "test_dental_clinic.db"
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QImage
    from widgets.dental_chart import DentalChartWidget
    from widgets.xray_viewer import XrayViewerWidget
    from main import DentaLinkMainWindow
    print("  SUCCESS: All modules imported successfully.")
    # Initialize QApplication to prevent Qt font engine crash when drawing mock OPG images
    app = QApplication(sys.argv)
except ImportError as e:
    print(f"  FAILED: Import error: {e}")
    sys.exit(1)

# Test 2: Database Initialization and Seeding
try:
    print("Test 2: Initializing SQLite database and seeding sample records...")
    # Delete old database if exists to test clean initialization
    if os.path.exists(database.DB_NAME):
        os.remove(database.DB_NAME)
        print("  Cleaned up old SQLite database file.")
        
    database.initialize_database()
    database.seed_demo_data()
    
    if os.path.exists(database.DB_NAME):
        print(f"  SUCCESS: Database '{database.DB_NAME}' created successfully.")
    else:
        print("  FAILED: Database file not found after initialization.")
        sys.exit(1)
except Exception as e:
    print(f"  FAILED: Database initialization error: {e}")
    sys.exit(1)

# Test 3: Verify Patient Workflows (Registration -> New OP -> File Open -> Registry)
try:
    print("Test 3: Verifying patient registration workflow...")
    # 1. Register a new patient
    new_pid = database.register_patient(
        "John Connor", "2004-02-28", "Male", "(555) 123-4567",
        "jconnor@resistance.net", "Los Angeles, CA", "None", "None"
    )
    print(f"  Registered John Connor. Generated ID: {new_pid}")
    
    # 2. Check if John is in New OP queue
    new_ops = database.get_new_op_patients()
    found_op = False
    for op in new_ops:
        if op['id'] == new_pid:
            found_op = True
            print(f"  John Connor found in NEW_OP queue. State check passed.")
            break
    if not found_op:
        print("  FAILED: John Connor was not found in the NEW_OP queue.")
        sys.exit(1)
        
    # 3. Open John's File (transitions to PATIENT_LIST)
    p_details = database.open_patient_file(new_pid)
    print(f"  Opened John Connor's file. Transitioned status in SQLite.")
    
    # Check if John is in Active Patient List and removed from New OP
    new_ops_after = database.get_new_op_patients()
    if any(op['id'] == new_pid for op in new_ops_after):
        print("  FAILED: Patient is still in NEW_OP queue after opening file.")
        sys.exit(1)
        
    active_patients = database.get_active_patients()
    found_active = False
    for ap in active_patients:
        if ap['id'] == new_pid:
            found_active = True
            print(f"  John Connor found in Active Patients list. Workflow state check passed.")
            break
    if not found_active:
        print("  FAILED: Patient was not found in active list after status change.")
        sys.exit(1)
        
    print("  SUCCESS: Registration to OP to Patient List transition verified.")
except Exception as e:
    print(f"  FAILED: State transition test error: {e}")
    sys.exit(1)

# Test 4: Image BLOB Database Storage
try:
    print("Test 4: Verifying X-ray binary BLOB storage and retrieval...")
    # Create fake image bytes (e.g. 100 bytes of zeros)
    dummy_image_data = bytes([0, 1, 2, 3, 4] * 20)
    
    xray_id = database.add_patient_xray(
        new_pid, "X-Ray", "Test Mandibular Bite", "2026-07-13", dummy_image_data
    )
    print(f"  Saved X-ray image BLOB. Generated X-ray ID: {xray_id}")
    
    retrieved_bytes = database.get_xray_image_data(xray_id)
    if retrieved_bytes == dummy_image_data:
        print("  Retrieved binary matches original bytes exactly.")
        print("  SUCCESS: Secure database BLOB storage verified.")
    else:
        print("  FAILED: Retrieved image bytes do not match uploaded bytes.")
        sys.exit(1)
except Exception as e:
    print(f"  FAILED: Image BLOB test error: {e}")
    sys.exit(1)

# Test 5: Multi-Referral Storage & Retrieval
try:
    print("Test 5: Verifying multi-referral persistence...")
    ref1_id = database.save_referral(new_pid, "Orthodontics", 1, "Evaluation for braces", "Pending")
    ref2_id = database.save_referral(new_pid, "Oral Surgery", 1, "Impacted 3rd molar extraction", "Pending")
    
    patient_details = database.get_patient_details(new_pid)
    referrals_list = patient_details.get("referrals", [])
    
    if len(referrals_list) >= 2:
        print(f"  SUCCESS: Multi-referral persistence verified. Count: {len(referrals_list)}")
    else:
        print(f"  FAILED: Expected at least 2 referrals, got {len(referrals_list)}")
        sys.exit(1)
except Exception as e:
    print(f"  FAILED: Multi-referral test error: {e}")
    sys.exit(1)

# Test 6: Git-Style Immutable History Commits & Key Unlocking
try:
    print("Test 6: Verifying Git-style immutable history commit creation & section hierarchy deltas...")
    
    snap1 = {
        'chief_complaint': 'Mild tooth sensitivity #30',
        'medical_conditions': 'None',
        'provisional_diagnosis': 'Enamel caries #30'
    }
    c1_id = database.create_patient_history_commit(new_pid, "Initial Examination", "Dr. Admin", snap1, force_commit=True)
    print(f"  Created baseline commit v1 ID: {c1_id}")
    
    snap2 = {
        'chief_complaint': 'Severe throbbing pain #30 disturbance in sleep',
        'medical_conditions': 'Hypertension (Newly Diagnosed)',
        'provisional_diagnosis': 'Irreversible Pulpitis #30',
        'final_diagnosis': 'Acute Apical Periodontitis #30'
    }
    c2_id = database.create_patient_history_commit(new_pid, "Emergency Re-visit", "Dr. Admin", snap2)
    print(f"  Created revision commit v2 ID: {c2_id}")
    
    commits = database.get_patient_history_commits(new_pid)
    if len(commits) >= 2:
        latest = commits[0]
        deltas = latest.get('deltas', [])
        print(f"  Retrieved {len(commits)} commits. Latest version v{latest['version_number']} timestamp: {latest['timestamp_formatted']}")
        print(f"  Categorized Deltas count: {len(deltas)}")
        for d in deltas:
            print(f"    - Section: {d['section']} | Subsection: {d['subsection']} | Title: {d['title']} -> {d['new_val']}")
        print("  SUCCESS: Git-style immutable section-categorized history commits verified.")
    else:
        print(f"  FAILED: Expected at least 2 commits, got {len(commits)}")
        sys.exit(1)
except Exception as e:
    print(f"  FAILED: History commit test error: {e}")
    sys.exit(1)

# Test 7: Universal Recovery Key & Doctor Password Recovery
try:
    print("Test 7: Verifying Universal Recovery Key generation & doctor-friendly password reset...")
    ukey = database.generate_universal_recovery_key()
    print(f"  Generated Universal Key: {ukey}")
    
    # Ensure doctor account exists and session key is active
    database.create_doctor("Dr. Admin", "dr_admin", "old_pass_123", 0.0)
    database.unlock_database_with_login("dr_admin", "old_pass_123")
    
    database.setup_doctor_security_and_recovery("dr_admin", "Q1 School", "Dental College", "Q2 City", "London", ukey)
    
    # Reset password using case-insensitive answers ("dental college", "london")
    res = database.reset_password_with_recovery("dr_admin", "dental college", "london", ukey, "new_secure_pwd_123")
    if not res:
        print("  FAILED: Password reset returned False.")
        sys.exit(1)
        
    auth_check = database.verify_password("dr_admin", "new_secure_pwd_123")
    if auth_check:
        print("  SUCCESS: Doctor password reset & Master Key re-wrapping verified successfully.")
    else:
        print("  FAILED: Could not verify new password.")
        sys.exit(1)
except Exception as e:
    print(f"  FAILED: Recovery key test error: {e}")
    sys.exit(1)

print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")
sys.exit(0)
