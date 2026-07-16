# DentaLink Automated Verification Script (verify_app.py)
import os
import sys

print("=== Starting DentaLink Verification ===")

# Test 1: Import custom modules and check dependencies
try:
    print("Test 1: Checking module imports and dependencies...")
    import database
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

print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")
sys.exit(0)
