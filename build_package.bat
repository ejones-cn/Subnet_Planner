@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo          Subnet Planner 一键打包脚本
echo ============================================================
echo.
python build_package.py
echo.
pause
