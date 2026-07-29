#!/bin/bash
# DentaLink RPM (.rpm) Package Builder Script
set -e

APP_NAME="dentalink"
VERSION="0.3.0"
RELEASE="1"
ARCH="x86_64"
RPM_TOPDIR="/tmp/rpmbuild_dentalink"
PACKAGE_NAME="${APP_NAME}-${VERSION}-${RELEASE}.${ARCH}.rpm"

echo "========================================================="
echo " Building DentaLink RPM Package: ${PACKAGE_NAME}"
echo "========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Clean previous build directory
rm -rf "$RPM_TOPDIR" "${PACKAGE_NAME}"

# 2. Check standalone Linux ELF binary via PyInstaller
PYINSTALLER_BIN="$HOME/.venv_deb/bin/python3"
rm -rf dist/DentaLink build/DentaLink

if [ -f "$PYINSTALLER_BIN" ] && "$PYINSTALLER_BIN" -m PyInstaller --version &>/dev/null; then
    echo "Building binary with PyInstaller ($PYINSTALLER_BIN)..."
    "$PYINSTALLER_BIN" -m PyInstaller DentaLink.spec --noconfirm --clean || true
elif command -v pyinstaller &>/dev/null; then
    echo "Building binary with PyInstaller (system pyinstaller)..."
    pyinstaller DentaLink.spec --noconfirm --clean || true
elif python3 -m PyInstaller --version &>/dev/null; then
    echo "Building binary with PyInstaller (python3 -m PyInstaller)..."
    python3 -m PyInstaller DentaLink.spec --noconfirm --clean || true
else
    echo "PyInstaller not found in environment. Packaging source-based distribution."
fi

# 3. Create rpmbuild directory structure
mkdir -p "$RPM_TOPDIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
PAYLOAD_DIR="$RPM_TOPDIR/SOURCES/dentalink_payload"
mkdir -p "$PAYLOAD_DIR"

# 4. Copy build bundle files and python source modules
if [ -d "dist/DentaLink" ]; then
    echo "Copying compiled PyInstaller executable bundle..."
    cp -r dist/DentaLink/. "$PAYLOAD_DIR/"
    # Clean up host-dependent libraries that cause GLIBC mismatch errors
    rm -f "$PAYLOAD_DIR/_internal/libglib-2.0.so.0"
    rm -f "$PAYLOAD_DIR/_internal/libtinfo.so.6"
fi

cp -r main.py database.py app_icon.png settings_config.json gui widgets db dentalink.desktop "$PAYLOAD_DIR/"

# 5. Copy RPM Spec file
cp dentalink_rpm.spec "$RPM_TOPDIR/SPECS/dentalink.spec"

# 6. Execute rpmbuild
if command -v rpmbuild &>/dev/null; then
    echo "Executing rpmbuild..."
    rpmbuild --define "_topdir $RPM_TOPDIR" -bb "$RPM_TOPDIR/SPECS/dentalink.spec"
    
    # Copy generated RPM to current directory
    GENERATED_RPM=$(find "$RPM_TOPDIR/RPMS" -name "*.rpm" | head -n 1)
    if [ -f "$GENERATED_RPM" ]; then
        cp "$GENERATED_RPM" "./${PACKAGE_NAME}"
        echo "========================================================="
        echo " Success! RPM package built: ./${PACKAGE_NAME}"
        echo " Install using: sudo dnf install ./${PACKAGE_NAME} (Fedora/RHEL)"
        echo "           or:  sudo zypper install ./${PACKAGE_NAME} (openSUSE)"
        echo "========================================================="
    fi
    rm -rf "$RPM_TOPDIR"
else
    echo "========================================================="
    echo " Notice: 'rpmbuild' command not installed on host."
    echo " Payload staged in: $PAYLOAD_DIR"
    echo " Spec file saved to: dentalink_rpm.spec"
    echo " To build the RPM on RedHat/Fedora/CentOS/openSUSE:"
    echo "   1. Install rpmbuild: sudo dnf install rpm-build"
    echo "   2. Run this script:  bash build_rpm.sh"
    echo "========================================================="
fi
