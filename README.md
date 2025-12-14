# IP子网切分工具 v1.3.0

**IP子网切分工具** - 让网络管理变得简单高效！

## 📋 项目概述

IP子网切分工具是一个功能强大、易于使用的网络工具，旨在帮助网络管理员和工程师快速、准确地进行IP地址规划和子网划分。该工具支持CIDR表示法，能够自动计算子网信息，并提供友好的用户界面。

## ✨ 功能特性

- **CIDR输入支持**：直接输入CIDR格式的IP地址（如192.168.1.0/24）
- **子网切分**：从一个父网段中精确切分出一个指定的子网段
- **剩余网段自动计算**：切分后自动生成剩余可用的网段列表
- **全面的参数计算**：自动计算网络地址、广播地址、可用IP范围、子网掩码、通配符掩码等
- **清晰的结果展示**：直观展示切分网段和剩余网段的详细信息
- **多种界面支持**：提供Web界面和Windows GUI界面，满足不同使用场景
- **图表可视化**：提供网段分布的图表可视化
- **结果导出功能**：Windows GUI界面支持将计算结果导出为文本文件（仅Windows版本）

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

## 🔍 代码自动审查

项目集成了多种Python代码审查工具，帮助保持代码质量和风格一致性：

### 使用方法

```bash
.code_review.bat
```

### 包含的工具

1. **Pylint** - 代码质量检查，检测潜在问题和错误
2. **Flake8** - 代码风格检查，确保符合PEP 8标准
3. **isort** - 自动排序导入语句，保持一致性
4. **Black** - 自动格式化代码，统一代码风格
5. **compileall** - 编译检查，确保代码语法正确

### 配置文件

- `.pylintrc` - Pylint配置文件
- `.flake8` - Flake8配置文件
- `pyproject.toml` - Black和isort配置文件

### 审查报告

运行代码审查脚本后，将依次显示各工具的检查结果。对于发现的问题，部分工具（如isort和Black）提供自动修复功能。


> 注意：项目已配置国内PyPI镜像源（阿里云），安装依赖时会自动使用国内下载源，提高下载速度。
> 如果需要使用其他国内镜像源，可以修改项目根目录下的`.pip/pip.conf`文件。

### 使用方法

#### Web界面

**方式一：直接运行Python脚本**

```bash
python web_app.py
```

然后在浏览器中访问 `http://localhost:5000`

**方式二：使用批处理脚本**

```bash
.run_web_app.bat
```

#### Windows GUI界面

**方式一：直接运行Python脚本**

```bash
python windows_app.py
```

**方式二：使用批处理脚本**

```bash
.run_app.bat
```

**方式三：使用可执行文件**

直接运行 `dist/IP子网分割工具.exe`

## 🛠️ 工具原理

本工具基于IPv4地址的子网划分原理，利用Python的`ipaddress`模块实现了以下核心功能：

1. **IP地址解析与转换**：将输入的IP地址字符串转换为整数格式，便于进行网络计算
2. **子网掩码计算**：根据CIDR前缀长度自动计算子网掩码
3. **网络地址计算**：自动识别并计算网络地址
4. **广播地址计算**：自动计算广播地址
5. **子网切分算法**：从父网段中精确切分出指定子网段，并智能生成剩余可用的网段列表
6. **可用IP范围计算**：计算每个子网的可用IP数量和范围
7. **通配符掩码计算**：计算子网掩码的反码（通配符掩码）

## 📁 文件结构

```
Netsub tools/
├── windows_app.py       # Windows GUI界面主程序
├── web_app.py           # Web界面主程序
├── ip_subnet_calculator.py  # IP子网计算核心模块
├── version.py           # 版本号管理模块
├── requirements.txt     # 项目依赖
├── README.md            # 项目说明文档
├── run_app.bat          # Windows GUI界面快速启动脚本
├── run_web_app.bat      # Web界面快速启动脚本
├── refresh_icon_cache.bat  # 刷新图标缓存脚本
├── bump_version.py      # 自动版本号更新脚本
├── verify_versions.py   # 版本号一致性验证工具
├── simple_pack.py       # 打包脚本
├── create_self_signed_cert.bat  # 创建自签名证书脚本
├── update_web_app_version.py  # 更新Web应用版本脚本
├── dist/                # 打包后的可执行文件目录
│   ├── IP子网分割工具.exe  # Windows可执行文件
│   └── icon.ico         # 应用程序图标
├── icon.ico             # 应用程序图标
├── icon.svg             # 应用程序图标SVG源文件
└── IMPLEMENTATION_SUMMARY.md  # 实现摘要文档
```

## 🖼️ 界面预览

### Web界面

- **简洁直观**：清晰的输入区域和结果展示区域
- **响应式设计**：适配不同屏幕尺寸
- **实时计算**：输入后立即显示计算结果

### Windows GUI界面

- **现代化界面**：使用Tkinter构建的友好图形界面
- **多标签页**：分别展示输入、结果和帮助信息
- **导出功能**：支持将结果导出为文本文件

