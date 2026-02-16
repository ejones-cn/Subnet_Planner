# Subnet Planner 编译指南

## 编译选项

### 基本编译命令

```bash
# 使用Nuitka编译（默认）
python build_compile.py

# 使用PyInstaller编译
python build_compile.py --type pyinstaller

# 同时使用两种方式编译
python build_compile.py --type both
```

### 减少杀毒软件误报的选项

为了减少Windows Defender等杀毒软件的误报，我们提供了以下优化选项：

#### 1. 禁用UPX压缩

UPX压缩是常见的误报原因，我们已默认在PyInstaller编译中禁用了UPX压缩。

#### 2. 选择多文件编译模式

单文件编译模式（`--onefile`）更容易被误报，你可以尝试使用多文件编译模式：

```bash
# 使用多文件编译模式
python build_compile.py --no-onefile
```

#### 3. 排除不必要的模块

我们已在编译选项中排除了许多不必要的模块，如测试模块、电子邮件模块等，以减少可执行文件的复杂度。

#### 4. 禁用链接时优化（LTO）

链接时优化可能会产生被误报的代码模式，我们已默认禁用。

#### 5. 添加数字签名

如果您有数字证书，可以使用以下命令为可执行文件添加签名：

```bash
# 使用PFX证书签名
python build_compile.py --pfx-password "your_password"

# 或使用命令行工具指定signtool路径
python build_compile.py --signtool-path "C:\path\to\signtool.exe" --pfx-password "your_password"
```

### 其他选项

```bash
# 指定输出目录
python build_compile.py --output "dist"

# 清理构建文件
python build_compile.py --clean

# 仅安装依赖
python build_compile.py --install-deps
```

## 减少误报的最佳实践

1. **使用多文件编译模式**：`--no-onefile`选项生成的可执行文件被误报的概率更低
2. **确保代码签名**：如果可能，为可执行文件添加数字签名
3. **定期更新编译工具**：保持Nuitka和PyInstaller的最新版本
4. **向杀毒软件报告误报**：如果您的程序被误报，向相关杀毒软件厂商报告
5. **避免使用可疑的第三方库**：只使用可信的库，并定期更新

## 常见问题

### Q: 编译后的程序被Windows Defender报毒怎么办？

A: 尝试以下方法：

1. 使用多文件编译模式：`python build_compile.py --no-onefile`
2. 确保您使用的是最新版本的编译工具
3. 向Microsoft Defender报告误报
4. 考虑为您的程序添加数字签名

### Q: 如何查看编译命令？

A: 编译脚本会在执行前打印完整的编译命令，您可以查看并根据需要调整。

### Q: 如何安装编译依赖？

A: 执行以下命令：

```bash
python build_compile.py --install-deps
```

## 联系方式

如果您在编译过程中遇到问题，请随时联系我们。
