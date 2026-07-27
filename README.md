# 🦷 DentaLink — Patient Management Desktop Application (v0.3)

DentaLink is a native Windows desktop application for dental clinics to manage patient registration, clinical examinations, dental/periodontal charts, diagnostic images, billing, referrals, and appointments. It features modular architecture, encrypted database security, 2-Factor recovery keys, and Git-style immutable patient history tracking.

---

## 🚀 Core Features (v0.3)

### 🏥 Onboarding & Multi-User Management
- **First-Launch Setup Wizard**: Guided onboarding for clinic profile creation, admin doctor credentials, and security recovery setup.
- **Doctor & Admin Authentication**: Role-based access control with secure password hashing and recovery options.
- **Emergency Password Recovery**: 16-character **Universal Recovery Key** generation for emergency doctor password reset without data loss.

### 📋 Patient Workflow & Clinical Records
- **Queue Management**: Outpatient registration, transition from New OP to Active Patients list.
- **Comprehensive Case History**: Capture chief complaints, HPI, medical/dental history, deleterious habits (tobacco, alcohol, etc.), and personal background.
- **Clinical Examination Panels**:
  - **Extra-Oral Examination**: TMJ assessment, lymph node checks, and vital signs capture.
  - **Intra-Oral Examination**: Occlusion, gingival findings, oral mucosal health, and wasting conditions logging.
  - **Local Examinations**: Detailed soft/hard tissue inspection, palpation, and percussion.

### 🦷 Interactive Charting & Imaging
- **Interactive Dental Chart**: Tooth-level surface-specific condition charting.
- **Periodontal Chart**: Probing depths, tooth mobility, and Bleeding on Probing (BOP).
- **X-Ray & Diagnostic Viewer**: Upload, view, and store X-ray images directly within the SQLite database as secure BLOBs.

### 📜 Git-Style Immutable History Tracking
- **Version Control for Patient Records**: Snapshot commits for patient record modifications.
- **Section Hierarchy Deltas**: Categorized visual diffs tracking changes across medical history, clinical findings, and dental charts.
- **Version History Dialog**: Inspect full commit history and timeline deltas for every patient record.

### 💳 Billing, Appointments & Referrals
- **Billing & Payments**: Procedure item billing, doctor discount rules, payment acceptance, and dues tracking.
- **Multi-Referral System**: Track patient referral sources and specialist outgoing referrals.
- **Appointments**: Schedule and track upcoming patient visits.

---

## 🛠️ Technology Stack

- **Python**: 3.14 / 3.12
- **GUI Framework**: [PyQt6](https://pypi.org/project/PyQt6/)
- **Database**: [SQLite](https://sqlite.org/) with cryptography extensions
- **Security**: `cryptography` (PBKDF2, AES, HMAC)
- **Packaging & Installer**: [PyInstaller 6.x](https://pyinstaller.org/) & [Inno Setup 6](https://jrsoftware.org/isinfo.php)

---

## 📂 Project Structure

```
dental-patient-management/
├── main.py                     # Entry point & component facade
├── database.py                 # Root facade for database operations
├── DentaLink.spec              # PyInstaller build configuration
├── setup.iss                   # Inno Setup installer script
├── verify_app.py               # 7-step test verification script
├── db/                         # Modular database domain layer
│   ├── appointments.py         # Appointment scheduling
│   ├── clinical.py             # Clinical exams, prescriptions, X-rays
│   ├── clinics.py              # Clinic setup, doctor auth & recovery
│   ├── connection.py           # SQLite connection & schema initialization
│   ├── crypto.py               # Encryption, hashing & universal key generator
│   ├── history.py              # Git-style immutable history commit engine
│   ├── patients.py             # Patient demographic & workflow state
│   ├── procedural_graphics.py  # Procedural image rendering
│   ├── referrals.py            # Patient referral management
│   └── seeding.py              # Mock data seeding
├── gui/                        # Modular Qt UI components & dialogs
│   ├── components/             # Custom UI widgets (clickable labels, file uploader)
│   ├── dialogs/                # Dialog windows (first launch, auth, recovery key)
│   ├── login_window.py         # Clinic login window
│   ├── main_window.py          # Primary application workbench window
│   └── styles.py               # Dark & Light stylesheet tokens
├── widgets/                    # Custom interactive graphics widgets
│   ├── dental_chart.py         # Interactive dental charting widget
│   └── xray_viewer.py          # Diagnostic X-ray viewer widget
└── installer_dist/             # Distribution output directory
    └── DentaLinkSetup.exe      # Compiled Windows installer v0.3
```

---

## 🧪 Verification & Testing

Run the automated test suite to verify database schemas, security recovery keys, and history commit tracking:

```powershell
python verify_app.py
```

---

## 📦 Windows Installer & Release v0.3

### Build Standalone Executable
```powershell
py -m PyInstaller DentaLink.spec --noconfirm
```

### Build Inno Setup Installer
```cmd
"C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 6\ISCC.exe" setup.iss
```
The output installer is generated at `installer_dist/DentaLinkSetup.exe`.

### 📥 Download Release
Download the latest Windows Installer from [GitHub Releases v0.3](https://github.com/Cgogineni03/dentalink/releases/tag/v0.3.0).

---

## 📄 License

This project is licensed under the terms included in the [LICENSE](LICENSE) file.