## 🔧 技术特点

- **跨平台**：支持Windows、Linux和macOS
- **轻量级**：依赖少，安装简单
- **高性能**：快速处理大量IP地址计算
- **易于扩展**：模块化设计，便于添加新功能
- **开源免费**：基于MIT许可证开源

## 📊 示例输出

### 功能说明
本工具的核心功能是**子网切分**：从一个父网段中切分出一个指定的子网段，并返回剩余的网段列表。

### 示例：从父网段中切分出一个子网段

输入：
- 父网段: `10.0.0.0/8`
- 切分网段: `10.21.60.0/23`

输出结果：

```
父网段: 10.0.0.0/8
切分网段: 10.21.60.0/23

切分网段信息:
  network: 10.21.60.0
  netmask: 255.255.254.0
  wildcard: 0.0.1.255
  broadcast: 10.21.61.255
  cidr: 10.21.60.0/23
  prefixlen: 23
  num_addresses: 512
  usable_addresses: 510

剩余网段 (15 个):

网段 1:
  network: 10.0.0.0
  netmask: 255.255.255.0
  wildcard: 0.0.0.255
  broadcast: 10.0.0.255
  cidr: 10.0.0.0/24
  prefixlen: 24
  num_addresses: 256
  usable_addresses: 254

网段 2:
  network: 10.0.1.0
  netmask: 255.255.254.0
  wildcard: 0.0.1.255
  broadcast: 10.0.2.255
  cidr: 10.0.1.0/23
  prefixlen: 23
  num_addresses: 512
  usable_addresses: 510

网段 3:
  network: 10.0.3.0
  netmask: 255.255.252.0
  wildcard: 0.0.3.255
  broadcast: 10.0.6.255
  cidr: 10.0.3.0/22
  prefixlen: 22
  num_addresses: 1024
  usable_addresses: 1022

网段 4:
  network: 10.0.7.0
  netmask: 255.255.255.0
  wildcard: 0.0.0.255
  broadcast: 10.0.7.255
  cidr: 10.0.7.0/24
  prefixlen: 24
  num_addresses: 256
  usable_addresses: 254
  ...

网段 8:
  network: 10.21.62.0
  netmask: 255.255.254.0
  wildcard: 0.0.1.255
  broadcast: 10.21.63.255
  cidr: 10.21.62.0/23
  prefixlen: 23
  num_addresses: 512
  usable_addresses: 510
  ...

网段 15:
  network: 10.128.0.0
  netmask: 255.128.0.0
  wildcard: 0.127.255.255
  broadcast: 10.255.255.255
  cidr: 10.128.0.0/9
  prefixlen: 9
  num_addresses: 8388608
  usable_addresses: 8388606
```

## ⚠️ 注意事项

1. 确保输入的IP地址和CIDR前缀长度格式正确
2. 子网切分时，确保切分网段必须是父网段的子集，否则会导致计算错误
3. Web界面需要Python环境和Flask框架支持，运行前请确保已安装所有依赖
4. Windows GUI界面需要Python环境和Tkinter库支持，Tkinter通常随Python一起安装
5. 如果遇到防火墙问题，请确保允许Python或生成的可执行文件通过防火墙
6. 工具目前主要支持IPv4地址，不支持IPv6地址
7. 在使用批量处理功能时，确保输入文件格式正确（每行一个网段）
8. 结果导出功能仅在Windows GUI版本中可用

## 📝 更新日志

### v1.2.1 (2025-12-11)

- 实现了自动生成版本号功能
- 添加了`bump_version.py`脚本，支持自动递增版本号
- 添加了`verify_versions.py`脚本，用于验证所有文件版本号一致性
- 添加了`version.py`模块，集中管理版本号
- 更新了文档，修复了Windows GUI界面运行命令错误
- 优化了文件结构说明

### v1.2.0 (2025-12-10)

- 添加了`run_web_app.bat`批处理脚本，支持快速启动Web界面
- 更新了文档结构，优化了使用说明
- 新增了`dist`目录说明，包含打包后的可执行文件
- 添加了`refresh_icon_cache.bat`脚本，用于刷新Windows图标缓存
- 修复了README.md中的换行问题
- 优化了界面布局和用户体验

### v1.1.0 (2025-12-05)

- 新增了Web界面支持
- 优化了子网计算算法
- 改进了结果展示格式
- 修复了已知bug

### v1.0.0 (2025-11-30)

- 初始版本发布
- 支持CIDR输入和子网划分
- 提供Windows GUI界面
- 实现了基本的IP子网计算功能

## 📄 许可证

本项目基于MIT许可证开源，详情请查看LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目！

## 📞 联系方式

如果您有任何问题或建议，请通过以下方式联系我：

- 邮箱：[ejones.cn@hotmail.com](mailto:ejones.cn@hotmail.com)  
- GitCode：https://gitcode.com/ejones-cn/Netsub-tools
- Gitee：https://gitee.com/ejones-cn/netsub-tools

---

**IP子网切分工具** - 让IP地址管理变得简单高效！
