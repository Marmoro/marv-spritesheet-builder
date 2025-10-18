
@echo off
IF "%~1"=="" (
    echo Please provide an input directory path
    echo Usage: %~nx0 "C:\your\path"
    exit /b 1
)
powershell -ExecutionPolicy Bypass -File .\advanced-automate-sprite-sheet-auto.ps1 -InputDirectory "%~1"
pause