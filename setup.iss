; Inno Setup script for DentaLink Patient Management System

[Setup]
AppName=DentaLink
AppVersion=1.0
AppPublisher=DentaLink Team
DefaultDirName={localappdata}\DentaLink
DefaultGroupName=DentaLink
UninstallDisplayIcon={app}\DentaLink.exe
OutputDir=installer_dist
OutputBaseFilename=DentaLinkSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
Source: "dist\DentaLink.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\dental_clinic.db"; DestDir: "{app}"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{group}\DentaLink"; Filename: "{app}\DentaLink.exe"
Name: "{userdesktop}\DentaLink"; Filename: "{app}\DentaLink.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\DentaLink.exe"; Description: "Launch DentaLink"; Flags: nowait postinstall skipifsilent
