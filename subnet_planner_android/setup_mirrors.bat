@echo off
REM 设置Flutter国内镜像源
echo 设置Flutter国内镜像源...
set PUB_HOSTED_URL=https://mirrors.aliyun.com/dart-pub/
set FLUTTER_STORAGE_BASE_URL=https://mirrors.aliyun.com/flutter/

echo 已设置国内镜像源：
echo PUB_HOSTED_URL=%PUB_HOSTED_URL%
echo FLUTTER_STORAGE_BASE_URL=%FLUTTER_STORAGE_BASE_URL%
echo.
echo 现在可以运行 flutter pub get 或其他 Flutter 命令了。
pause
