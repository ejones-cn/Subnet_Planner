; Inno Setup 安装脚本 - 子网规划师 v3.0.0
; 该脚本用于创建 Subnet Planner 的 Windows 安装包
; 使用前请先运行 build_compile.py 或 build_package.py 生成打包目录

#define MyAppName "子网规划师"
#define MyAppNameEn "SubnetPlanner"
#define MyAppVersion "3.0.0"
#define MyAppPublisher "Subnet Planner Team"
#define MyAppURL "https://gitcode.com/ejones-cn/Subnet_Planner"
#define MyAppExeName "SubnetPlanner.exe"
#define MyAppCopyright "Copyright (C) 2025-2026 Subnet Planner Team"

; 源目录定义（支持多种编译输出路径）
#define SourcePath "SubnetPlannerV{#MyAppVersion}_Package"
#define FallbackPath "SubnetPlanner_Nuitka.dist"

[Setup]
; 基本配置
AppId={A5B8C9D0-E1F2-4A5B-8C9D-0E1F24A5B8C9}
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
SetupIconFile={#SourcePath}\icon.ico
; 压缩配置
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4
; 安装选项
DisableProgramGroupPage=yes
LicenseFile=
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
; 界面配置
WizardStyle=modern
WizardSizePercent=100
; 最低 Windows 版本（Windows 7）
MinVersion=6.1
; 架构
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 主程序（支持多种源目录）
Source: "{#SourcePath}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\*.dll"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "{#SourcePath}\*.pyd"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; 配置文件
Source: "{#SourcePath}\translations.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\SubnetPlanner_config.json"; DestDir: "{app}"; Flags: ignoreversion
; 图片资源已嵌入代码中
; 其他必要文件
Source: "{#SourcePath}\*.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function InitializeSetup(): Boolean;
var
  SourceExists: Boolean;
begin
  SourceExists := DirExists(ExpandConstant('{#SourcePath}'));
  
  if not SourceExists then
  begin
    SourceExists := DirExists(ExpandConstant('{#FallbackPath}'));
    if SourceExists then
    begin
      MsgBox('警告：未找到标准打包目录！' + #13#10 + 
             '已检测到 Nuitka 编译输出目录，将使用它进行打包。' + #13#10 + 
             '建议先运行 build_package.py 生成标准打包目录。', mbWarning, MB_OK);
    end
    else
    begin
      MsgBox('错误：未找到打包目录！' + #13#10 + 
             '请先运行以下命令生成打包目录：' + #13#10 + 
             'python build_package.py', mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
  
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 安装后操作（如需要）
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
end;
