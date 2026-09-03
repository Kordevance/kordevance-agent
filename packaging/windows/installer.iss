
#define MyAppName "Kordevance"
#define MyAppVersion GetEnv("KORDEVANCE_VERSION")
#define MyServiceName "KordevanceGateway"

[Setup]
AppId={{B3B6A6C1-6B7B-4B7A-9C1D-3F1E7B7B0A11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Kordevance
DefaultGroupName=Kordevance
DisableProgramGroupPage=yes
OutputDir=..\..\dist
OutputBaseFilename=Kordevance-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
Uninstallable=yes

[Files]
Source: "..\..\dist\kordevance\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "nssm.exe"; DestDir: "{app}"; Flags: ignoreversion

[Run]
Filename: "{app}\nssm.exe"; Parameters: "install {#MyServiceName} ""{app}\kordevance-gateway.exe"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#MyServiceName} AppDirectory ""{app}"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#MyServiceName} Start SERVICE_AUTO_START"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#MyServiceName} AppStdout ""{commonappdata}\Kordevance\logs\kordevance-gateway.log"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#MyServiceName} AppStderr ""{commonappdata}\Kordevance\logs\kordevance-gateway.err.log"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "start {#MyServiceName}"; Flags: runhidden

[UninstallRun]
Filename: "{app}\kordi.exe"; Parameters: "purge-keyring --yes"; Flags: runhidden skipifdoesntexist; RunOnceId: "PurgeKeyring"
Filename: "{app}\nssm.exe"; Parameters: "stop {#MyServiceName}"; Flags: runhidden; RunOnceId: "StopService"
Filename: "{app}\nssm.exe"; Parameters: "remove {#MyServiceName} confirm"; Flags: runhidden; RunOnceId: "RemoveService"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; \
    Check: NeedsAddPath('{app}')

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

procedure RemoveFromPath(Param: string);
var
  OrigPath, NewPath: string;
  P: Integer;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', OrigPath)
  then
    exit;
  NewPath := ';' + OrigPath + ';';
  P := Pos(';' + Param + ';', NewPath);
  if P > 0 then
  begin
    Delete(NewPath, P, Length(Param) + 1);
    Delete(NewPath, 1, 1);
    Delete(NewPath, Length(NewPath), 1);
    RegWriteStringValue(HKEY_LOCAL_MACHINE,
      'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', NewPath);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: string;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RemoveFromPath(ExpandConstant('{app}'));

    DataDir := ExpandConstant('{%USERPROFILE}\.kordevance');
    if DirExists(DataDir) then
      DelTree(DataDir, True, True, True);
  end;
end;

[Dirs]
Name: "{commonappdata}\Kordevance\logs"

[Icons]
Name: "{group}\Uninstall Kordevance"; Filename: "{uninstallexe}"
