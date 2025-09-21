@echo off
echo ==========================================
echo   GreenCode AI - Project Cleanup Tool
echo ==========================================
echo.
echo This will help you clean up unnecessary files to reduce project size.
echo.
pause

powershell -ExecutionPolicy Bypass -File "cleanup_project.ps1"

pause