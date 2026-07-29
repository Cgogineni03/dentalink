#!/bin/bash
# DentaLink Arch Linux (.pkg.tar.zst) Package Builder Script
set -e

APP_NAME="dentalink"
VERSION="0.3.0"
RELEASE="1"
ARCH="x86_64"
PACKAGE_NAME="${APP_NAME}-${VERSION}-${RELEASE}-${ARCH}.pkg.tar.zst"

echo "========================================================="
echo " Building DentaLink Arch Linux Package: ${PACKAGE_NAME}"
echo "========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Clean previous build artifacts
rm -rf pkg src "${APP_NAME}-*.pkg.tar.*"

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

# 3. Check for makepkg command
if command -v makepkg &>/dev/null; then
    echo "Executing makepkg..."
    makepkg -s -f --noconfirm
    echo "========================================================="
    echo " Success! Arch package built."
    echo " Install using: sudo pacman -U ${APP_NAME}-${VERSION}-${RELEASE}-${ARCH}.pkg.tar.zst"
    echo "========================================================="
else
    echo "========================================================="
    echo " Notice: 'makepkg' command not installed on host."
    echo " PKGBUILD manifest saved to: PKGBUILD"
    echo " To build the Arch package on Arch Linux / Manjaro / EndeavourOS:"
    echo "   1. Run: makepkg -si"
    echo "   2. Or install: sudo pacman -U ${APP_NAME}-${VERSION}-${RELEASE}-${ARCH}.pkg.tar.zst"
    echo "========================================================="
fi
