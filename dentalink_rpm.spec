Name:           dentalink
Version:        0.3.0
Release:        1%{?dist}
Summary:        Native Patient Management Desktop Application for Dental Clinics

License:        MIT
URL:            https://github.com/Cgogineni03/dentalink
BuildArch:      x86_64

Requires:       python3, python3-pyqt6, sqlite, libxcb, libX11, mesa-libGL, glib2, fontconfig, dbus

%description
DentaLink is a native desktop application for dental clinics to manage
patient registration, clinical examinations, dental/periodontal charts,
diagnostic images, billing, referrals, and appointments. Features encrypted
SQLite storage, universal recovery keys, and Git-style history tracking.

%prep
# Staged in SOURCES/dentalink_payload by build_rpm.sh

%build
# Python desktop application

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/dentalink
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps

cp -r %{_sourcedir}/dentalink_payload/* %{buildroot}/usr/share/dentalink/
cp %{_sourcedir}/dentalink_payload/app_icon.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/dentalink.png
cp %{_sourcedir}/dentalink_payload/dentalink.desktop %{buildroot}/usr/share/applications/

cat << 'EOF' > %{buildroot}/usr/bin/dentalink
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
chmod +x %{buildroot}/usr/bin/dentalink

%post
if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q || true
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

%postun
if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q || true
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

%files
/usr/bin/dentalink
/usr/share/dentalink
/usr/share/applications/dentalink.desktop
/usr/share/icons/hicolor/256x256/apps/dentalink.png

%changelog
* Mon Jul 27 2026 DentaLink Development Team <support@dentalink.org> - 0.3.0-1
- Initial RPM package release for Fedora/RHEL/CentOS/openSUSE.
