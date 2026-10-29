@echo off
setlocal
cd /d "%~dp0"
title Hardwood Local Development Server
echo ========================================================
echo Starting Hardwood local server for preview and testing...
echo ========================================================
python run_dev.py
if errorlevel 1 (
    echo.
    echo Server stopped with error.
    pause
)
endlocal
