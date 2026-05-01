; Inno Setup 安装脚本 - 子网规划师 v3.0.0
; 该脚本用于创建 Subnet Planner 的 Windows 安装包
; 使用前请先运行 build_compile.py 生成 Nuitka 编译输出目录

#define MyAppName "子网规划师"
#define MyAppNameEn "SubnetPlanner"
#define MyAppVersion "3.0.0"
#define MyAppPublisher "Subnet Planner Team"
#define MyAppURL "https://gitcode.com/ejones-cn/Subnet_Planner"
#define MyAppExeName "SubnetPlanner.exe"
#define MyAppCopyright "Copyright (C) 2025-2026 Subnet Planner Team"

; 源目录定义
#define SourcePath "SubnetPlanner_Nuitka.dist"

[Setup]
AppId={{A5B8C9D0-E1F2-4A5B-8C9D-0E1F24A5B8C9}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright={#MyAppCopyright}
DefaultDirName={autopf}\{#MyAppNameEn}
DefaultGroupName="Subnet Planner"
AllowNoIcons=yes
; 输出配置
OutputDir=installer
OutputBaseFilename=SubnetPlannerV{#MyAppVersion}_Setup
SetupIconFile=icon.ico
; 压缩配置
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4
; 安装选项
DisableProgramGroupPage=yes
LicenseFile=LICENSE
PrivilegesRequired=admin
; 界面配置
WizardStyle=modern
WizardSizePercent=100
; 最低 Windows 版本（Windows 7 SP1）
MinVersion=6.1sp1
; 架构
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "chinesetraditional"; MessagesFile: "compiler:Languages\ChineseTraditional.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; 主程序
Source: "{#SourcePath}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; DLL 文件
Source: "{#SourcePath}\*.dll"; DestDir: "{app}"; Flags: ignoreversion
; PYD 文件
Source: "{#SourcePath}\*.pyd"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; 配置和翻译文件
Source: "{#SourcePath}\translations.json"; DestDir: "{app}"; Flags: ignoreversion
; 图标文件
Source: "{#SourcePath}\*.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; 所有子目录递归包含
Source: "{#SourcePath}\babel\*"; DestDir: "{app}\babel"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\jaraco\*"; DestDir: "{app}\jaraco"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\PIL\*"; DestDir: "{app}\PIL"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\tcl\*"; DestDir: "{app}\tcl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\tcl8\*"; DestDir: "{app}\tcl8"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\tk\*"; DestDir: "{app}\tk"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    Exec('icacls', ExpandConstant('"{app}" /grant Users:(OI)(CI)M'), '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
end;
