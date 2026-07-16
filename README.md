# 🦷 DentaLink — Patient Management Desktop Application

DentaLink is a native desktop application for dental clinics to manage patient registration, clinical examinations, dental/periodontal charts, diagnostic images, billing, and appointments. It is built with **Python 3.12**, **PyQt6**, and a local **SQLite** database, supporting both dark and light themes.

---

## 🚀 Core Features

- **Clinic Dashboard**: Overview of pending outpatients, appointments, and clinic status.
- **Patient Workflow**: Register patients, move them through the new OP queue, and manage active patient records.
- **Case History**: Maintain chief complaints, HPI, medical/dental history, brushing habits, and personal background.
- **Clinical Examination Panels**:
  - **Extra-Oral Examination**: TMJ assessment, lymph node checks, and general vital sign capture.
  - **Intra-Oral Examination**: Occlusion, gingival findings, oral mucosal health, and wasting condition logging.
  - **Local Examinations**: Inspect and record soft/hard tissue findings, palpation, and percussion.
- **Dental & Periodontal Charting**:
  - **Dental Chart**: Capture tooth-level condition and surface-specific findings.
  - **Periodontal Chart**: Track probing depths, mobility, and bleeding on probing (BOP).
- **Diagnostics & X-ray Viewer**:
  - Upload and store X-ray images securely within the patient profile.
  - View diagnostic images with built-in display controls.
- **Billing & Payments**: Create procedure billing, apply doctor discounts, accept payments, and track dues.
- **Appointments**: Book appointments and maintain visit schedules.
- **Clinic Customization**:
  - Upload a clinic logo for the app header and printed reports.
  - Switch between dark and light themes.

---

## 🛠️ Technology Stack

- **Python**: 3.12
- **GUI**: [PyQt6](https://pypi.org/project/PyQt6/)
- **Database**: [SQLite](https://sqlite.org/)
- **Packaging**: [PyInstaller](https://pyinstaller.org/) and [Inno Setup](https://jrsoftware.org/isinfo.php)

---

## 📂 Project Structure

```
dental-patient-management/
├── main.py                     # Main application entry point and UI logic
├── database.py                 # SQLite schema, connection helpers, and operations
├── DentaLink.spec              # PyInstaller build specification
├── setup.iss                   # Inno Setup installer script
├── verify_app.py               # Verification and sanity-check script
├── widgets/                    # Custom Qt widgets
│   ├── __init__.py
│   ├── dental_chart.py         # Dental chart widget
│   └── xray_viewer.py          # X-ray viewer widget
└── dental_clinic.db            # Generated SQLite database file at runtime
```

---

## 📦 Database Schema Overview

DentaLink stores application data in a normalized SQLite database with the following tables:

| Table | Description |
| :--- | :--- |
| `clinics` | Clinic settings, admin credentials, and logo path. |
| `doctors` | Doctor profiles, login credentials, and discount percentages. |
| `patients` | Patient demographics, status, assigned doctor, and balances. |
| `case_history` | Medical/dental history, brushing habits, and narrative records. |
| `deleterious_habits` | Patient habit logs such as tobacco, alcohol, quid, and others. |
| `extra_oral_exam` | Vital signs and extra-oral exam findings. |
| `intra_oral_exam` | Intra-oral exam details and occlusion data. |
| `local_examinations` | Local examination records for soft/hard tissue findings. |
| `diagnoses` | Provisional, differential, and final diagnosis entries. |
| `dental_chart` | Tooth-level charting for each surface and condition. |
| `perio_chart` | Periodontal probing depths, mobility, and bleeding data. |
| `xrays` | Diagnostic X-ray images stored as BLOBs. |
| `investigations` | Investigation orders and billing totals. |
| `appointments` | Appointment dates, times, and visit tracking. |
| `prescriptions` | Medication prescriptions and dosage instructions. |
| `treatments_needed` | Planned treatment items and billing details. |
| `treatments_done` | Completed procedures and clinical notes. |
| `patient_files` | External attachments such as PDFs or images. |

---

## ⚙️ Getting Started

### 1. Prerequisites

Install **Python 3.12**.

### 2. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install PyQt6
```

### 4. Run the application

```bash
python main.py
```

---

## 🧪 Verification & Testing

Run the verification script to confirm the application environment and database setup:

```bash
python verify_app.py
```

A successful verification run should complete without errors.

---

## 📦 Packaging for Windows

### Build standalone executable

```bash
pyinstaller DentaLink.spec
```

### Build installer with Inno Setup

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php).
2. Open `setup.iss` in the Inno Setup compiler and compile.

Or compile from the command line:

```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

The generated installer will be placed in `installer_dist/`.

---

## Notes

- `dental_clinic.db` is generated at runtime and should not be committed to source control.
- The installer initializes the database only when the file does not already exist.
