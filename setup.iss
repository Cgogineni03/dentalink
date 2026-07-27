; Inno Setup script for DentaLink Patient Management System

[Setup]
AppName=DentaLink
AppVersion=1.0
AppPublisher=DentaLink Team
DefaultDirName={localappdata}\DentaLink
DefaultGroupName=DentaLink
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\DentaLink.exe
OutputDir=installer_dist
OutputBaseFilename=DentaLinkSetup
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Copy all application binaries, PyQt6 assets, dependencies, and widgets from dist\DentaLink
Source: "dist\DentaLink\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DentaLink"; Filename: "{app}\DentaLink.exe"; IconFilename: "{app}\app_icon.ico"
Name: "{group}\{cm:UninstallProgram,DentaLink}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\DentaLink"; Filename: "{app}\DentaLink.exe"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon

[Run]
; Initialize SQLite database schema on first run if database does not exist
Filename: "{app}\DentaLink.exe"; Parameters: "--initialize-db"; WorkingDir: "{app}"; Flags: waituntilterminated skipifsilent; Check: not FileExists(ExpandConstant('{app}\dental_clinic.db'))
Filename: "{app}\DentaLink.exe"; Description: "{cm:LaunchProgram,DentaLink}"; Flags: nowait postinstall skipifsilent
