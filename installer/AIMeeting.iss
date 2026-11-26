; Inno Setup script. Build with: iscc installer\AIMeeting.iss (after build_exe.ps1)
[Setup]
AppName=AI Meeting Intelligence
AppVersion=1.0
DefaultDirName={autopf}\AIMeeting
DefaultGroupName=AI Meeting Intelligence
OutputDir=..\dist
OutputBaseFilename=AIMeeting-Setup
Compression=lzma2/fast
DiskSpanning=yes
DiskSliceSize=2000000000
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
Source: "..\dist\AIMeeting\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\AI Meeting Intelligence"; Filename: "{app}\AIMeeting.exe"
Name: "{autodesktop}\AI Meeting Intelligence"; Filename: "{app}\AIMeeting.exe"

[Run]
Filename: "{app}\AIMeeting.exe"; Description: "Launch AI Meeting Intelligence"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
