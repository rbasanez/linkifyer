@echo off
net stop Linkifyer
robocopy %~dp0_internal c:\Linkifyer\_internal /E
robocopy %~dp0 c:\Linkifyer linkifyer.exe
robocopy %~dp0 c:\Linkifyer README.html
python c:\Linkifyer\_internal\update.py
net start Linkifyer
pause