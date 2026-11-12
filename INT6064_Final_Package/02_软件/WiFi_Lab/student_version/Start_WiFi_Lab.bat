
@echo off
cd /d "%~dp0"

py -3 gui.py

if errorlevel 1 (
    echo.
    echo Failed to start Campus Wi-Fi Coding Lab.
    pause
)
