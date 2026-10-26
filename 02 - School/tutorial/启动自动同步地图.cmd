@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0.atlas\launch.ps1"
if errorlevel 1 pause
