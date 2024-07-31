@echo off

set PREFIX=/linkifyer
set PORT=6969

call conda activate py312
call python -m pip install --upgrade pip
call python -m pip install -r %~dp0requirements.txt

echo.
echo **********************************************************
echo.

call python %~dp0app.py --prefix %PREFIX% --port %PORT%
call conda deactivate

pause