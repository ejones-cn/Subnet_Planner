@echo off
echo 🔄 开始推送代码和标签到远程仓库...
echo.

echo 📤 推送代码到main分支...
git push origin main

echo.
echo 🏷️  同步所有标签到远程仓库...
git push --tags

echo.
echo ✅ 推送完成！
echo.
echo 📋 当前标签状态:
git tag -l --sort=-version:refname | head -5

pause