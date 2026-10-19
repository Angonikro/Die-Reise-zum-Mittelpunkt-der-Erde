#define MyAppName "Die Reise zum Mittelpunkt der Erde"
#define MyAppVersion "2.3.1"
#define MyAppExeName "Die-Reise-zum-Mittelpunkt-der-Erde.exe"

[Setup]
AppId={{8B41F53C-CC4B-4F74-9F0A-5A26D4A7B231}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Die Reise zum Mittelpunkt der Erde
DefaultDirName={autopf}\Die Reise zum Mittelpunkt der Erde
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=Die-Reise-zum-Mittelpunkt-der-Erde-2.3.1-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Symbole:"; Flags: unchecked

[Files]
Source: "..\dist\Die-Reise-zum-Mittelpunkt-der-Erde\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Spiel starten"; Flags: postinstall nowait skipifsilent
