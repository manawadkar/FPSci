[Setup]
AppId={{2F5A4D0B-7C39-4E3F-B90F-7D8E6A4A8C11}
AppName=FPSci
AppVersion=1.0.0
AppPublisher=SunilBM
DefaultDirName={autopf}\FPSci
DefaultGroupName=FPSci
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=FPSciSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\FPSciGame.exe
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\FPSciGame.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\FPSci"; Filename: "{app}\FPSciGame.exe"
Name: "{autodesktop}\FPSci"; Filename: "{app}\FPSciGame.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\FPSciGame.exe"; Description: "Launch FPSci"; Flags: nowait postinstall skipifsilent
