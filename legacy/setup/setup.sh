'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

'''

# Check if Python is installed
if ! (python -V &> /dev/null || py -V &> /dev/null); then
    # Install the latest stable Python version
    while ! (python -V &> /dev/null || py -V &> /dev/null);
    do
        echo "Python is not installed or not accessible!"
        echo "Please install Python and make sure it is added to your system's PATH environment variable."
        echo "Hold Ctrl and click on the link below or search 'Python Download' in your browser."
        echo "https://www.python.org/downloads/"
        echo "After installing Python and adding it to PATH, close and reopen setup file."
        read -p ""
    done
else
    echo "Python is already installed."
fi


# # Install required Python packages
# (python -m pip install selenium || py -m pip install selenium)
# (python -m pip install undetected-chromedriver || py -m pip install undetected-chromedriver)
# # (python -m pip install beautifulsoup4 || py -m pip install beautifulsoup4)


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
        echo "After the installation is complete, press Enter to continue, if that does not work then close and reopen setup file.."
        read -p ""
    done
else
    echo "Google Chrome is already installed."
fi





# Step 1: Get the JSON data
latest_versions_info=$(curl -sS "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json")

echo $latest_versions_info

# Step 2: Get the download URL for win64 platform
download_url=$(echo "$latest_versions_info" | 
               grep -A 5 '"platform": "win64",' | 
               grep 'url":' | 
               awk -F'"' '{print $4}')

echo "Download URL: '$download_url'"

# Step 3: Download the file
curl -o chromedriver.zip "$download_url"

# Step 4: Set the destination directory
chrome_install_dir="/c/Program Files/Google/Chrome"
mkdir -p "$chrome_install_dir"

# Step 5: Unzip and move ChromeDriver
unzip -q chromedriver.zip -d "$chrome_install_dir"
mv "$chrome_install_dir/chromedriver_win64/chromedriver.exe" "$chrome_install_dir"
rm -r "$chrome_install_dir/chromedriver_win64" chromedriver.zip

# Step 6: Add ChromeDriver directory to PATH
echo "export PATH=\"\$PATH:${chrome_install_dir}\"" >> ~/.bashrc
source ~/.bashrc

echo "Setup complete. You can now use the web scraping tool."

# Step 7: Pause for user to read console messages
read -rsn1 -p "Press any key to continue..."








# # Get the latest ChromeDriver version
# LATEST_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)

# # Download ChromeDriver
# echo "Installing latest version of Google Chrome Driver (${LATEST_VERSION})"
# CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/${LATEST_VERSION}/chromedriver_win32.zip"
# CHROMEDRIVER_FILE="chromedriver.zip"
# CHROMEDRIVER_DIR="chromedriver"

# # Download ChromeDriver using certutil
# certutil -urlcache -split -f $CHROMEDRIVER_URL $CHROMEDRIVER_FILE

# # Extract ChromeDriver zip
# unzip $CHROMEDRIVER_FILE -d $CHROMEDRIVER_DIR
# rm $CHROMEDRIVER_FILE

# # Get the absolute path to the current directory
# CURRENT_DIR=$(pwd)

# # Set up environment variables
# echo "setx CHROME_DRIVER_PATH \"${CURRENT_DIR}\\${CHROMEDRIVER_DIR}\\chromedriver.exe\"" >> setup_env.bat
# echo "setx PATH \"%PATH%;${CURRENT_DIR}\\${CHROMEDRIVER_DIR}\"" >> setup_env.bat

# # Run the environment setup script
# cmd.exe /c setup_env.bat

# echo "Setup complete. You can now use the web scraping tool."

# # Remove the environment setup script
# rm setup_env.bat
# read -p "Press any key to continue!"# Get the latest ChromeDriver version
# LATEST_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)

# # Set the destination directory
# CHROME_INSTALL_DIR="C:\\Program Files\\Google\\Chrome"

# # Download ChromeDriver
# echo "Installing latest version of Google Chrome Driver (${LATEST_VERSION})"
# CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/${LATEST_VERSION}/chromedriver_win32.zip"
# CHROMEDRIVER_FILE="chromedriver.zip"
# CHROMEDRIVER_DIR="$CHROME_INSTALL_DIR"

# # Create the destination directory if it doesn't exist
# mkdir -p "$CHROME_INSTALL_DIR"

# # Download ChromeDriver using certutil
# certutil -urlcache -split -f $CHROMEDRIVER_URL $CHROMEDRIVER_FILE

# # Extract ChromeDriver zip to the installation directory
# unzip $CHROMEDRIVER_FILE -d $CHROME_INSTALL_DIR
# rm $CHROMEDRIVER_FILE

# echo "Setup complete. You can now use the web scraping tool."
