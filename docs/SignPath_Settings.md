# SignPath 代码签名集成指南

## 概览

SignPath 提供开源项目的免费代码签名服务，帮助解决杀毒软件误报问题。

---

## 一、准备工作

### 1.1 前置条件

- 项目在 GitHub 上是公开的（开源项目）
- 仓库链接：https://github.com/ejones-cn/Subnet_Planner

---

## 二、申请 SignPath 开源计划

### 2.1 注册 SignPath 账号

1. 访问 https://about.signpath.org/
2. 点击 "Get Started for Free（免费开始）
3. 使用 GitHub 账号登录

### 2.2 申请开源项目计划

1. 访问 https://about.signpath.org/apply
2. 填写项目信息：
   - 项目名称：SubnetPlanner
   - GitHub 仓库 URL
   - 开源许可证（MIT/Apache 等）
   - 项目描述
3. 提交申请，等待审核（通常1-3个工作日）

---

## 三、配置 SignPath

### 3.1 安装 SignPath GitHub App

1. 审核通过后，访问 SignPath 会提供安装链接
2. 在 GitHub 上安装 SignPath App
3. 选择要启用的仓库（SubnetPlanner）

### 3.2 创建项目

1. 在 SignPath 中创建新项目
2. 设置项目名称：SubnetPlanner
3. 配置签名策略（Signing Policy）

---

## 四、集成 GitHub Actions

### 4.1 配置 SignPath 工作流

修改 `.github/workflows/signpath.yml`

```yaml
name: SignPath Code Signing

on:
  workflow_run:
    workflows: ["Build SubnetPlanner"]
    types:
      - completed
  workflow_dispatch:

jobs:
  sign-with-signpath:
    name: Sign with SignPath
    runs-on: windows-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch' }}
    permissions:
      id-token: write
      actions: read
      contents: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: SubnetPlanner_OneFile
          path: ./artifacts/onefile/
      
      - name: Sign EXE with SignPath
        uses: signpath/github-action@v3
        with:
          organization: 你的组织ID
          project: SubnetPlanner
          signing-policy: 你的策略名称
          artifact: ./artifacts/onefile/*.exe
          output-path: ./artifacts/signed/
        env:
          SIGNPATH_API_TOKEN: ${{ secrets.SIGNPATH_API_TOKEN }}
      
      - name: Upload signed artifacts
        uses: actions/upload-artifact@v4
        with:
          name: SubnetPlanner_Signed
          path: ./artifacts/signed/
```

---

## 五、配置 GitHub Secrets

在 GitHub 仓库设置 → Secrets and variables → Actions

添加以下 Secrets：

| Secret 名称 | 说明 | 获取位置 |
|----------|------|---------|
| SIGNPATH_API_TOKEN | SignPath API Token | SignPath 项目设置 → API Tokens |
| SIGNPATH_ORGANIZATION_ID | SignPath 组织 ID | SignPath 组织设置 |
| SIGNPATH_PROJECT_ID | SignPath 项目 ID | SignPath 项目设置 |

---

## 六、工作流程

### 完整流程

```
GitCode（推送代码）
    ↓
GitHub（自动镜像）
    ↓
GitHub Actions（自动构建 EXE）
    ↓
SignPath（自动签名）
    ↓
下载签名后的 EXE（已解决误报问题）
```

---

## 七、替代方案（如果 SignPath 无法使用）

### 7.1 方案 A：购买商业证书

如果不想等待 SignPath 审核，可以购买商业代码签名证书：

| 证书提供商 | 价格范围 | 适用场景 |
|----------|---------|---------|
| Sectigo | $179-299/年 | 个人开发/小型项目 |
| DigiCert | $299-499/年 | 企业级项目 |
| GlobalSign | $249-499/年 | 全功能证书 |

### 7.2 方案 B：自签名（仅用于测试）

在 `build_compile.py` 已有自签名支持，使用 `--pfx-password` 参数即可。

---

## 八、常见问题

### Q: SignPath 申请被拒绝怎么办？

A: 确保你的项目必须是真正的开源项目，有 README、许可证和一定的提交历史。可以尝试：

1. 完善项目文档
2. 添加开源许可证文件
3. 增加几个有意义的提交
4. 重新提交申请

### Q: 签名后的 EXE 还被误报怎么办？

A: 签名后误报率会显著降低，但仍有可能。可以：

1. 向杀毒软件厂商提交误报
2. 使用多个杀毒引擎测试（VirusTotal）
3. 提供使用说明

### Q: 如何测试签名效果？

A: 将签名后的 EXE 上传到 https://www.virustotal.com/ 扫描，查看检测结果。

---

## 九、参考资料

- SignPath 官方文档: https://docs.signpath.org/
- SignPath GitHub Actions: https://github.com/signpath/github-action
- GitHub Actions 文档: https://docs.github.com/en/actions
