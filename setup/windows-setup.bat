:: Author:     Sai Vignesh Golla
:: LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

:: Copyright (C) 2024 Sai Vignesh Golla

:: License:    GNU Affero General Public License
::             https://www.gnu.org/licenses/agpl-3.0.en.html

:: GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn



@echo off
setlocal enabledelayedexpansion

:: Check for administrative privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

:: If error flag is set, we do not have admin privileges
if %errorlevel% neq 0 (
    echo Please run this setup as admin. & echo Requesting administrative privileges...
    powershell -Command "& {Start-Process -FilePath '%0' -ArgumentList '-Admin' -Verb RunAs}"
    goto End
)

echo Setting up ChromeDriver installation...

:: Use https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE to get version number directly Replace>>>>

:: Step 1: Get the latest version information 
powershell -Command "& { $response = Invoke-WebRequest -Uri 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'; if ($response.StatusCode -ne 200) { exit 1 }; $response.Content | Out-File 'latest_versions_info.json' }"
if %errorlevel% neq 0 ( 
    echo Please check your internet connection. See if any applications, firewalls, vpns, or devices are blocking the download.
    goto ExitSetup
)


:: Step 2: Extract the latest version directly from the JSON file
for /f "delims=" %%a in ('powershell -Command "& {(Get-Content 'latest_versions_info.json' | ConvertFrom-Json).channels.Stable.version} "') do (
    set "latest_version=%%~a"
)

:: <<<<<Replace

:: Check if latest_version is not null or empty
if not defined latest_version (
    echo FAILED to extract the latest version from the JSON file.
    goto ExitSetup
)

:: Construct the ChromeDriver URL
set "chrome_driver_url=https://storage.googleapis.com/chrome-for-testing-public/!latest_version!/win64/chromedriver-win64.zip"

echo Latest ChromeDriver version: !latest_version!.
echo Downloading ChromeDriver from URL: '!chrome_driver_url!' ...

:: Step 3: Download ChromeDriver
powershell -Command "& {Invoke-WebRequest -Uri !chrome_driver_url! -OutFile 'chromedriver.zip'}"

:: Step 4: Create installation directory and unzip
set "chrome_install_dir=C:\Program Files\Google\Chrome"
if not exist "%chrome_install_dir%" mkdir "%chrome_install_dir%"

:: Use PowerShell Expand-Archive for extraction (works with ZIP files)
powershell -Command "& {Expand-Archive -Path 'chromedriver.zip' -DestinationPath '%chrome_install_dir%' -Force}"
if %errorlevel% neq 0 ( 
    echo FAILED to extract ChromeDriver. Check if any application is denying installation or extraction.
    goto ExitSetup
)


:: Step 5: Add chromedriver.exe to PATH
set "chromedriver_dir=%chrome_install_dir%\chromedriver-win64"

@REM :: Update PATH for the current session
@REM set "path=%path%;%chromedriver_dir%"

@REM :: Update PATH in the registry for future sessions
@REM echo Adding ChromeDriver to path...
@REM @REM echo ";%PATH%;" | find /C /I ";%path%;
@REM @REM if errorlevel > 0 ( 
@REM @REM     echo Chromedriver path was already added
@REM @REM     goto CleanUp 
@REM @REM )

@REM reg add "HKCU\Environment" /v Path /t REG_EXPAND_SZ /d "%path%" /f
@REM if %errorlevel% neq 0 (
@REM     echo Failed to add chromedriver path to environment variables. Please add it manually.
@REM     goto ExitSetup
@REM )

:: Step 6: Clean up
:CleanUp
del chromedriver.zip
del latest_versions_info.json
echo Removed setup files.


:: Step 7: Open chromedriver
echo Opening Chrome Driver...
start "" "%chromedriver_dir%\chromedriver.exe"


:: Check if python and chrome are installed or not
:: pip install undetected-chromedriver
:: pip install setuptools
:: pip install pyautogui





:ExitSetup
pause
exit

:End
