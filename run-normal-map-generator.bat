@echo off
setlocal enabledelayedexpansion

:: Get directory (first argument, default to current if not provided)
set TARGET_DIR=%1
if "%TARGET_DIR%"=="" set TARGET_DIR=.

:: Get parameters from command line arguments
set STRENGTH=%2
if "%STRENGTH%"=="" set STRENGTH=1.0

set DISTANCE=%3
if "%DISTANCE%"=="" set DISTANCE=1

set CHUNK_SIZE=%4
if "%CHUNK_SIZE%"=="" set CHUNK_SIZE=100

set INVERT=%5
if "%INVERT%"=="" set INVERT=0

set WRAP=%6
if "%WRAP%"=="" set WRAP=0

:: Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python.
    exit /b 1
)

:: Check if the script exists
if not exist low_memory_normal_map.py (
    echo Could not find low_memory_normal_map.py in the current directory.
    exit /b 1
)

echo Normal Map Generator Batch Script
echo =================================
echo Processing images in: %TARGET_DIR%
echo Strength: %STRENGTH%
echo Distance: %DISTANCE%
echo Chunk Size: %CHUNK_SIZE%
echo Invert: %INVERT%
echo Wrap: %WRAP%
echo.

:: Count total images for progress reporting (excluding *_n.*)
set IMG_COUNT=0
for %%F in ("%TARGET_DIR%\*.png" "%TARGET_DIR%\*.jpg" "%TARGET_DIR%\*.jpeg" "%TARGET_DIR%\*.bmp" "%TARGET_DIR%\*.tif" "%TARGET_DIR%\*.tiff") do (
    set "FILENAME=%%~nF"
    if "!FILENAME:~-2!" NEQ "_n" (
        set /a IMG_COUNT+=1
    )
)

if %IMG_COUNT% equ 0 (
    echo No valid image files found in the specified directory.
    exit /b 1
)

echo Found %IMG_COUNT% images to process.
echo.
echo Starting processing...
echo.

:: Initialize counter for progress
set CURRENT=0

:: Process each image, skipping those with _n suffix
for %%F in ("%TARGET_DIR%\*.png" "%TARGET_DIR%\*.jpg" "%TARGET_DIR%\*.jpeg" "%TARGET_DIR%\*.bmp" "%TARGET_DIR%\*.tif" "%TARGET_DIR%\*.tiff") do (
    set "FILENAME=%%~nF"
    if "!FILENAME:~-2!" NEQ "_n" (
        set /a CURRENT+=1
        echo [!CURRENT!/%IMG_COUNT%] Processing: %%~nxF
        
        set CMD=python low_memory_normal_map_1.py "%%F" -s %STRENGTH% -d %DISTANCE% -c %CHUNK_SIZE%
        
        if "%INVERT%"=="1" set CMD=!CMD! -i
        if "%WRAP%"=="1" set CMD=!CMD! -w
        
        !CMD!
        echo.
    ) else (
        echo Skipping normal map: %%~nxF
    )
)

echo All images processed successfully!
exit /b 0