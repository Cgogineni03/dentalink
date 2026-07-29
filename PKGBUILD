# Maintainer: DentaLink Development Team <support@dentalink.org>
pkgname=dentalink
pkgver=0.3.0
pkgrel=1
pkgdesc="Native Patient Management Desktop Application for Dental Clinics"
arch=('x86_64')
url="https://github.com/Cgogineni03/dentalink"
license=('MIT')
depends=('python' 'python-pyqt6' 'python-cryptography' 'sqlite')
optdepends=('qt6-wayland: Wayland support')

package() {
  install -d "$pkgdir/usr/bin"
  install -d "$pkgdir/usr/share/dentalink"
  install -d "$pkgdir/usr/share/applications"
  install -d "$pkgdir/usr/share/icons/hicolor/256x256/apps"

  if [ -d "dist/DentaLink" ]; then
    cp -r dist/DentaLink/. "$pkgdir/usr/share/dentalink/"
    rm -f "$pkgdir/usr/share/dentalink/_internal/libglib-2.0.so.0"
    rm -f "$pkgdir/usr/share/dentalink/_internal/libtinfo.so.6"
  fi

  cp -r main.py database.py app_icon.png settings_config.json gui widgets db "$pkgdir/usr/share/dentalink/"
  cp app_icon.png "$pkgdir/usr/share/icons/hicolor/256x256/apps/dentalink.png"
  cp dentalink.desktop "$pkgdir/usr/share/applications/"

  cat << 'EOF' > "$pkgdir/usr/bin/dentalink"
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
  chmod +x "$pkgdir/usr/bin/dentalink"
}
