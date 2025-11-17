; Inno Setup Script для Helper
; Создает полноценный установщик для Windows

#define MyAppName "Helper"
#define MyAppVersion "2.0.3"
#define MyAppPublisher "teja1337"
#define MyAppURL "https://github.com/teja1337/HelperTemplates"
#define MyAppExeName "Helper.exe"

[Setup]
; Основные параметры
AppId={{8F3D5C2A-9B7E-4D1F-A8C6-2E5F7B9D3A1C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=dist
OutputBaseFilename=Helper_Installer
SetupIconFile=installer_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableDirPage=no
DisableProgramGroupPage=no

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Helper.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\updater.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "version.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\Helper.exe"
Type: files; Name: "{app}\updater.exe"
Type: files; Name: "{app}\version.json"
Type: files; Name: "{app}\Helper.exe.backup"
Type: files; Name: "{app}\Helper_update.exe"
Type: dirifempty; Name: "{app}"
