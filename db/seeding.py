# DentaLink Database Seed Generators for Demo & Initial Setup
import hashlib
import os

from db.connection import get_db_connection
from db.crypto import (
    derive_key,
    encrypt_payload,
    generate_universal_recovery_key,
    normalize_answer,
)
from db.procedural_graphics import (
    generate_procedural_opg_fracture_bytes,
    generate_procedural_xray_bytes,
)


def seed_demo_data(conn=None):
    """Seeds default clinic, doctor, and mock patient records for testing/demonstration."""
    close_at_end = False
    if conn is None:
        conn = get_db_connection()
        close_at_end = True

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM doctors;")
    has_doctors_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM clinics;")
    has_clinics_cnt = cursor.fetchone()[0]

    if has_clinics_cnt == 0:
        salt_c = os.urandom(16).hex()
        hash_c = hashlib.pbkdf2_hmac('sha256', "admin123".encode('utf-8'), bytes.fromhex(salt_c), 100000).hex()
        cursor.execute("INSERT INTO clinics (name, username, password_hash, salt) VALUES (?, ?, ?, ?);",
                       ("DentaLink Dental Clinic", "admin", hash_c, salt_c))
        conn.commit()

    if has_doctors_cnt == 0:
        salt_d = os.urandom(16).hex()
        hash_d = hashlib.pbkdf2_hmac('sha256', "admin123".encode('utf-8'), bytes.fromhex(salt_d), 100000).hex()
        user_key = derive_key("admin123", bytes.fromhex(salt_d))
        cmk_hex = b"DENTA_LINK_MASTER_CMK_SESSION_256".hex()
        doc_wrapper = encrypt_payload(cmk_hex, user_key)

        ukey = generate_universal_recovery_key()
        norm_a1 = normalize_answer("Medical College")
        norm_a2 = normalize_answer("London")
        hash_a1 = hashlib.pbkdf2_hmac('sha256', norm_a1.encode('utf-8'), bytes.fromhex(salt_d), 100000).hex()
        hash_a2 = hashlib.pbkdf2_hmac('sha256', norm_a2.encode('utf-8'), bytes.fromhex(salt_d), 100000).hex()
        rec_secret = f"{ukey.strip()}:{norm_a1}:{norm_a2}"
        rec_key = derive_key(rec_secret, bytes.fromhex(salt_d))
        rec_wrapper = encrypt_payload(cmk_hex, rec_key)

        cursor.execute("""
            INSERT INTO doctors (name, username, password_hash, salt, discount_pct, master_key_wrapper,
                                 security_q1, security_a1, security_q2, security_a2, universal_recovery_wrapper)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, ("Dr. Admin", "dr_admin", hash_d, salt_d, 0.0, doc_wrapper,
              "What was the name of your first school/college?", hash_a1,
              "What city were you born in?", hash_a2, rec_wrapper))
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM patients;")
    if cursor.fetchone()[0] == 0:
        seed_detailed_mock_data(conn)

    if close_at_end:
        conn.close()


def seed_detailed_mock_data(conn):
    """Seeds rich mock clinical cases."""
    cursor = conn.cursor()

    patients_data = [
        {
            "name": "CH. KRISHNA PRASAD",
            "dob": "1966-03-12",
            "gender": "Male",
            "phone": "9963123498",
            "email": "krishnaprasad@gmail.com",
            "address": "D.No 4-12, Main Road",
            "village": "Thulluru",
            "occupation": "Farmer",
            "allergies": "None",
            "medical_conditions": "Diabetes Milletus (15 yrs)",
            "status": "PATIENT_LIST",
            "op_no": "202606220194",
            "crn": "OMR260622189",
            "cc": "Patient complains of sensitivity of tooth since 1 week",
            "hpi": "Patient complains of sensitivity of tooth since 1 week in upper and lower posterior regions during cold food and liquids intake.",
            "past_med": "Diabetes Milletus - Since 15 yrs under medication (Metformin 500mg BD)",
            "past_dent": "Nrh",
            "habits": "Absent",
            "diet": "Veg",
            "sleep": "Normal",
            "lymph_node": "Palpable",
            "eoe": {"lymph_node_left_size": "", "lymph_node_right_size": "", "lymph_node_left_consistency": "/", "lymph_node_right_consistency": "/"},
            "ioe": {"wasting_attrition": "Generalised", "hypoplasia": "Absent", "labial_mucosa": "Apparently Normal", "buccal_mucosa": "Apparently Normal", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Apparently Normal", "lingual_mucosa": "Apparently Normal", "palatal_mucosa": "Apparently Normal", "salivary_duct": "Patent"},
            "chart": [("15", "ALL", "root-canal", "RS"), ("14", "ALL", "root-canal", "RS"), ("26", "ALL", "crown", "FD"), ("27", "ALL", "crown", "FD"), ("28", "ALL", "root-canal", "RS")],
            "prov_diag": "Chronic irreversible pulpitis irt 26,27,14,15, Chronic generalised gingivitis",
            "final_diag": "Chronic irreversible pulpitis irt 26,27,14,15, Chronic generalised gingivitis",
            "inv": [("IOPA - X-Ray (Digital)", "26,27,14,15", 2, 60.00, 60.00, "2627/707508", "2026-06-22")],
            "ref": [("OPD", "OMR", "Referral for OMR evaluation", "Visited", "2026-06-22")],
            "xrays": [("IOPA - Digital X-Ray", "Root apex view teeth 26,27", "2026-06-22"), ("IOPA - Digital X-Ray", "Root apex view teeth 14,15", "2026-06-22")]
        },
        {
            "name": "ANITHA REDDY",
            "dob": "1992-08-25",
            "gender": "Female",
            "phone": "9848022334",
            "email": "anitha.reddy@yahoo.com",
            "address": "Plot 45, Benz Circle",
            "village": "Vijayawada",
            "occupation": "Teacher",
            "allergies": "Penicillin",
            "medical_conditions": "Hypertension",
            "status": "PATIENT_LIST",
            "op_no": "202606220195",
            "crn": "OMR260622190",
            "cc": "Severe throbbing pain in lower left molar tooth since 3 days.",
            "hpi": "Pain aggravated during chewing and lying down. Mild localized swelling in lower left cheek.",
            "past_med": "Hypertension (Under medication Amlodipine 5mg QD)",
            "past_dent": "Composite restoration on 36 done 1 year ago.",
            "habits": "Absent",
            "diet": "Non-Veg",
            "sleep": "Disturbed",
            "lymph_node": "Palpable",
            "eoe": {"lymph_node_left_size": "1.0 cm", "lymph_node_right_size": "", "lymph_node_left_consistency": "Soft", "lymph_node_right_consistency": "/"},
            "ioe": {"wasting_attrition": "Localized 36", "hypoplasia": "Absent", "labial_mucosa": "Apparently Normal", "buccal_mucosa": "Localized swelling irt 36", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Tender irt 36", "lingual_mucosa": "Apparently Normal", "palatal_mucosa": "Apparently Normal", "salivary_duct": "Patent"},
            "chart": [("36", "ALL", "decay", "RCT Needed"), ("37", "ALL", "decay", "Deep Cavity"), ("16", "ALL", "filled", "F")],
            "prov_diag": "Acute periapical abscess irt 36",
            "final_diag": "Acute periapical abscess irt 36",
            "inv": [("IOPA - X-Ray (Digital)", "36", 1, 30.00, 30.00, "3601/707509", "2026-06-23")],
            "ref": [("OPD", "Endodontics", "Root canal therapy", "Visited", "2026-06-23")],
            "xrays": [("IOPA - Digital X-Ray", "Periapical radiolucency tooth 36", "2026-06-23")]
        },
        {
            "name": "VENKATESWARA RAO",
            "dob": "1974-05-18",
            "gender": "Male",
            "phone": "9440188776",
            "email": "venkat.rao52@gmail.com",
            "address": "Door No 12-8, Arundelpet",
            "village": "Guntur",
            "occupation": "Business",
            "allergies": "None",
            "medical_conditions": "Type 2 Diabetes Mellitus",
            "status": "PATIENT_LIST",
            "op_no": "202606220196",
            "crn": "OMR260622191",
            "cc": "Loosening of lower front teeth and bleeding gums while brushing since 6 months.",
            "hpi": "Gradual progression of mobility in lower anterior teeth. Difficulty in biting hard food.",
            "past_med": "Type 2 Diabetes Mellitus (HbA1c 7.8%)",
            "past_dent": "Oral scaling done 3 years ago.",
            "habits": "Tobacco chewing for 10 years",
            "diet": "Mixed",
            "sleep": "Normal",
            "lymph_node": "Non-palpable",
            "eoe": {"lymph_node_left_size": "", "lymph_node_right_size": "", "lymph_node_left_consistency": "/", "lymph_node_right_consistency": "/"},
            "ioe": {"wasting_attrition": "Moderate generalised", "hypoplasia": "Absent", "labial_mucosa": "Recession lower anteriors", "buccal_mucosa": "Apparently Normal", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Apparently Normal", "lingual_mucosa": "Heavy calculus", "palatal_mucosa": "Apparently Normal", "salivary_duct": "Patent"},
            "chart": [("31", "ALL", "missing", "Grade II Mobility"), ("32", "ALL", "missing", "Grade II Mobility"), ("41", "ALL", "missing", "Grade II Mobility"), ("42", "ALL", "missing", "Grade II Mobility")],
            "prov_diag": "Generalized chronic severe periodontitis with Grade II mobility irt 31,32,41,42",
            "final_diag": "Generalized severe chronic periodontitis",
            "inv": [("OPG - Panoramic Radiograph", "All", 1, 350.00, 350.00, "9910/707510", "2026-06-24")],
            "ref": [("OPD", "Periodontics", "Full mouth scaling & root planing", "Visited", "2026-06-24")],
            "xrays": [("OPG - Panoramic Scan", "Generalized horizontal bone loss maxilla & mandible", "2026-06-24")]
        },
        {
            "name": "LAKSHMI DEVI",
            "dob": "1981-11-04",
            "gender": "Female",
            "phone": "9989011223",
            "email": "lakshmi.devi@gmail.com",
            "address": "Flat 201, RTC Colony",
            "village": "Tenali",
            "occupation": "Homemaker",
            "allergies": "Sulfa drugs",
            "medical_conditions": "Hypothyroidism",
            "status": "NEW_OP",
            "op_no": "202606220197",
            "crn": "OMR260622192",
            "cc": "White burning patch on inner cheek since 2 months.",
            "hpi": "Burning sensation while eating spicy food. Noticed white reticular lines on right buccal mucosa.",
            "past_med": "Hypothyroidism (Thyronorm 50mcg daily)",
            "past_dent": "Regular checkups",
            "habits": "Absent",
            "diet": "Veg",
            "sleep": "Normal",
            "lymph_node": "Non-palpable",
            "eoe": {"lymph_node_left_size": "", "lymph_node_right_size": "", "lymph_node_left_consistency": "/", "lymph_node_right_consistency": "/"},
            "ioe": {"wasting_attrition": "Mild", "hypoplasia": "Absent", "labial_mucosa": "Apparently Normal", "buccal_mucosa": "Reticular white striae bilateral", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Apparently Normal", "lingual_mucosa": "Apparently Normal", "palatal_mucosa": "Apparently Normal", "salivary_duct": "Patent"},
            "chart": [],
            "prov_diag": "Reticular Oral Lichen Planus",
            "final_diag": "Oral Lichen Planus",
            "inv": [("Biopsy & Histopathology", "Right Buccal Mucosa", 1, 500.00, 500.00, "8812/707511", "2026-06-25")],
            "ref": [("OPD", "OMR", "Biopsy evaluation", "Visited", "2026-06-25")],
            "xrays": [("Digital Soft Tissue View", "Right buccal mucosa lesion site", "2026-06-25")]
        },
        {
            "name": "RAMESH BABU",
            "dob": "1998-02-14",
            "gender": "Male",
            "phone": "9866122334",
            "email": "ramesh.babu28@gmail.com",
            "address": "H.No 8-44, Near IT Park",
            "village": "Mangalagiri",
            "occupation": "Software Engineer",
            "allergies": "None",
            "medical_conditions": "None",
            "status": "PATIENT_LIST",
            "op_no": "202606220198",
            "crn": "OMR260622193",
            "cc": "Pain in lower right wisdom tooth area and inability to open mouth fully since 2 days.",
            "hpi": "Pain started 2 days ago after food impaction behind lower right last tooth. Mild trismus.",
            "past_med": "None",
            "past_dent": "None",
            "habits": "Absent",
            "diet": "Non-Veg",
            "sleep": "Disturbed",
            "lymph_node": "Palpable",
            "eoe": {"lymph_node_left_size": "", "lymph_node_right_size": "1.2 cm", "lymph_node_left_consistency": "/", "lymph_node_right_consistency": "Tender"},
            "ioe": {"wasting_attrition": "Absent", "hypoplasia": "Absent", "labial_mucosa": "Apparently Normal", "buccal_mucosa": "Swollen operculum irt 48", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Tender irt 48", "lingual_mucosa": "Apparently Normal", "palatal_mucosa": "Apparently Normal", "salivary_duct": "Patent"},
            "chart": [("48", "ALL", "implant", "Impaction")],
            "prov_diag": "Impacted tooth #48 with acute pericoronitis",
            "final_diag": "Impacted tooth #48 with acute pericoronitis",
            "inv": [("IOPA - X-Ray (Digital)", "48", 1, 30.00, 30.00, "4801/707512", "2026-06-26")],
            "ref": [("OPD", "Oral Surgery", "Surgical disimpaction 48", "Visited", "2026-06-26")],
            "xrays": [("IOPA - Digital X-Ray", "Mesioangular impacted tooth #48", "2026-06-26")]
        },
        {
            "name": "PRIYA SHARMA",
            "dob": "2004-09-10",
            "gender": "Female",
            "phone": "9701044556",
            "email": "priya.sharma@gmail.com",
            "address": "D.No 15-2, NGO Colony",
            "village": "Amaravati",
            "occupation": "Student",
            "allergies": "Dust allergy",
            "medical_conditions": "None",
            "status": "NEW_OP",
            "op_no": "202606220199",
            "crn": "OMR260622194",
            "cc": "Forwardly placed upper teeth and gap between front teeth.",
            "hpi": "Patient desires cosmetic improvement and orthodontic alignment.",
            "past_med": "None",
            "past_dent": "Oral prophylaxis done 6 months ago.",
            "habits": "Thumb sucking (childhood)",
            "diet": "Veg",
            "sleep": "Normal",
            "lymph_node": "Non-palpable",
            "eoe": {"lymph_node_left_size": "", "lymph_node_right_size": "", "lymph_node_left_consistency": "/", "lymph_node_right_consistency": "/"},
            "ioe": {"wasting_attrition": "Absent", "hypoplasia": "Absent", "labial_mucosa": "High frenal attachment", "buccal_mucosa": "Apparently Normal", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Apparently Normal", "lingual_mucosa": "Apparently Normal", "palatal_mucosa": "Deep palate", "salivary_duct": "Patent"},
            "chart": [("11", "ALL", "decay", "Diastema"), ("21", "ALL", "decay", "Diastema")],
            "prov_diag": "Angle's Class II Div 1 malocclusion with midline diastema",
            "final_diag": "Angle's Class II Div 1 malocclusion",
            "inv": [("Lateral Cephalogram & OPG", "All", 2, 600.00, 600.00, "1102/707513", "2026-06-27")],
            "ref": [("OPD", "Orthodontics", "Orthodontic evaluation", "Visited", "2026-06-27")],
            "xrays": [("Lateral Cephalogram", "Class II skeletal relationship", "2026-06-27"), ("OPG - Panoramic Scan", "Full dentition orthodontic view", "2026-06-27")]
        },
        {
            "name": "SURESH KUMAR",
            "dob": "1968-07-22",
            "gender": "Male",
            "phone": "9441199887",
            "email": "suresh.k@gmail.com",
            "address": "Flat 3A, Sea Breeze Apts",
            "village": "Kakinada",
            "occupation": "Bank Officer",
            "allergies": "None",
            "medical_conditions": "Hypertension",
            "status": "PATIENT_LIST",
            "op_no": "202606220200",
            "crn": "OMR260622195",
            "cc": "Missing back teeth in upper and lower jaw, difficulty in chewing food.",
            "hpi": "Teeth extracted due to caries over the past 5 years. Wants fixed teeth/implants.",
            "past_med": "Hypertension (Under medication Telmisartan 40mg)",
            "past_dent": "Multiple extractions",
            "habits": "Ex-smoker",
            "diet": "Mixed",
            "sleep": "Normal",
            "lymph_node": "Non-palpable",
            "eoe": {"lymph_node_left_size": "", "lymph_node_right_size": "", "lymph_node_left_consistency": "/", "lymph_node_right_consistency": "/"},
            "ioe": {"wasting_attrition": "Moderate", "hypoplasia": "Absent", "labial_mucosa": "Apparently Normal", "buccal_mucosa": "Apparently Normal", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Apparently Normal", "lingual_mucosa": "Apparently Normal", "palatal_mucosa": "Apparently Normal", "salivary_duct": "Patent"},
            "chart": [("16", "ALL", "missing", "Extracted"), ("17", "ALL", "missing", "Extracted"), ("26", "ALL", "missing", "Extracted"), ("27", "ALL", "missing", "Extracted"), ("36", "ALL", "missing", "Extracted"), ("37", "ALL", "missing", "Extracted")],
            "prov_diag": "Partially edentulous maxillary & mandibular arches (Kennedy Class I)",
            "final_diag": "Partially edentulous maxillary & mandibular arches",
            "inv": [("CBCT Scan - Full Arch", "Maxilla & Mandible", 1, 1500.00, 1500.00, "7701/707514", "2026-06-28")],
            "ref": [("OPD", "Prosthodontics", "Implant supported fixed prosthesis", "Visited", "2026-06-28")],
            "xrays": [("CBCT 3D Scan", "Maxillary & mandibular bone volume assessment", "2026-06-28")]
        },
        {
            "name": "BHAVANI PRASAD",
            "dob": "1985-01-30",
            "gender": "Male",
            "phone": "9849033445",
            "email": "bhavani.p@gmail.com",
            "address": "D.No 3-19, Godavari Road",
            "village": "Rajahmundry",
            "occupation": "Accountant",
            "allergies": "None",
            "medical_conditions": "None",
            "status": "NEW_OP",
            "op_no": "202606220201",
            "crn": "OMR260622196",
            "cc": "Sharp pain on drinking cold water in upper right back tooth.",
            "hpi": "Short sharp pain lasting few seconds upon thermal stimulus. Disappears immediately after stimulus removal.",
            "past_med": "None",
            "past_dent": "Filling in lower molar 4 years ago.",
            "habits": "Absent",
            "diet": "Non-Veg",
            "sleep": "Normal",
            "lymph_node": "Non-palpable",
            "eoe": {"lymph_node_left_size": "", "lymph_node_right_size": "", "lymph_node_left_consistency": "/", "lymph_node_right_consistency": "/"},
            "ioe": {"wasting_attrition": "Cervical abrasion on 14,15", "hypoplasia": "Absent", "labial_mucosa": "Apparently Normal", "buccal_mucosa": "Apparently Normal", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Apparently Normal", "lingual_mucosa": "Apparently Normal", "palatal_mucosa": "Apparently Normal", "salivary_duct": "Patent"},
            "chart": [("14", "ALL", "decay", "Cervical Cavity"), ("15", "ALL", "decay", "Abrasion")],
            "prov_diag": "Reversible pulpitis irt 14",
            "final_diag": "Reversible pulpitis irt 14",
            "inv": [("IOPA - X-Ray (Digital)", "14", 1, 30.00, 30.00, "1401/707515", "2026-06-29")],
            "ref": [("OPD", "Conservative Dentistry", "GIC/Composite restoration", "Visited", "2026-06-29")],
            "xrays": [("IOPA - Digital X-Ray", "Bitewing view tooth 14 cervical lesion", "2026-06-29")]
        },
        {
            "name": "SARASWATHI",
            "dob": "1959-04-12",
            "gender": "Female",
            "phone": "9948077665",
            "email": "saraswathi.67@gmail.com",
            "address": "H.No 1-88, Temple Street",
            "village": "Eluru",
            "occupation": "Retired",
            "allergies": "Aspirin",
            "medical_conditions": "Diabetes & Hypertension",
            "status": "PATIENT_LIST",
            "op_no": "202606220202",
            "crn": "OMR260622197",
            "cc": "Ulcer on the left side of tongue since 3 weeks.",
            "hpi": "Non-healing ulcer on left lateral border of tongue. History of sharp broken tooth in lower left jaw rubbing against tongue.",
            "past_med": "Diabetes Mellitus & Hypertension",
            "past_dent": "Broken teeth 36",
            "habits": "Betel nut chewing for 20 years",
            "diet": "Veg",
            "sleep": "Normal",
            "lymph_node": "Palpable",
            "eoe": {"lymph_node_left_size": "1.5 cm", "lymph_node_right_size": "", "lymph_node_left_consistency": "Firm", "lymph_node_right_consistency": "/"},
            "ioe": {"wasting_attrition": "Severe generalised", "hypoplasia": "Absent", "labial_mucosa": "Apparently Normal", "buccal_mucosa": "Apparently Normal", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Apparently Normal", "lingual_mucosa": "Ulcer 1.2cm left lateral border", "palatal_mucosa": "Apparently Normal", "salivary_duct": "Patent"},
            "chart": [("36", "ALL", "decay", "Fractured Cusp")],
            "prov_diag": "Traumatic ulcerative granuloma (TUGSE) irt 36 / Rule out Oral SCC",
            "final_diag": "Traumatic ulcerative granuloma (TUGSE)",
            "inv": [("Excisional Biopsy & OPG", "Tongue & Mandible", 1, 750.00, 750.00, "5501/707516", "2026-06-30")],
            "ref": [("OPD", "OMR", "Biopsy and lesion excision", "Visited", "2026-06-30")],
            "xrays": [("OPG - Panoramic Scan", "Mandible bone integrity left molar region", "2026-06-30")]
        },
        {
            "name": "MASTER KARTHIK",
            "dob": "2017-10-05",
            "gender": "Male",
            "phone": "9866055443",
            "email": "karthik.parent@gmail.com",
            "address": "D.No 6-12, School Lane",
            "village": "Vijayawada",
            "occupation": "Student",
            "allergies": "None",
            "medical_conditions": "None",
            "status": "PATIENT_LIST",
            "op_no": "202606220203",
            "crn": "OMR260622198",
            "cc": "Toothache in lower left primary molar tooth while eating sweets.",
            "hpi": "Child complains of pain in lower left back tooth since 5 days during food intake.",
            "past_med": "None",
            "past_dent": "First dental visit",
            "habits": "Sweet tooth",
            "diet": "Mixed",
            "sleep": "Normal",
            "lymph_node": "Non-palpable",
            "eoe": {"lymph_node_left_size": "", "lymph_node_right_size": "", "lymph_node_left_consistency": "/", "lymph_node_right_consistency": "/"},
            "ioe": {"wasting_attrition": "Primary dentition wear", "hypoplasia": "Absent", "labial_mucosa": "Apparently Normal", "buccal_mucosa": "Apparently Normal", "floor_of_mouth": "Apparently Normal", "vestibular_mucosa": "Apparently Normal", "lingual_mucosa": "Apparently Normal", "palatal_mucosa": "Apparently Normal", "salivary_duct": "Patent"},
            "chart": [("75", "ALL", "root-canal", "Pulpectomy"), ("74", "ALL", "decay", "Filling")],
            "prov_diag": "Chronic irreversible pulpitis irt 75",
            "final_diag": "Chronic irreversible pulpitis irt 75",
            "inv": [("IOPA - Pedodontic X-Ray", "75", 1, 30.00, 30.00, "7501/707517", "2026-07-01")],
            "ref": [("OPD", "Pedodontics", "Pulpectomy & Stainless steel crown", "Visited", "2026-07-01")],
            "xrays": [("Pedodontic IOPA Scan", "Primary molar 75 pulp involvement view", "2026-07-01")]
        }
    ]

    for p in patients_data:
        cursor.execute("""
            INSERT INTO patients (name, dob, gender, phone, email, address, allergies, medical_conditions, status, assigned_doctor_id, occupation, village_town_city, allotted_to, validity_date, category, case_record_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (p['name'], p['dob'], p['gender'], p['phone'], p['email'], p['address'], p['allergies'], p['medical_conditions'], p['status'], 1, p['occupation'], p['village'], "Dr. Admin", "2027-07-15", "Regular", p['crn']))
        pid = cursor.lastrowid

        cursor.execute("""
            INSERT INTO case_history (patient_id, chief_complaint, hpi, past_dental_history, past_medical_history, habits, clinical_findings, diet, parafunctional_habits, sleep)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (pid, p['cc'], p['hpi'], p['past_dent'], p['past_med'], p['habits'], p['cc'], p['diet'], p['habits'], p['sleep']))

        for htype in ['tobacco', 'alcohol', 'quid', 'others']:
            is_p = 1 if htype in p['habits'].lower() else 0
            cursor.execute("INSERT INTO deleterious_habits (patient_id, habit_type, is_present) VALUES (?, ?, ?);", (pid, htype, is_p))

        eoe = p['eoe']
        cursor.execute("""
            INSERT INTO extra_oral_exam (patient_id, lymph_palpable, lymph_left_size, lymph_right_size, lymph_left_consistency, lymph_right_consistency)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (pid, p['lymph_node'], eoe.get('lymph_node_left_size', ''), eoe.get('lymph_node_right_size', ''), eoe.get('lymph_node_left_consistency', '/'), eoe.get('lymph_node_right_consistency', '/')))

        ioe = p['ioe']
        cursor.execute("""
            INSERT INTO intra_oral_exam (patient_id, wasting_attrition, hypoplasia, labial_mucosa, buccal_mucosa, floor_mouth, vestibular_mucosa, lingual_mucosa, palatal_mucosa, salivary_duct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (pid, ioe['wasting_attrition'], ioe['hypoplasia'], ioe['labial_mucosa'], ioe['buccal_mucosa'], ioe['floor_of_mouth'], ioe['vestibular_mucosa'], ioe['lingual_mucosa'], ioe['palatal_mucosa'], ioe['salivary_duct']))

        for t_num, surf, cond, notes in p['chart']:
            cursor.execute("INSERT INTO dental_chart (patient_id, tooth_number, surface, condition, notes) VALUES (?, ?, ?, ?, ?);", (pid, t_num, surf, cond, notes))

        cursor.execute("INSERT INTO diagnoses (patient_id, provisional_diagnosis, final_diagnosis) VALUES (?, ?, ?);", (pid, p['prov_diag'], p['final_diag']))

        for srv, teeth, qty, amt, paid, inv_no, dt in p['inv']:
            cursor.execute("""
                INSERT INTO investigations (patient_id, service_name, teeth_no, qty, rate, amount, disc_pct, total, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (pid, srv, teeth, qty, amt, amt, 0.0, paid, dt))

        for f_dept, t_dept, reason, status, dt in p['ref']:
            cursor.execute("""
                INSERT INTO referrals (patient_id, referred_to_dept, referral_reason, referral_status, created_at)
                VALUES (?, ?, ?, ?, ?);
            """, (pid, t_dept, reason, status, dt))

        for itype, desc, dt in p['xrays']:
            if "opg" in itype.lower():
                x_bytes = generate_procedural_opg_fracture_bytes()
            else:
                x_bytes = generate_procedural_xray_bytes()
            cursor.execute("""
                INSERT INTO xrays (patient_id, image_type, description, date_taken, image_data)
                VALUES (?, ?, ?, ?, ?);
            """, (pid, itype, desc, dt, x_bytes))

    conn.commit()
