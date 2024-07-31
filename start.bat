@echo off
setlocal

REM Get the directory of the current script
set SCRIPT_DIR=%~dp0

REM Set the path to the env python executable
set ENV_PYTHON=%SCRIPT_DIR%env\python.exe

REM Install requirements if needed
%ENV_PYTHON% -m pip install --upgrade pip
%ENV_PYTHON% -m pip install -r %SCRIPT_DIR%requirements.txt

REM Run the application
%ENV_PYTHON% %SCRIPT_DIR%app.py

endlocal