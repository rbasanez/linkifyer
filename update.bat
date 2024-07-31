@echo off
setlocal EnableDelayedExpansion

:: Define variables
set root_path=%~dp0
set owner=rbasanez
set repo=linkifyer
set version_file=%root_path%app.version

:: Function to get latest release
:get_latest_release
set url=https://api.github.com/repos/%owner%/%repo%/releases/latest
call :log.info "get latest version: %url%"
curl -s "%url%" > "%root_path%temp.json"

:: Check if temp.json exists
if not exist "%root_path%temp.json" (
    call :log.error "failed to retrieve latest release"
    goto :end
)

:: Extract tag_name from temp.json
for /f "tokens=2 delims=:" %%A in ('type "%root_path%temp.json" ^| find /i "tag_name"') do (
    set latest_version=%%~A
)

set latest_version=%latest_version:,=%
set latest_version=%latest_version:"=%
set latest_version=%latest_version:v=%
set latest_version=%latest_version: =%

if %latest_version% == "" (
    call :log.error "failed to retrieve latest release"
    goto :end
)

:: Get app.version
if exist "%version_file%" (
    set /p current_version=<"%version_file%"
) else (
    set current_version=NULL
)
set current_version=%current_version: =%

call :log.info "latest version: %latest_version%"
call :log.info "current version: %current_version%"

:: Compare latest version with current version
if "%latest_version%" == "%current_version%" (
    call :log.info "app is up to date..."
    goto :end
) else (
    call :log.info "updating app..."
)

:: Function to download and replace repository
set url_download=https://codeload.github.com/%owner%/%repo%/zip/refs/tags/%latest_version%
set zip_path=%root_path%%repo%-%latest_version%.zip
set extracted_folder=%root_path%%repo%-%latest_version%


:: Download the zip file using curl with follow redirect
call :log.info "download %url_download%"
call :log.info "target %zip_path%"
curl -L "%url_download%" -o "%zip_path%"

:: Check if the zip file is downloaded successfully
if not exist "%zip_path%" (
    call :log.error "failed to download the zip file..."
    goto :end
)

:: Extract the downloaded file
call :log.info "extracting zip file..."
set command=Add-Type -Assembly 'System.IO.Compression.Filesystem'; [System.IO.Compression.ZipFile]::ExtractToDirectory('!zip_path!','!root_path!')
powershell -Command "!command!"

:: Check if the extraction was successful
if errorlevel 1 (
    call :log.error "failed to extract the zip file. You may need to unzip the file manually."
    goto :end
) else (
    call :log.info "zip file extracted successfully..."
)

call :log.info "move files..."
IF %root_path:~-1%==\ SET target_path=%root_path:~0,-1%
robocopy "!extracted_folder!" "!target_path!" /E /MOVE /NFL /NDL

call :log.info "update current version..."
echo %latest_version%>"%version_file%"

rem Check if temp.json exists and delete it if it does
if exist "%root_path%temp.json" (
    del /q "%root_path%temp.json"
)

rem Check if the extracted folder exists and remove it if it does
if exist "%extracted_folder%" (
    rmdir /s /q "%extracted_folder%"
)

rem Check if the zip file exists and delete it if it does
if exist "%zip_path%" (
    del /q "%zip_path%"
)
goto :end

:end
pause
exit


:log.info
echo [INFO   ]   %~1
exit /b

:log.warning
echo [WARNING]   %~1
exit /b

:log.error
echo [ERROR  ]   %~1
exit /b