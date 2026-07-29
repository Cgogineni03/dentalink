#!/bin/bash
# DentaLink Debian (.deb) Package Builder Script
set -e

APP_NAME="dentalink"
VERSION="0.3.0"
ARCH="amd64"
DEB_DIR="/tmp/build_deb_pkg"
PACKAGE_NAME="${APP_NAME}_${VERSION}_${ARCH}"

echo "========================================================="
echo " Building DentaLink Debian Package: ${PACKAGE_NAME}.deb"
echo "========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Clean previous build artifacts
rm -rf "$DEB_DIR" "${PACKAGE_NAME}.deb"

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

# 3. Prepare Debian directory structure
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/dentalink"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"

# 4. Copy build bundle files and python source modules
if [ -d "dist/DentaLink" ]; then
    echo "Copying compiled PyInstaller executable bundle..."
    cp -r dist/DentaLink/. "$DEB_DIR/usr/share/dentalink/"
    # Clean up host-dependent libraries that cause GLIBC mismatch errors
    rm -f "$DEB_DIR/usr/share/dentalink/_internal/libglib-2.0.so.0"
    rm -f "$DEB_DIR/usr/share/dentalink/_internal/libtinfo.so.6"
fi

cp -r main.py database.py app_icon.png settings_config.json gui widgets db "$DEB_DIR/usr/share/dentalink/"
cp app_icon.png "$DEB_DIR/usr/share/icons/hicolor/256x256/apps/dentalink.png"
cp dentalink.desktop "$DEB_DIR/usr/share/applications/"

# Clean up pycache files from staging directory
find "$DEB_DIR/usr/share/dentalink" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$DEB_DIR/usr/share/dentalink" -name "*.pyc" -delete 2>/dev/null || true

# 5. Create launcher wrapper script in /usr/bin/dentalink
cat << 'EOF' > "$DEB_DIR/usr/bin/dentalink"
#!/bin/bash
cd /usr/share/dentalink || exit 1
export QT_QPA_PLATFORMTHEME=${QT_QPA_PLATFORMTHEME:-gtk3}
export PYTHONPATH="/usr/share/dentalink:$PYTHONPATH"

if [ -x /usr/share/dentalink/DentaLink ]; then
    /usr/share/dentalink/DentaLink "$@" || exec python3 /usr/share/dentalink/main.py "$@"
else
    exec python3 /usr/share/dentalink/main.py "$@"
fi
EOF
chmod +x "$DEB_DIR/usr/bin/dentalink"

# 6. Copy Debian maintainer scripts (postinst, postrm)
if [ -f "debian/postinst" ]; then
    cp debian/postinst "$DEB_DIR/DEBIAN/postinst"
    chmod 755 "$DEB_DIR/DEBIAN/postinst"
fi
if [ -f "debian/postrm" ]; then
    cp debian/postrm "$DEB_DIR/DEBIAN/postrm"
    chmod 755 "$DEB_DIR/DEBIAN/postrm"
fi

# 7. Create Debian control file
cat << EOF > "$DEB_DIR/DEBIAN/control"
Package: ${APP_NAME}
Version: ${VERSION}
Architecture: ${ARCH}
Maintainer: DentaLink Development Team <support@dentalink.org>
Depends: python3, python3-pyqt6, python3-cryptography, sqlite3, libc6, libxcb-cursor0, libxcb-xinerama0, libxcb-icccm4, libxcb-image0, libxcb-keysyms1, libxcb-render-util0, libxcb-shape0, libx11-xcb1, libgl1, libglib2.0-0, libegl1, libfontconfig1, libdbus-1-3
Section: utils
Priority: optional
Description: Native Patient Management Desktop Application for Dental Clinics
 DentaLink is a native desktop application for dental clinics to manage
 patient registration, clinical examinations, dental/periodontal charts,
 diagnostic images, billing, referrals, and appointments. Features encrypted
 SQLite storage, universal recovery keys, and Git-style history tracking.
EOF


# 8. Build .deb package using dpkg-deb
dpkg-deb --root-owner-group --build "$DEB_DIR" "${PACKAGE_NAME}.deb"


# 9. Cleanup temporary package directory
rm -rf "$DEB_DIR"

echo "========================================================="
echo " Success! Package built: ${PACKAGE_NAME}.deb"
echo " Install using: sudo dpkg -i ${PACKAGE_NAME}.deb"
echo "========================================================="
