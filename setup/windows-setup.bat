@echo off
setlocal enabledelayedexpansion

echo Setting up ChromeDriver installation...

:: Step 1: Get the latest version information
powershell -Command "& {Invoke-WebRequest -Uri 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json' -OutFile 'latest_versions_info.json'}"

:: Step 2: Extract the latest version directly from the JSON file
for /f "delims=" %%a in ('powershell -Command "& {(Get-Content 'latest_versions_info.json' | ConvertFrom-Json).channels.Stable.version} "') do (
    set "latest_version=%%~a"
)

:: Check if latest_version is not null or empty
if not defined latest_version (
    echo Failed to extract the latest version from the JSON file.
    exit /b 1
)

:: Construct the ChromeDriver URL
set "chrome_driver_url=https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/!latest_version!/win64/chromedriver-win64.zip"

echo Latest ChromeDriver version: !latest_version!
echo ChromeDriver URL: !chrome_driver_url!

:: Step 3: Download ChromeDriver
powershell -Command "& {Invoke-WebRequest -Uri !chrome_driver_url! -OutFile 'chromedriver.zip'}"

:: Step 4: Create installation directory and unzip
set "chrome_install_dir=C:\Program Files\Google\Chrome"
mkdir "%chrome_install_dir%"

:: Use PowerShell Expand-Archive for extraction (works with ZIP files)
powershell -Command "& {Expand-Archive -Path 'chromedriver.zip' -DestinationPath '%chrome_install_dir%'}"

:: Step 5: Add chromedriver.exe to PATH
set "chromedriver_dir=%chrome_install_dir%\chromedriver-win64"
setx PATH "%PATH%;%chromedriver_dir%"

:: Step 6: Clean up
del chromedriver.zip
:: Add any other cleanup here

echo Setup complete. If it Failed, retry by running it as administrator and with proper internet connection.

pause
