# 🦷 DentaLink — Premium Patient Management Desktop Application

DentaLink is a native, premium desktop application designed for dental clinics to manage patient registrations, clinical examinations, dental/periodontal charts, diagnostic images (X-rays), billing, and appointments. Built using **Python 3**, **PyQt6**, and a secure local **SQLite** database, DentaLink provides an all-in-one offline clinical assistant with a high-performance dark/light themed user interface.

---

## 🚀 Core Features

- **Dashboard / Clinic Overview**: Get a bird's-eye view of today's pending new outpatients, upcoming appointments, and daily clinic statistics.
- **Queue Management**: Efficient workflow transitions from registration to the "New OP Queue" to active patient files.
- **Comprehensive Case History**: Track patient chief complaints, history of present illness (HPI), brushing habits, medical/dental histories, and lifestyle patterns.
- **Clinical Examination Panels**:
  - **Extra-Oral Examination**: TMJ assessment, lymph node palpation (size, consistency, tenderness, fixity for left/right sides), and general vital signs.
  - **Intra-Oral Examination**: Detailed gingival status, wasting diseases (attrition, abrasion, etc.), and dental occlusion.
  - **Local Examinations**: Specific inspection, palpation, and percussion logs.
- **Interactive Dental & Periodontal Charts**:
  - **Graphical Dental Chart**: High-fidelity interactive UI to mark tooth-specific conditions (decay, fillings, full crowns, root canals, implants, or missing teeth) across all 5 surfaces (Occlusal, Buccal, Lingual, Mesial, Distal).
  - **Periodontal Chart**: Record pocket depth, tooth mobility, and bleeding on probing (BOP) metrics.
- **Diagnostics & X-ray Viewer**:
  - Upload clinical images and X-rays directly into the patient profile (stored securely as binary BLOBs inside SQLite).
  - Interactive image processing controls (brightness, contrast, and color inversion).
- **Billing & Financials**: Create invoices for procedures, calculate automatic doctor discounts, accept payments, track outstanding balances, and preview/print invoices.
- **Appointment Scheduling**: Schedule, reschedule, and track patient visits.
- **Clinic Branding & Customization**:
  - Upload your clinic logo to display on app headers and printed invoices.
  - Toggle between a **Premium Dark Theme** and a **Clean Light Theme**.

---

## 🛠️ Technology Stack

- **Frontend Framework**: [PyQt6](https://pypi.org/project/PyQt6/) (Python bindings for Qt6)
- **Database Engine**: [SQLite](https://sqlite.org/) (Local, serverless relational database with foreign key constraints enabled)
- **Packaging Tools**: [PyInstaller](https://pyinstaller.org/) & [Inno Setup](https://jrsoftware.org/isinfo.php) (for Windows Installer creation)

---

## 📂 Project Structure

```
dental-patient-management/
├── main.py                     # Main application entry point & UI views
├── database.py                 # SQLite database schema, connections, and query operations
├── DentaLink.spec              # PyInstaller executable build specifications
├── setup.iss                   # Inno Setup Windows installer configuration script
├── verify_app.py               # Automated verification and workflow testing script
├── widgets/                    # Custom interactive Qt widgets
│   ├── __init__.py
│   ├── dental_chart.py         # Graphical Dental Chart & Periodontal editor
│   └── xray_viewer.py          # Diagnostic X-ray viewer & image processing tools
└── dental_clinic.db            # SQLite database file (generated automatically)
```

---

## 📦 Database Schema Overview

DentaLink uses a normalized SQLite database containing the following tables:

| Table | Description |
| :--- | :--- |
| `clinics` | Clinic settings, admin credentials, and clinic logo image paths. |
| `doctors` | Registered dentists, credentials, and custom discount rates. |
| `patients` | Demographic data, categories, balance dues, and workflow statuses. |
| `case_history` | Medical/dental histories, brushing habits, and personal records. |
| `deleterious_habits` | Logs of harmful habits, duration, and frequency. |
| `extra_oral_exam` | Vitals, TMJ, and detailed lymph node palpation results. |
| `intra_oral_exam` | Occlusions, wasting diseases, and detailed gingival pocket details. |
| `local_examinations` | Soft and hard tissue inspection/palpation logs. |
| `diagnoses` | Provisional, differential, and final diagnosis logs. |
| `dental_chart` | Individual surface condition configurations for all teeth. |
| `perio_chart` | Periodontal pocket depths, mobility, and bleeding on probing. |
| `xrays` | X-ray images stored securely as binary BLOB data. |
| `investigations` | Treatment diagnostics, requisitions, and billing totals. |
| `appointments` | Booked dates, times, and visitation tracking. |
| `prescriptions` | Drug name, dosage, frequency, and duration lists. |
| `treatments_needed` | Planned dental procedures, unit rates, and discount details. |
| `treatments_done` | Completed procedures, operator/doctor details, and progress notes. |
| `patient_files` | External PDF/image attachments stored as BLOBs. |

---

## ⚙️ Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Set Up Virtual Environment
It is highly recommended to use a virtual environment:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install the required PyQt6 library:
```bash
pip install PyQt6
```

### 4. Run the Application
Start the desktop application:
```bash
python main.py
```

---

## 🧪 Verification & Testing

DentaLink includes a verification script (`verify_app.py`) to test dependency imports, clean database initialization, state transitions, and BLOB storage integration:

```bash
python verify_app.py
```

Successful execution will output:
```text
=== Starting DentaLink Verification ===
Test 1: Checking module imports and dependencies...
  SUCCESS: All modules imported successfully.
Test 2: Initializing SQLite database and seeding sample records...
  Cleaned up old SQLite database file.
  SUCCESS: Database 'dental_clinic.db' created successfully.
Test 3: Verifying patient registration workflow...
  Registered John Connor. Generated ID: 1
  John Connor found in NEW_OP queue. State check passed.
  Opened John Connor's file. Transitioned status in SQLite.
  John Connor found in Active Patients list. Workflow state check passed.
  SUCCESS: Registration to OP to Patient List transition verified.
Test 4: Verifying X-ray binary BLOB storage and retrieval...
  Saved X-ray image BLOB. Generated X-ray ID: 1
  Retrieved binary matches original bytes exactly.
  SUCCESS: Secure database BLOB storage verified.

=== ALL TESTS PASSED SUCCESSFULLY! ===
```

---

## 📦 Packaging for Windows

### Build Standalone Executable
You can bundle the Python scripts into a single, standalone executable:
```bash
pyinstaller DentaLink.spec
```
This generates a single `DentaLink.exe` file in the `dist/` directory.

### Build Installer (Inno Setup)
To build a setup installer (`DentaLinkSetup.exe`):
1. Install [Inno Setup compiler](https://jrsoftware.org/isinfo.php).
2. Right-click `setup.iss` and select **Compile**, or run via command line:
   ```cmd
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
   ```
The installer will be generated in `installer_dist/`.
