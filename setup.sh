#!/bin/bash

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python not found. Installing Python..."
    # Download the latest Python installer for Windows (modify the URL based on your Python version)
    curl -O "https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe"
    # Run the Python installer silently
    python-3.11.4-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    # Clean up the installer
    rm python-3.11.4-amd64.exe
else
    echo "Python already installed."
fi

# Check if Chrome is installed
if ! command -v "C:\Program Files\Google\Chrome\Application\chrome.exe" &> /dev/null; then
    echo "Google Chrome not found. Installing Chrome..."
    # Download the latest Chrome installer for Windows (modify the URL based on your Chrome version)
    curl -O "https://dl.google.com/chrome/install/ChromeStandaloneSetup.exe"
    # Run the Chrome installer silently
    ChromeStandaloneSetup.exe --silent --install
    # Clean up the installer
    rm ChromeStandaloneSetup.exe
else
    echo "Google Chrome already installed."
fi

# Install required packages
pip install selenium

# Download ChromeDriver (replace the URL with the appropriate version for your system)
CHROME_DRIVER_URL="https://chromedriver.storage.googleapis.com/93.0.4577.15/chromedriver_win32.zip"
curl -O "$CHROME_DRIVER_URL"
unzip chromedriver_win32.zip
# Move the chromedriver executable to a directory included in the PATH environment variable
mv chromedriver.exe /usr/local/bin/
# Clean up the downloaded archive
rm chromedriver_win32.zip

# Provide instructions for the user
echo "Setup completed successfully!"
echo "You can now run your web scraping tool."
