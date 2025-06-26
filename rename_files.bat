@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Please provide a directory path.
    goto :EOF
)

set "dir=%~1"
cd /d "%dir%"

echo Processing files in %dir%...

REM Process files with _n suffix
for %%F in (*_n) do (
    set "fullname=%%F"
    echo Found: !fullname!
    
    REM Get the filename without the _n suffix
    set "basename=!fullname:~0,-2!"
    
    REM Find the position of the last underscore
    set "last_underscore_pos=-1"
    set "temp_name=!basename!"
    :find_last_underscore_n
    for /f "delims=" %%i in ("!temp_name:*_=!") do (
        if not "%%i"=="!temp_name!" (
            set "temp_name=%%i"
            set /a "last_underscore_pos+=1+!temp_name:~0,1000000!"
            goto find_last_underscore_n
        )
    )
    
    if !last_underscore_pos! gtr 0 (
        REM Extract parts before and after the last underscore
        set "prefix=!basename:~0,!last_underscore_pos!!"
        set "suffix=!basename:~!last_underscore_pos!!"
        
        echo Renaming to: !prefix!_n!suffix!
        ren "!fullname!" "!prefix!_n!suffix!"
    ) else (
        echo No underscore found in !fullname!, skipping.
    )
    echo.
)

REM Process files with _s suffix
for %%F in (*_s) do (
    set "fullname=%%F"
    echo Found: !fullname!
    
    REM Get the filename without the _s suffix
    set "basename=!fullname:~0,-2!"
    
    REM Find the position of the last underscore
    set "last_underscore_pos=-1"
    set "temp_name=!basename!"
    :find_last_underscore_s
    for /f "delims=" %%i in ("!temp_name:*_=!") do (
        if not "%%i"=="!temp_name!" (
            set "temp_name=%%i"
            set /a "last_underscore_pos+=1+!temp_name:~0,1000000!"
            goto find_last_underscore_s
        )
    )
    
    if !last_underscore_pos! gtr 0 (
        REM Extract parts before and after the last underscore
        set "prefix=!basename:~0,!last_underscore_pos!!"
        set "suffix=!basename:~!last_underscore_pos!!"
        
        echo Renaming to: !prefix!_s!suffix!
        ren "!fullname!" "!prefix!_s!suffix!"
    ) else (
        echo No underscore found in !fullname!, skipping.
    )
    echo.
)

echo Done.
pause