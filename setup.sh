#!/bin/bash

# Check if Python is installed
if ! command -v python &> /dev/null; then
    # Install the latest stable Python version
    echo "Python is not installed. Installing the latest stable version..."
    PYTHON_URL="https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe"
    PYTHON_FILE="python-installer.exe"
    
    wget -O $PYTHON_FILE $PYTHON_URL
    cmd.exe /c start $PYTHON_FILE
    
    echo "Please follow the Python installation wizard."
    echo "After the installation is complete, press Enter to continue."
    read -p ""
    
    rm $PYTHON_FILE
else
    echo "Python is already installed."
fi

# Check if Google Chrome is installed
if ! command -v google-chrome &> /dev/null; then
    # Download and install Google Chrome
    echo "Google Chrome is not installed. Installing Google Chrome..."
    CHROME_URL="https://dl.google.com/chrome/install/standalone/chrome_installer.exe"
    CHROME_FILE="chrome-installer.exe"
    
    wget -O $CHROME_FILE $CHROME_URL
    cmd.exe /c start $CHROME_FILE
    
    echo "Please follow the Google Chrome installation wizard."
    echo "After the installation is complete, press Enter to continue."
    read -p ""
    
    rm $CHROME_FILE
else
    echo "Google Chrome is already installed."
fi

# Install required Python packages
pip install selenium

# Get the latest ChromeDriver version
LATEST_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)

# Download ChromeDriver
CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/${LATEST_VERSION}/chromedriver_win32.zip"
CHROMEDRIVER_FILE="chromedriver.zip"
CHROMEDRIVER_DIR="chromedriver"

wget -O $CHROMEDRIVER_FILE $CHROMEDRIVER_URL
unzip $CHROMEDRIVER_FILE -d $CHROMEDRIVER_DIR
rm $CHROMEDRIVER_FILE

# Get the absolute path to the current directory
CURRENT_DIR=$(pwd)

# Set up environment variables
echo "export CHROME_DRIVER_PATH=${CURRENT_DIR}/${CHROMEDRIVER_DIR}/chromedriver.exe" >> ~/.bashrc
echo "export PATH=\$PATH:${CURRENT_DIR}/${CHROMEDRIVER_DIR}" >> ~/.bashrc

# Activate the environment variables in the current shell
source ~/.bashrc

echo "Setup complete. You can now use the web scraping tool."
