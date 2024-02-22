'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

'''

# Check if Python is installed
while (-not (python -V)) {
    Write-Host "Python is not installed or not accessible!"
    Write-Host "Please install Python and make sure it is added to your system's PATH environment variable."
    Write-Host "Hold Ctrl and click on the link below or search 'Python Download' in your browser."
    Write-Host "https://www.python.org/downloads/"
    Write-Host "After installing Python and adding it to PATH, press Enter to continue."
    Read-Host -Prompt ""
}

Write-Host "Python is installed."



# Check if Google Chrome is installed
while (-not (Test-Path -Path "C:\Program Files\Google\Chrome\Application\chrome.exe")) {
    # Prompt user to install Google Chrome
    Write-Host "Google Chrome is not installed or not installed in the default location."
    Write-Host "Please make sure to install it before proceeding."
    Write-Host "Please install Google Chrome to continue..."
    Write-Host "Hold Ctrl and click on the link below or manually open a browser and search 'Google Chrome Download'."
    Write-Host "https://www.google.com/chrome/"
    Write-Host "After the installation is complete, press Enter to continue."
    Read-Host -Prompt ""
}

Write-Host "Google Chrome is installed."

# Install required Python packages
pip install selenium
pip install undetected-chromedriver

# Get the latest ChromeDriver version
$latestVersionUrl = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
$latestVersion = Invoke-WebRequest -Uri $latestVersionUrl -UseBasicParsing | Select-Object -ExpandProperty Content

# Download ChromeDriver
$chromeDriverUrl = "https://chromedriver.storage.googleapis.com/$latestVersion/chromedriver_win32.zip"
$chromeDriverZip = "chromedriver.zip"
$chromeDriverDir = "chromedriver"
Invoke-WebRequest -Uri $chromeDriverUrl -OutFile $chromeDriverZip
Expand-Archive -Path $chromeDriverZip -DestinationPath $chromeDriverDir
Remove-Item -Path $chromeDriverZip

# Set up environment variables
$env:CHROME_DRIVER_PATH = "$($PWD.Path)\$chromeDriverDir\chromedriver.exe"
$env:PATH += ";$($PWD.Path)\$chromeDriverDir"

Write-Host "Setup complete. You can now use the web scraping tool."
Read-Host -Prompt "Press any button to continue..."

