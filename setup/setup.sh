# Check if Python is installed
if ! python -V &> /dev/null; then
    # Install the latest stable Python version
    while ! python -V &> /dev/null;
    do
        echo "Python is not installed or not accessible!"
        echo "Please install Python and make sure it is added to your system's PATH environment variable."
        echo "Hold Ctrl and click on the link below or search 'Python Download' in your browser."
        echo "https://www.python.org/downloads/"
        echo "After installing Python and adding it to PATH, press Enter to continue."
        read -p ""
    done
else
    echo "Python is already installed."
fi

# Check if Google Chrome is installed
if ! command -v "C:\Program Files\Google\Chrome\Application\chrome.exe" &> /dev/null; then
    # Install Google Chrome
    while ! command -v "C:\Program Files\Google\Chrome\Application\chrome.exe" &> /dev/null;
    do
        echo "Google Chrome is not installed or not installed in the default location."
        echo "Please install Google Chrome to continue..."
        echo "Hold Ctrl and click on the link below or search 'google chrome download' in your browser."
        echo "https://www.google.com/chrome/"
        echo "Please follow the Google Chrome installation wizard."
        echo "After the installation is complete, press Enter to continue."
        read -p ""
    done
else
    echo "Google Chrome is already installed."
fi

# Install required Python packages
pip install selenium
pip install beautifulsoup4

# Get the latest ChromeDriver version
LATEST_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)

# Download ChromeDriver
CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/${LATEST_VERSION}/chromedriver_win32.zip"
CHROMEDRIVER_FILE="chromedriver.zip"
CHROMEDRIVER_DIR="chromedriver"

# Download ChromeDriver using certutil
certutil -urlcache -split -f $CHROMEDRIVER_URL $CHROMEDRIVER_FILE

# Extract ChromeDriver zip
unzip $CHROMEDRIVER_FILE -d $CHROMEDRIVER_DIR
rm $CHROMEDRIVER_FILE

# Get the absolute path to the current directory
CURRENT_DIR=$(pwd)

# Set up environment variables
echo "setx CHROME_DRIVER_PATH \"${CURRENT_DIR}\\${CHROMEDRIVER_DIR}\\chromedriver.exe\"" >> setup_env.bat
echo "setx PATH \"%PATH%;${CURRENT_DIR}\\${CHROMEDRIVER_DIR}\"" >> setup_env.bat

# Run the environment setup script
cmd.exe /c setup_env.bat

echo "Setup complete. You can now use the web scraping tool."

# Remove the environment setup script
rm setup_env.bat
