# 分离Web版和Windows版版本号计划

## 目标

将Web版的版本号从Windows版中分离出来，单独更新，并将Web版初始版本号设置为1.0.0，重新开始迭代。

## 实现步骤

1. **创建Web版独立版本管理文件**

   * 创建 `web_version.py` 文件，用于管理Web版的版本号

   * 初始版本号设置为1.0.0

2. **修改web\_app.py**

   * 将版本号导入从 `version` 改为 `web_version`

   * 确保HTML模板中正确显示Web版的版本号

3. **更新update\_web\_app\_version.py脚本**

   * 修改脚本，使其从 `web_version.py` 获取版本号，而不是 `version.py`

   * 确保只更新Web版相关文件中的版本号

4. **修改verify\_versions.py脚本**

   * 分离Windows版和Web版的版本验证逻辑

   * 分别验证两个版本号的一致性

5. **更新相关文件中的版本号引用**

   * 确保所有引用Web版版本号的地方都使用新的 `web_version.py`

## 预期结果

* Windows版和Web版将拥有独立的版本号

* Web版初始版本号为1.0.0，可独立更新

* 版本验证系统能够分别验证两个版本号的一致性

* 所有功能保持正常运行

## 文件修改列表

* `web_version.py` (新建)

* `web_app.py` (修改)

* `update_web_app_version.py` (修改)

* `verify_versions.py` (修改)

