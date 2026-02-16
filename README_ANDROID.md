# Subnet Planner 安卓版迁移方案

## 项目现状分析

- **当前技术栈**：Python + Tkinter
- **目标平台**：Windows
- **编译方式**：Nuitka 或 PyInstaller 编译成 Windows 可执行文件
- **主要功能**：子网规划、IP地址计算、子网分割、合并等

## 安卓迁移可行性

### 1. Tkinter 局限性
Tkinter 是 Python 的标准 GUI 库，主要用于桌面应用开发，**不支持直接编译成安卓应用**。要迁移到安卓平台，需要更换 GUI 框架。

### 2. 可选方案

| 方案 | 优势 | 劣势 | 推荐度 |
|------|------|------|--------|
| Kivy | 纯 Python 开发，支持多平台 | 性能一般，社区相对较小 | ⭐⭐⭐ |
| BeeWare | 纯 Python 开发，原生 UI | 成熟度较低，文档不完善 | ⭐⭐ |
| Flutter + Python | 高性能，现代 UI，支持 Python 后端 | 需要学习 Dart，混合开发复杂度高 | ⭐⭐⭐⭐ |
| React Native + Python | 跨平台，社区大 | 需要学习 JavaScript，混合开发复杂度高 | ⭐⭐⭐ |

### 3. 推荐方案
**Kivy 框架** - 最适合现有 Python 项目的迁移，原因如下：

- 纯 Python 开发，无需学习新语言
- 支持 Windows、macOS、Linux、Android、iOS 多平台
- 拥有成熟的网络、图形、输入等组件
- 可以复用大部分现有业务逻辑代码

## 迁移步骤

### 1. 环境搭建

```bash
# 安装 Kivy 及依赖
pip install kivy[base] kivy_examples

# 安装安卓打包工具
pip install buildozer
```

### 2. 代码重构

#### 2.1 目录结构调整
```
Subnet_Planner/
├── core/              # 核心业务逻辑（可复用）
│   ├── ip_subnet_calculator.py
│   ├── chart_utils.py
│   ├── export_utils.py
│   └── ...
├── android/           # 安卓平台特定代码
│   ├── main.py        # Kivy 应用入口
│   ├── screens/       # 各个页面
│   ├── widgets/       # 自定义组件
│   └── ...
├── windows/           # Windows 平台特定代码
│   ├── windows_app.py
│   └── ...
├── common/            # 公共资源
│   ├── translations.json
│   ├── Picture/
│   └── ...
└── buildozer.spec     # Buildozer 配置文件
```

#### 2.2 核心逻辑复用
- 将 `ip_subnet_calculator.py`、`chart_utils.py` 等核心逻辑移至 `core/` 目录
- 确保核心逻辑不依赖 Tkinter
- 为核心逻辑添加单元测试，确保迁移后功能正常

#### 2.3 GUI 重写
- 使用 Kivy 重写所有 Tkinter 界面
- 适配安卓屏幕尺寸和触摸操作
- 实现响应式设计

### 3. 打包配置

创建 `buildozer.spec` 配置文件：

```ini
[app]
title = Subnet Planner
package.name = subnetplanner
package.domain = com.subnetplanner
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 2.6.5

requirements = python3,kivy

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 0

android.api = 31
android.sdk = 21
android.ndk = 23
android.arch = arm64-v8a
android.buildtools = 31.0.0
android.use_aapt2 = True

ios.codesign.allowed = false
```

### 4. 编译打包

```bash
# 初始化 Buildozer 配置
buildozer init

# 编译安卓 APK
buildozer -v android debug
```

## 迁移工作量评估

| 模块 | 工作量 | 备注 |
|------|--------|------|
| 核心逻辑重构 | ⭐⭐ | 主要是解耦 Tkinter 依赖 |
| GUI 重写 | ⭐⭐⭐⭐ | 需要重新实现所有界面 |
| 测试调试 | ⭐⭐⭐ | 跨平台测试工作量大 |
| 打包发布 | ⭐⭐ | 需要配置安卓签名等 |

## 预期效果

- ✅ 支持安卓平台运行
- ✅ 保留原有所有功能
- ✅ 适配安卓触摸操作
- ✅ 支持多语言
- ✅ 支持离线使用

## 风险与应对

| 风险 | 应对措施 |
|------|----------|
| Kivy 性能问题 | 优化代码，使用 Kivy 的优化技巧 |
| 安卓权限问题 | 合理申请权限，提供权限说明 |
| 屏幕适配问题 | 使用 Kivy 的响应式布局 |
| 打包失败 | 参考 Buildozer 官方文档，排查依赖问题 |

## 后续计划

1. **第一阶段**：搭建 Kivy 开发环境，实现简单界面
2. **第二阶段**：重构核心逻辑，解耦 Tkinter 依赖
3. **第三阶段**：重写所有功能界面
4. **第四阶段**：测试调试，优化性能
5. **第五阶段**：打包发布到 Google Play

## 结论

Subnet Planner 可以迁移到安卓平台，推荐使用 Kivy 框架进行迁移。虽然需要重写 GUI 部分，但核心业务逻辑可以大部分复用，迁移工作量可控。