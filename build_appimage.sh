#!/bin/bash
# DentaLink Universal AppImage (.AppImage) Builder Script
set -e

APP_NAME="DentaLink"
VERSION="0.3.0"
ARCH="x86_64"
APPDIR="AppDir"
APPIMAGE_OUTPUT="${APP_NAME}-${VERSION}-${ARCH}.AppImage"

echo "========================================================="
echo " Building DentaLink Universal AppImage: ${APPIMAGE_OUTPUT}"
echo "========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Clean previous AppDir and AppImage build artifacts
rm -rf "$APPDIR" "$APPIMAGE_OUTPUT"

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
    echo "PyInstaller not found in environment. Packaging source-based AppDir distribution."
fi

# 3. Create AppDir directory structure
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/dentalink"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# 4. Copy payload and icons
if [ -d "dist/DentaLink" ]; then
    echo "Copying PyInstaller binary bundle to AppDir..."
    cp -r dist/DentaLink/. "$APPDIR/usr/share/dentalink/"
    rm -f "$APPDIR/usr/share/dentalink/_internal/libglib-2.0.so.0"
    rm -f "$APPDIR/usr/share/dentalink/_internal/libtinfo.so.6"
fi

cp -r main.py database.py app_icon.png settings_config.json gui widgets db "$APPDIR/usr/share/dentalink/"
cp app_icon.png "$APPDIR/app_icon.png"
cp app_icon.png "$APPDIR/.DirIcon"
cp app_icon.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/dentalink.png"
cp dentalink.desktop "$APPDIR/dentalink.desktop"
cp dentalink.desktop "$APPDIR/usr/share/applications/dentalink.desktop"

# 5. Create AppRun launcher entrypoint
cat << 'EOF' > "$APPDIR/AppRun"
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${HERE}/usr/share/dentalink/_internal:${LD_LIBRARY_PATH}"
export PYTHONPATH="${HERE}/usr/share/dentalink:${PYTHONPATH}"
export QT_QPA_PLATFORMTHEME=${QT_QPA_PLATFORMTHEME:-gtk3}

cd "${HERE}/usr/share/dentalink" || exit 1

if [ -x "${HERE}/usr/share/dentalink/DentaLink" ]; then
    exec "${HERE}/usr/share/dentalink/DentaLink" "$@"
else
    exec python3 "${HERE}/usr/share/dentalink/main.py" "$@"
fi
EOF
chmod +x "$APPDIR/AppRun"

# 6. Build AppImage using appimagetool if available
if command -v appimagetool &>/dev/null; then
    echo "Running appimagetool..."
    appimagetool "$APPDIR" "$APPIMAGE_OUTPUT"
    echo "========================================================="
    echo " Success! Universal AppImage built: ./${APPIMAGE_OUTPUT}"
    echo " Run using: chmod +x ./${APPIMAGE_OUTPUT} && ./${APPIMAGE_OUTPUT}"
    echo "========================================================="
else
    echo "========================================================="
    echo " AppDir bundle staged successfully at: ./${APPDIR}"
    echo " Test AppRun directly: ./${APPDIR}/AppRun"
    echo " To generate single-file AppImage:"
    echo "   1. Install appimagetool (https://github.com/AppImage/AppImageKit)"
    echo "   2. Run: appimagetool AppDir ${APPIMAGE_OUTPUT}"
    echo "========================================================="
fi
