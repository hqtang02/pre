@echo off
cd /d "%~dp0"
py -3 teacher_demo.py
if errorlevel 1 pause
