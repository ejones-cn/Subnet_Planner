@echo off
REM Subnet Planner Compile Script
REM Default to multi-file mode to reduce antivirus false positives

REM Display help information
echo ===========================================
echo Subnet Planner Compile Script
REM Use --help for detailed parameter help
echo ===========================================
echo 
echo Running with default settings...
echo - Multi-file mode (--no-onefile)
echo - Nuitka compiler (default)
echo 
echo To change compiler: --type pyinstaller or --type both
echo To use single-file mode: --onefile
echo ===========================================
echo.

REM Default to multi-file mode to reduce antivirus false positives
python build_compile.py --no-onefile %*

pause