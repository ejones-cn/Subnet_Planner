# 安全迁移指南：保护现有项目成果

## 一、核心原则

**保护现有成果是迁移工作的首要任务**。在进行任何迁移工作前，请严格遵循以下原则：

1. **不修改主分支**：所有迁移工作在独立分支进行
2. **分离核心逻辑与GUI**：确保核心业务逻辑与GUI框架解耦
3. **充分测试**：任何修改都要有测试用例验证
4. **保留历史记录**：使用版本控制追踪所有变更
5. **渐进式迁移**：分阶段进行，确保每个阶段都可回滚

## 二、版本控制保护

### 1. Git 仓库初始化（如果尚未使用）

```bash
# 初始化Git仓库
git init

# 创建.gitignore文件
echo "# Windows
dist/
build/
*.exe
*.spec
*.log

# Python
__pycache__/
*.pyc

# IDE
.vs/
.idea/
*.swp
*.swo

# 证书文件
*.pfx
*.csr
" > .gitignore

# 提交初始版本
git add .
git commit -m "Initial commit: Subnet Planner v2.6.5"
```

### 2. 分支管理策略

```bash
# 创建迁移专用分支
git checkout -b android-migration

# 定期提交迁移进度
git add .
git commit -m "[android] 完成核心逻辑分离"
git commit -m "[android] 实现Kivy基础界面"

# 如需合并主分支更新
git checkout main
git pull
git checkout android-migration
git merge main
```

### 3. 备份策略

```bash
# 本地备份
tar -czf subnet_planner_backup_$(date +%Y%m%d).tar.gz --exclude='*.git' .

# 远程备份（推荐使用GitHub/Gitee）
git remote add origin <远程仓库URL>
git push -u origin main
git push -u origin android-migration
```

## 三、代码结构安全调整

### 1. 渐进式目录重构

**步骤1：创建核心逻辑目录**
```bash
mkdir -p core
mkdir -p common

# 复制核心逻辑文件到core目录（仅复制，不修改原文件）
cp ip_subnet_calculator.py core/
cp chart_utils.py core/
cp export_utils.py core/
cp i18n.py core/
cp version.py core/

# 复制公共资源到common目录
cp translations.json common/
cp -r Picture common/
```

**步骤2：创建平台特定目录**
```bash
mkdir -p windows
mkdir -p android

# 将Windows特定文件移动到windows目录
mv windows_app.py windows/
mv build_compile.py windows/
mv run_app.bat windows/
```

**步骤3：创建兼容层**
```python
# 创建core/__init__.py，实现兼容导入
from .ip_subnet_calculator import *
from .chart_utils import *
from .export_utils import *
from .i18n import *
from .version import *

# 创建windows/__init__.py
from .windows_app import *
```

### 2. 核心逻辑保护

**创建自动化测试套件**
```bash
# 运行现有测试
python -m pytest test_*.py -v

# 为core目录创建专用测试
mkdir -p test/core
cp test_*.py test/core/

# 修改测试导入路径
# 将所有测试文件中的导入语句从
# from ip_subnet_calculator import ...
# 改为
# from core.ip_subnet_calculator import ...
```

## 四、渐进式迁移流程

### 阶段1：核心逻辑分离（安全）
- ✅ 创建core目录，复制核心逻辑文件
- ✅ 创建兼容层，确保原有Windows应用仍可运行
- ✅ 运行所有测试，确保核心功能正常
- ✅ 提交代码到android-migration分支

### 阶段2：GUI框架替换（安全）
- ✅ 创建android目录，编写Kivy应用入口
- ✅ 实现基础界面，不影响原有功能
- ✅ 测试新界面与核心逻辑的集成
- ✅ 提交代码，保持主分支纯净

### 阶段3：功能完整迁移（安全）
- ✅ 逐步实现所有功能界面
- ✅ 每个功能模块都有测试用例
- ✅ 定期合并主分支更新
- ✅ 确保Windows版本和Android版本都可正常运行

### 阶段4：测试与优化（安全）
- ✅ 跨平台测试
- ✅ 性能优化
- ✅ 用户体验优化
- ✅ 安全审计

### 阶段5：发布准备（安全）
- ✅ 代码审查
- ✅ 最终测试
- ✅ 文档更新
- ✅ 合并到主分支（可选）

## 五、回滚机制

### 1. 分支回滚

```bash
# 查看提交历史
git log --oneline

# 回滚到指定提交
git checkout <commit_hash> .

# 或创建新分支继续开发
git checkout -b android-migration-v2 <commit_hash>
```

### 2. 目录结构回滚

```bash
# 如果目录结构调整出现问题，可恢复原结构
rm -rf core common windows android
cp windows/windows_app.py .
cp windows/build_compile.py .
cp windows/run_app.bat .
cp common/translations.json .
cp -r common/Picture .
cp core/* .
```

## 六、日常开发安全规范

### 1. 开发前更新

```bash
# 每次开发前更新主分支
git checkout main
git pull
git checkout android-migration
git merge main
```

### 2. 提交前验证

```bash
# 运行测试套件
python -m pytest test_*.py -v

# 验证Windows版本仍可编译运行
cd windows
python build_compile.py --no-onefile
cd ..
```

### 3. 代码审查

- 定期查看差异：`git diff main android-migration`
- 确保没有意外修改主分支代码
- 检查所有导入路径是否正确

## 七、现有Windows版本保护

### 1. 保留原有编译脚本

```bash
# 创建编译脚本备份
cp windows/build_compile.py windows/build_compile.py.backup

# 修改后的编译脚本仅用于迁移测试
# 原有编译脚本始终可用
python windows/build_compile.py.backup --type nuitka
```

### 2. 验证Windows版本正常运行

```bash
# 运行原有Windows应用
python windows/windows_app.py

# 或编译后运行
python windows/build_compile.py
./SubnetPlannerV2.6.5.exe
```

## 八、风险预警与应对

| 风险 | 预警信号 | 应对措施 |
|------|----------|----------|
| 核心逻辑被破坏 | 测试用例失败 | 回滚到上一个稳定版本，检查修改点 |
| Windows版本无法编译 | 编译脚本报错 | 使用备份的编译脚本，检查修改的核心文件 |
| 分支冲突 | git merge失败 | 手动解决冲突，优先保留主分支代码 |
| 依赖冲突 | 安装依赖时报错 | 使用虚拟环境隔离不同版本的依赖 |

## 九、结论

通过严格遵循以上安全迁移指南，可以确保现有项目成果得到充分保护，同时顺利进行安卓版本的迁移工作。请记住：**安全第一，渐进式迁移，充分测试**。

迁移过程中如有任何问题，可随时回滚到主分支，确保现有功能不受影响。

祝迁移工作顺利！
