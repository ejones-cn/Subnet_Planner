# GitHub Actions CI/CD 快速开始指南

## 📦 已创建的文件

| 文件 | 用途 |
|------|------|
| `.github/workflows/build.yml` | 主要构建工作流 |
| `.github/workflows/signpath.yml` | SignPath 签名工作流 |
| `docs/SignPath_Settings.md` | SignPath 详细集成说明 |
| `docs/Github_CI_Quickstart.md` | 本文件（本文档） |

---

## 🚀 快速开始

### 第 1 步：推送到 GitHub

确保代码已同步到 GitHub 仓库

```bash
git add .github/workflows/
git commit -m "Add GitHub Actions CI/CD"
git push origin main
```

### 第 2 步：启用 GitHub Actions

1. 访问 GitHub 仓库页面
2. 点击顶部 "Actions" 标签
3. 确认 Actions 已启用（默认已启用）

### 第 3 步：触发构建

#### 方式 A：推送代码
```bash
git push origin main
```

#### 方式 B：创建 Tag（会自动发布
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

#### 方式 C：手动触发
1. 访问 GitHub Actions → 选择工作流 → "Run workflow"

---

## 📥 下载构建产物

1. 打开 GitHub Action 构建完成
2. 选择一次成功的构建
3. 滚动到 "Artifacts" 区域
4. 下载：
   - `SubnetPlanner_Standalone：多文件版本
   - `SubnetPlanner_OneFile：单文件 EXE 版本
   - `SubnetPlanner_Signed`：签名版本（配置 SignPath 后）

---

## ⚙️ 配置详解

### 主要工作流功能 (`build.yml`)

- **触发条件**：
  - 推送到 `main` 或 `master` 分支
  - 创建以 `v` 开头的 Tag（如 `v1.0.0`）
  - Pull Request
  - 手动触发

- **包含作业**：
  - `build-standalone`：构建多文件版本（Windows）
  - `build-onefile`：构建单文件版本（Windows）
  - `release`：仅在 Tag 时自动创建 GitHub Release

---

## 📋 工作流参数

在 `.github/workflows/build.yml` 中可调整：

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `PYTHON_VERSION` | 3.10 | Python 版本 |
| `NUITKA_VERSION` | 2.1.1 | Nuitka 版本 |
| `timeout-minutes` | 90 | 超时时间（分钟） |
| `retention-days` | 30 | 产物保留天数 |

---

## 🔧 自定义构建

修改 `build.yml` 中的编译命令可自定义：

```yaml
python -m nuitka --mode=standalone \
  --follow-imports \
  # ... 更多参数
```

---

## 📌 注意事项

- 每个月免费额度：2000 分钟（Windows 按 2x 分钟计算）
- 构建时间：约 30-60 分钟每次
- 确保依赖使用清华源加速构建
- 镜像同步需等待（GitCode → GitHub）

---

## 🎯 下一步

1. **立即开始使用当前工作流（无需 SignPath 也可）
2. 如需代码签名 → 查看 `docs/SignPath_Settings.md`
3. 调整 CI → 推 Tag 自动发布到 GitHub Releases

---

## 💡 常用命令

| 任务 | 命令 |
|------|------|
| 查看 Actions | 访问 GitHub 仓库 → Actions |
| 下载构建 | Actions → 选择构建 → Artifacts |
| 创建发布 | `git tag v1.0.0 && git push origin v1.0.0` |
