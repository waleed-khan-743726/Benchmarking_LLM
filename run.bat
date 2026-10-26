@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\Robot_Navigation_FYP\scripts\run.ps1"
if errorlevel 1 pause

