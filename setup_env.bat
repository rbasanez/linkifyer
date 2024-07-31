@echo off
setlocal

REM Get the directory of the current script
set SCRIPT_DIR=%~dp0

REM Create the environment if it doesn't exist
if not exist "%SCRIPT_DIR%env" (
    conda env create --prefix "%SCRIPT_DIR%env" --file "%SCRIPT_DIR%environment.yml"
)

endlocal