# 子网规划工具 (Subnet Planner Android)

一个基于Flutter开发的子网规划工具，用于帮助网络管理员进行子网划分、规划和计算。

## 功能特性

### 1. 子网切分 (Subnet Split)
- 输入父网段和要切分的网段
- 自动计算并显示父网段、切分网段和剩余网段信息
- 结果包括：CIDR、网络地址、子网掩码、广播地址、地址总数
- 支持查看剩余网段列表

### 2. 子网规划 (Subnet Plan)
- 根据主机数量自动规划子网
- 生成子网分配表
- 可视化子网结构
- 导出子网规划报告

### 3. 高级工具 (Advanced Tools)
- 子网计算：计算子网掩码、广播地址等
- 地址转换：IP地址与二进制/十六进制转换
- 地址查询：查询IP地址所属区域
- 子网验证：验证子网划分是否正确
- 历史记录：查看历史操作记录
- 设置：应用设置和偏好

## 技术栈

- **框架**：Flutter 3.0+
- **状态管理**：Provider
- **UI组件**：Material Design
- **图表库**：fl_chart
- **文件操作**：path_provider
- **数据处理**：csv
- **本地存储**：shared_preferences
- **国际化**：intl

## 项目结构

```
subnet_planner_android/
├── lib/
│   ├── main.dart              # 应用入口
│   ├── providers/
│   │   └── app_provider.dart  # 状态管理
│   └── pages/
│       ├── home_page.dart     # 主页面（底部导航）
│       ├── split_page.dart    # 子网切分页面
│       ├── plan_page.dart     # 子网规划页面
│       └── tools_page.dart    # 高级工具页面
├── assets/                    # 资源目录
├── pubspec.yaml               # 项目配置
└── README.md                  # 项目说明
```

## 安装与运行

### 前提条件

- **Flutter SDK 3.0+**：需要先安装并配置 Flutter SDK
- **Dart SDK 3.0+**：Flutter SDK 已包含 Dart SDK
- **Android Studio / VS Code**：用于开发和运行应用
- **安卓模拟器或真机**：用于测试应用

### Flutter SDK 安装步骤

如果您还没有安装 Flutter SDK，请按照以下步骤操作：

1. **下载 Flutter SDK**：
   - 访问 [Flutter 官方下载页面](https://flutter.dev/docs/get-started/install)
   - 下载适合您操作系统的 Flutter SDK 压缩包

2. **解压并配置**：
   - **Windows**：
     - 将下载的压缩包解压到您想要安装 Flutter 的位置（如 `C:\src\flutter`）
     - 将 `flutter\bin` 目录添加到系统环境变量 `PATH` 中
   - **Linux/macOS**：
     - 将下载的压缩包解压到您想要安装 Flutter 的位置（如 `~/development/flutter`）
     - 将 `flutter/bin` 目录添加到您的 shell 配置文件中（如 `.bashrc` 或 `.zshrc`）

3. **验证安装**：
   - 打开新的终端窗口
   - 运行 `flutter --version` 检查 Flutter 是否正确安装
   - 运行 `flutter doctor` 检查开发环境是否配置完整

4. **配置开发环境**：
   - 根据 `flutter doctor` 的提示安装缺少的依赖
   - 配置 Android Studio 或 VS Code 的 Flutter 插件

详细的安装指南请参考 [Flutter 官方文档](https://flutter.dev/docs/get-started/install)。

### 安装步骤

1. 克隆项目
2. **设置国内镜像源**（可选，加速依赖下载）：
   - Windows：运行 `setup_mirrors.ps1` PowerShell脚本
   - 或手动设置环境变量（根据不同Shell选择）：
     - **Windows PowerShell**：
       ```powershell
       $env:PUB_HOSTED_URL = "https://mirrors.aliyun.com/dart-pub/"
       $env:FLUTTER_STORAGE_BASE_URL = "https://mirrors.aliyun.com/flutter/"
       ```
     - **Windows CMD**：
       ```cmd
       set PUB_HOSTED_URL=https://mirrors.aliyun.com/dart-pub/
       set FLUTTER_STORAGE_BASE_URL=https://mirrors.aliyun.com/flutter/
       ```
   - **Linux/macOS Bash**：
     ```bash
     export PUB_HOSTED_URL=https://mirrors.aliyun.com/dart-pub/
     export FLUTTER_STORAGE_BASE_URL=https://mirrors.aliyun.com/flutter/
     ```
3. 运行 `flutter pub get` 安装依赖
4. 运行 `flutter run` 启动应用

## 使用说明

### 子网切分

1. 在「子网切分」页面输入父网段（如：10.0.0.0/8）
2. 输入要切分的网段（如：10.1.0.0/16）
3. 点击「执行切分」按钮
4. 查看切分结果，包括父网段、切分网段和剩余网段信息

### 子网规划

1. 在「子网规划」页面输入网络地址和子网掩码
2. 设置每个子网所需的主机数量
3. 点击「自动规划」按钮
4. 查看生成的子网规划结果

### 高级工具

- 点击对应的工具卡片进入相应功能
- 按照提示输入信息并执行操作

## 开发说明

### 状态管理

使用Provider进行状态管理，主要管理：
- 当前选中的标签页
- 历史记录
- 子网切分逻辑

### 数据模型

- `AppProvider`：全局状态管理
- 子网信息：包含CIDR、网络地址、子网掩码、广播地址、地址总数等字段

### 核心算法

- 子网切分算法：`splitSubnet(String parent, String split)`
- IP地址计算：将CIDR转换为网络地址、子网掩码、广播地址等

## 待实现功能

- [ ] 完整的子网规划算法
- [ ] 子网计算工具
- [ ] 地址转换工具
- [ ] 地址查询工具
- [ ] 子网验证工具
- [ ] 历史记录查看
- [ ] 应用设置

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱：your-email@example.com
- GitHub：https://github.com/your-username/subnet-planner-android
