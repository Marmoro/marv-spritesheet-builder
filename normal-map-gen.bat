@echo off
setlocal enabledelayedexpansion

:: Get directory (first argument, default to current if not provided)
set TARGET_DIR=%1
if "%TARGET_DIR%"=="" set TARGET_DIR=.

:: Get basic parameters from command line arguments
set STRENGTH=%2
if "%STRENGTH%"=="" set STRENGTH=1.0

set DISTANCE=%3
if "%DISTANCE%"=="" set DISTANCE=1

set INVERT=%4
if "%INVERT%"=="" set INVERT=0

set WRAP=%5
if "%WRAP%"=="" set WRAP=1

:: Get advanced parameters from command line arguments
set BLUR=%6
if "%BLUR%"=="" set BLUR=0.0

set KERNEL=%7
if "%KERNEL%"=="" set KERNEL=sobel

set KERNEL_SIZE=%8
if "%KERNEL_SIZE%"=="" set KERNEL_SIZE=3

set SPECULAR=%9
if "%SPECULAR%"=="" set SPECULAR=0.0

:: Get additional parameters (need to be shifted due to batch limitation)
shift
set INVERT_X=%9
if "%INVERT_X%"=="" set INVERT_X=0

shift
set INVERT_Y=%9
if "%INVERT_Y%"=="" set INVERT_Y=0

shift
set CHUNK_SIZE=%9
if "%CHUNK_SIZE%"=="" set CHUNK_SIZE=100

shift
set EDGE_ENHANCEMENT=%9
if "%EDGE_ENHANCEMENT%"=="" set EDGE_ENHANCEMENT=5.0

shift
set CONTRAST_ENHANCEMENT=%9
if "%CONTRAST_ENHANCEMENT%"=="" set CONTRAST_ENHANCEMENT=1.5

shift
set SHARPNESS=%9
if "%SHARPNESS%"=="" set SHARPNESS=1.0

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

echo Advanced Normal Map Generator Batch Script
echo =========================================
echo Processing images in: %TARGET_DIR%
echo.
echo Basic Parameters:
echo - Strength: %STRENGTH%
echo - Distance: %DISTANCE%
echo - Invert Height: %INVERT%
echo - Wrap Edges: %WRAP%
echo.
echo Advanced Parameters:
echo - Blur Radius: %BLUR%
echo - Kernel Type: %KERNEL%
echo - Kernel Size: %KERNEL_SIZE%
echo - Specular Intensity: %SPECULAR%
echo - Invert X Component: %INVERT_X%
echo - Invert Y Component: %INVERT_Y%
echo - Chunk Size: %CHUNK_SIZE%
echo - Edge Enhancement: %EDGE_ENHANCEMENT%
echo - Contrast Enhancement: %CONTRAST_ENHANCEMENT%
echo - Sharpness: %SHARPNESS%
echo.

:: Count total images for progress reporting (excluding any with "_n" in the filename)
set IMG_COUNT=0
for %%F in ("%TARGET_DIR%\*.png" "%TARGET_DIR%\*.jpg" "%TARGET_DIR%\*.jpeg" "%TARGET_DIR%\*.bmp" "%TARGET_DIR%\*.tif" "%TARGET_DIR%\*.tiff") do (
    set "FILENAME=%%~nF"
    echo !FILENAME! | findstr /C:"_n" >nul
    if !ERRORLEVEL! NEQ 0 (
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

:: Process each image, skipping those with "_n" anywhere in the filename
for %%F in ("%TARGET_DIR%\*.png" "%TARGET_DIR%\*.jpg" "%TARGET_DIR%\*.jpeg" "%TARGET_DIR%\*.bmp" "%TARGET_DIR%\*.tif" "%TARGET_DIR%\*.tiff") do (
    set "FILENAME=%%~nF"
    
    :: Check if "_n" is anywhere in the filename
    echo !FILENAME! | findstr /C:"_n" >nul
    if !ERRORLEVEL! NEQ 0 (
        set /a CURRENT+=1
        echo [!CURRENT!/%IMG_COUNT%] Processing: %%~nxF
        
        set CMD=python low_memory_normal_map.py "%%F" -s %STRENGTH% -d %DISTANCE% -b %BLUR% -k %KERNEL% -ks %KERNEL_SIZE% -sp %SPECULAR% -c %CHUNK_SIZE% -e %EDGE_ENHANCEMENT% -ce %CONTRAST_ENHANCEMENT% -sh %SHARPNESS%
        
        if "%INVERT%"=="1" set CMD=!CMD! -i
        if "%WRAP%"=="0" set CMD=!CMD! --no-wrap
        if "%INVERT_X%"=="1" set CMD=!CMD! -ix
        if "%INVERT_Y%"=="1" set CMD=!CMD! -iy
        
        !CMD!
        echo.
    ) else (
        echo Skipping normal map: %%~nxF
    )
)

echo All images processed successfully!
exit /b 0