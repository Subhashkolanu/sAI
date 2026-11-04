; =========================================================
; sAI — Scalable AI Interface v1.0.0
; Inno Setup Installer Script
; =========================================================
; Target: Windows 10 & Windows 11 (64-bit)
; Architecture: Per-user installation, PrivilegesRequired=lowest
; =========================================================

#define MyAppName "sAI — Scalable AI Interface"
#define MyAppShortName "sAI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Subhash Kolanu"
#define MyAppURL "https://github.com/Subhashkolanu/sAI"
#define MyAppExeName "sAI.exe"
#define SourceDir "D:\EXTRAS\Projects\sAI"

[Setup]
; Unique application GUID
AppId={{D37F624C-8A95-46B9-B3A2-225B810B89C4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Per-User Installation without requiring Administrator Privileges
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\{#MyAppShortName}
DefaultGroupName={#MyAppShortName}
DisableProgramGroupPage=yes

; Target 64-bit Windows 10 & 11
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

; Installer Executable Output
OutputDir={#SourceDir}\dist_installer
OutputBaseFilename=sAI-Setup-v1.0.0
SetupIconFile={#SourceDir}\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression & Packaging
Compression=lzma2/ultra64
SolidCompression=yes

; Wizard Interface
WizardStyle=modern
DisableWelcomePage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Standalone PyInstaller --onedir application bundle
Source: "{#SourceDir}\dist\sAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{autoprograms}\{#MyAppShortName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
; Optional Desktop shortcut
Name: "{autodesktop}\{#MyAppShortName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Run]
; Option to launch sAI upon installer completion
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// User data protection notice:
// Persistent user files (databases, settings, memory, profiles, uploads) reside
// safely in %LOCALAPPDATA%\sAI\data and are deliberately excluded from uninstallation.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // User data directory remains preserved intentionally in %LOCALAPPDATA%\sAI\data
  end;
end;
