# 🦷 DentaLink — Patient Management Desktop Application (v0.3)

DentaLink is a native Linux desktop application targeting Debian-based Linux distributions (Debian, Ubuntu, Linux Mint, Pop!_OS, Elementary OS, Zorin OS) for dental clinics to manage patient registration, clinical examinations, dental/periodontal charts, diagnostic images, billing, referrals, and appointments. It features modern GTK4 / Libadwaita dark and light visual themes, system GTK theme auto-detection, encrypted database security, 2-Factor recovery keys, and Git-style immutable patient history tracking.

---

## 🚀 Core Features (v0.3)

### 🐧 Debian-Based Linux Distribution Target
- **Native Freedesktop Integration**: `.desktop` application launcher for GNOME, XFCE, KDE, and MATE desktop docks and menus.
- **GNOME Libadwaita / GTK4 Visual Design**: Sleek dark and light GTK themes with rounded card containers, accent blue highlights (`#3584e4`), pill action buttons, and GTK typography.
- **System GTK Theme Auto-Detection**: Dynamically queries Linux desktop `gsettings color-scheme` to align app aesthetics with system preferences.
- **Debian Package Build (`.deb`)**: Automated `dpkg-deb` packaging script (`build_deb.sh`) for APT deployment.

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

- **Target Distros**: Debian, Ubuntu, Linux Mint, Pop!_OS, Zorin OS
- **Python**: 3.10+ / 3.12 / 3.14
- **GUI Framework**: [PyQt6](https://pypi.org/project/PyQt6/) with GTK platform integration
- **Styling**: Modern GTK4 / Libadwaita QSS design system
- **Database**: [SQLite](https://sqlite.org/) with cryptography extensions
- **Security**: `cryptography` (PBKDF2, AES, HMAC)
- **Linux Packaging**: Debian Package (`.deb`), `dpkg-deb`, [PyInstaller 6.x](https://pyinstaller.org/)

---

## 📂 Project Structure

```
dental-patient-management/
├── main.py                     # Entry point & component facade
├── database.py                 # Root facade for database operations
├── DentaLink.spec              # PyInstaller build configuration for Linux
├── dentalink.desktop           # Freedesktop application launcher file
├── build_deb.sh                # Debian (.deb) package compiler script
├── verify_app.py               # 7-step test verification script
├── debian/                     # Debian packaging metadata
│   ├── control                 # APT package dependencies & metadata
│   ├── changelog               # Package version release notes
│   ├── rules                   # debhelper build rules
│   └── copyright               # Debian copyright manifest
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
│   └── styles.py               # Modern GTK4 / Libadwaita stylesheets & system theme detector
└── widgets/                    # Custom interactive graphics widgets
    ├── dental_chart.py         # Interactive dental charting widget
    └── xray_viewer.py          # Diagnostic X-ray viewer widget
```

---

## 🧪 Verification & Testing

Run the automated test suite to verify database schemas, security recovery keys, and history commit tracking:

```bash
python3 verify_app.py
```

---

## 📦 Debian Package (.deb) & Linux Build

### System Dependencies (Debian / Ubuntu)
```bash
sudo apt update
sudo apt install python3 python3-pyqt6 python3-cryptography sqlite3
```

### Build Debian (.deb) Package
To compile a standalone `.deb` package targeting Debian-based Linux distros:

```bash
chmod +x build_deb.sh
./build_deb.sh
```
Output package: `dentalink_0.3.0_amd64.deb`.

### Install Package on Debian / Ubuntu / Mint / Pop!_OS
```bash
sudo dpkg -i dentalink_0.3.0_amd64.deb
# Fix any missing dependencies if needed:
sudo apt install -f
```

---

## 📄 License

This project is licensed under the terms included in the [LICENSE](LICENSE) file.
