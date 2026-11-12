@echo off
cd /d "%~dp0"
py -3 teacher_view.py
if errorlevel 1 pause
