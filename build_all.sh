#!/bin/bash
# DentaLink Master Installer Package Builder Script
# Builds .deb, .rpm, Arch Linux PKGBUILD, and Universal AppImage installers
set -e

echo "========================================================="
echo " Building ALL DentaLink Linux Installers"
echo "========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "--- [1/4] Building Debian/Ubuntu (.deb) package ---"
bash build_deb.sh

echo ""
echo "--- [2/4] Building Fedora/RHEL (.rpm) package ---"
bash build_rpm.sh

echo ""
echo "--- [3/4] Building Arch Linux (.pkg.tar.zst) package ---"
bash build_arch.sh

echo ""
echo "--- [4/4] Building Universal AppImage (.AppImage) ---"
bash build_appimage.sh

echo ""
echo "========================================================="
echo " 🎉 ALL INSTALLERS BUILT AND UPDATED SUCCESSFULLY!"
echo "========================================================="
