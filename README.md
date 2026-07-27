# 🐧 DentaLink — Linux Patient Management Desktop Application (v0.3)

[![Linux](https://img.shields.io/badge/Platform-Linux%20%2F%20Debian%20%2F%20Ubuntu-orange?logo=linux)](https://debian.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B%20%7C%203.12-blue?logo=python)](https://python.org)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6%20%2F%20GTK4-green)](https://pypi.org/project/PyQt6/)
[![Debian Package](https://img.shields.io/badge/Package-.deb%20Installer-blueviolet)](https://debian.org)
[![Branch](https://img.shields.io/badge/Git%20Branch-linux-brightgreen)](https://github.com/Cgogineni03/dentalink/tree/linux)

**DentaLink (Linux Edition)** is a desktop patient management system specifically tailored for Debian-based Linux distributions (*Debian, Ubuntu, Linux Mint, Pop!_OS, Elementary OS, Zorin OS*). Designed for dental clinics, it manages patient registration, clinical examinations, surface-level dental charting, diagnostic X-ray imaging, billing, referrals, and appointments.

It features a modern **GTK4 / Libadwaita dark & light visual design system**, dynamic GTK theme auto-detection via `gsettings`, encrypted database security, 2-Factor emergency recovery keys, and Git-style immutable history tracking.

---

## 🚀 Key Linux Features

- 🐧 **Native Linux Desktop Integration**: Includes a `.desktop` Freedesktop launcher for GNOME, XFCE, KDE, and MATE application menus and docks.
- 🎨 **GTK4 / Libadwaita Visual Aesthetics**: Clean dark and light GTK theme support with rounded card surfaces, `#3584e4` blue accent highlights, pill action buttons, and GTK typography.
- 🌗 **System GTK Theme Auto-Detection**: Dynamically queries Linux desktop `gsettings color-scheme` to automatically align app appearance with the host environment.
- 📦 **Automated Debian Package (`.deb`) Builder**: Built-in `build_deb.sh` script to package DentaLink into a standalone `.deb` installer with desktop entry and menu icons.
- 🏥 **Onboarding & Doctor Auth**: Guided setup wizard, role-based clinic authentication, and a 16-character **Universal Recovery Key** for emergency password resets.
- 🦷 **Interactive Charting & X-Ray Viewer**: Surface-specific adult/pediatric dental charting, periodontal probing logs, and BLOB-stored diagnostic X-ray management.
- 📜 **Git-Style Immutable History Tracking**: Record snapshot commit logs and visual section deltas tracking all patient record changes.

---

## 🛠️ Technology Stack

| Component | Technology / Library |
| :--- | :--- |
| **Target Operating System** | Linux (Debian 11+, Ubuntu 22.04+, Linux Mint, Pop!_OS, Zorin OS) |
| **Language** | Python 3.10+ / 3.12 |
| **GUI Framework** | PyQt6 with GTK4 / Libadwaita QSS styling |
| **Database** | SQLite3 with AES-256 / PBKDF2 encryption |
| **Packaging** | `dpkg-deb`, PyInstaller 6.x, `.desktop` Freedesktop launcher |

---

## 📦 Prerequisites & System Dependencies

On Debian-based distributions (Debian, Ubuntu, Linux Mint, Pop!_OS):

```bash
sudo apt update
sudo apt install -f python3 python3-pip python3-pyqt6 python3-cryptography sqlite3
```

---

## 🚀 Quick Start (Running from Source)

Clone the repository and switch to the `linux` branch:

```bash
git clone https://github.com/Cgogineni03/dentalink.git
cd dentalink
git checkout linux
```

Install Python dependencies (if not using distribution packages):

```bash
pip install PyQt6 cryptography
```

Run the application:

```bash
python3 main.py
```

---

## 🧪 Automated Testing & Verification

Run the verification test suite to validate database schemas, encryption, recovery keys, and history snapshot commits:

```bash
python3 verify_app.py
```

---

## 🛠️ Building & Installing the Debian Package (`.deb`)

DentaLink includes an automated packaging script (`build_deb.sh`) that compiles PyInstaller binaries and structures a Debian `.deb` package.

### 1. Build the `.deb` Package

```bash
chmod +x build_deb.sh
./build_deb.sh
```

The compiled package will be generated at:
`dentalink_0.3.0_amd64.deb`

### 2. Install the Package

```bash
sudo dpkg -i dentalink_0.3.0_amd64.deb
sudo apt install -f  # Fix any missing system dependencies if prompted
```

Once installed, DentaLink will appear in your application launcher menu under **Office** / **Medical** as **DentaLink Clinic Management**.

---

## 📂 Project Structure

```
Dentalink_linux/
├── main.py                     # Primary entry point & window controller
├── database.py                 # Core database access layer & facade
├── DentaLink.spec              # PyInstaller build specification for Linux
├── dentalink.desktop           # Freedesktop application entry file
├── app_icon.png                # Desktop launcher PNG icon
├── build_deb.sh                # Debian (.deb) package compilation script
├── verify_app.py               # Automated verification test suite
├── debian/                     # Debian package metadata
│   ├── control                 # APT package dependencies & metadata
│   ├── changelog               # Package version release notes
│   ├── rules                   # debhelper build instructions
│   └── copyright               # Package copyright manifest
├── db/                         # Modular SQLite database domain models
│   ├── appointments.py         # Appointment scheduling
│   ├── clinical.py             # Exams, prescriptions, X-rays
│   ├── clinics.py              # Clinic profile, auth & recovery keys
│   ├── connection.py           # SQLite connection pool & migration
│   ├── crypto.py               # PBKDF2 hashing, AES-256 encryption
│   ├── history.py              # Immutable record commit history engine
│   ├── patients.py             # Patient records & registration workflow
│   ├── procedural_graphics.py  # SVG/PNG procedural rendering
│   ├── referrals.py            # Referral tracking
│   └── seeding.py              # Sample clinic database seeding
├── gui/                        # Modular Qt user interface components
│   ├── components/             # Custom widgets (file uploader, clickable labels)
│   ├── dialogs/                # Dialog windows (onboarding, auth, history viewer)
│   ├── login_window.py         # Login screen
│   ├── main_window.py          # Main workbench interface
│   └── styles.py               # GTK4 / Libadwaita QSS theme manager & auto-detector
└── widgets/                    # Custom graphics widgets
    ├── dental_chart.py         # Interactive dental charting widget
    └── xray_viewer.py          # Diagnostic X-ray viewer widget
```

---

## 📄 License

This project is licensed under the terms included in the [LICENSE](LICENSE) file.

