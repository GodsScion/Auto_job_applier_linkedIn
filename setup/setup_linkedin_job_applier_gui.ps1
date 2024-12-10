# Save this script as setup_linkedin_job_applier_gui_v6.ps1

# Set Execution Policy for the Current Process
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force

# Load required assemblies for GUI
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Initialize phase statuses using an ordered hashtable
$phaseStatus = [ordered]@{
    "Network Check"        = $false
    "Install Git"          = $false
    "Install Python"       = $false
    "Install pip"          = $false
    "Install Chrome"       = $false
    "Clone Repository"     = $false
    "Install Requirements" = $false
    "Install ChromeDriver" = $false
    "Configure Files"      = $false
    "Run Main Script"      = $false
}

# Main function to start the setup process
function Start-Setup {
    Show-MainMenu
}

# Function to display the main menu with enhanced GUI
function Show-MainMenu {
    # Define colors following the 60/30/10 rule
    $primaryColor = [System.Drawing.Color]::FromArgb(255, 10, 102, 195)  # LinkedIn Blue (60%)
    $secondaryColor = [System.Drawing.Color]::FromArgb(255, 240, 240, 240)  # Light Gray (30%)
    $accentColor = [System.Drawing.Color]::FromArgb(255, 34, 139, 34)  # Forest Green (10%) for accents/completion
    $progressAccentColor = [System.Drawing.Color]::FromArgb(255, 255, 165, 0)  # Orange for progress bar to stand out

    # Create the form
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "LinkedIn AI Auto Job Applier Launcher"
    $form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
    $form.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    $form.MaximizeBox = $false
    $form.BackColor = $primaryColor
    $form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedSingle

    # Add the LinkedIn logo (aligned further left)
    $logoUrl = "https://blog.waalaxy.com/wp-content/uploads/2021/01/3-1.png"
    $scriptDir = $PSScriptRoot
    $logoPath = Join-Path $scriptDir "linkedin_logo.png"
    if (-not (Test-Path $logoPath)) {
        try {
            Invoke-WebRequest -Uri $logoUrl -OutFile $logoPath -ErrorAction Stop
        } catch {
            Write-Host "Failed to download LinkedIn logo: $_"
        }
    }

    if (Test-Path $logoPath) {
        try {
            $logo = [System.Drawing.Image]::FromFile($logoPath)
            $pictureBox = New-Object System.Windows.Forms.PictureBox
            $pictureBox.Image = $logo
            $pictureBox.SizeMode = [System.Windows.Forms.PictureBoxSizeMode]::Zoom  # Prevent stretching and keep aspect ratio
            $pictureBox.BackColor = $primaryColor  # Set background color to blend with the form
            $pictureBox.Location = New-Object System.Drawing.Point(10, 5)  # Moved further left
            $pictureBox.Size = New-Object System.Drawing.Size(360, 150)  # Same enlarged size
            $form.Controls.Add($pictureBox)
        } catch {
            Write-Host "Failed to load LinkedIn logo: $_"
        }
    }

    # Create ToolTip object
    $toolTip = New-Object System.Windows.Forms.ToolTip

    # "Run All" Button (top right aligned with the logo, padding adjusted)
    $runAllButton = New-Object System.Windows.Forms.Button
    $runAllButton.Location = New-Object System.Drawing.Point(450, 80)  # Positioned slightly down
    $runAllButton.Size = New-Object System.Drawing.Size(100, 40)
    $runAllButton.Text = "Run All"
    $runAllButton.BackColor = [System.Drawing.Color]::White
    $runAllButton.ForeColor = [System.Drawing.Color]::Black
    $runAllButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
    $runAllButton.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $runAllButton.Add_Click({
        Run-AllPhases -keys $keys -phaseButtons $phaseButtons -phaseLabels $phaseLabels -progressBar $progressBar -statusLog $statusLog
    })
    $form.Controls.Add($runAllButton)

    # Use dynamic calculation for positions
    $phaseCount = $phaseStatus.Count
    $controlHeight = 30
    $verticalSpacing = 10
    $initialYPos = if ($pictureBox) { $pictureBox.Location.Y + $pictureBox.Height + 10 } else { 150 }
    $currentYPos = $initialYPos

    # Create labels and buttons for each phase
    $phaseLabels = @{ }
    $phaseButtons = @{ }
    $phaseIndex = 0

    # Use the ordered keys
    $keys = @($phaseStatus.Keys)

    foreach ($phase in $keys) {
        # Phase Panel to hold label and button
        $phasePanel = New-Object System.Windows.Forms.Panel
        $phasePanel.Location = New-Object System.Drawing.Point(20, $currentYPos)
        $phasePanel.Size = New-Object System.Drawing.Size(540, $controlHeight)
        $phasePanel.BackColor = $secondaryColor

        # Phase Label
        $label = New-Object System.Windows.Forms.Label
        $label.Location = New-Object System.Drawing.Point(10, 5)
        $label.Size = New-Object System.Drawing.Size(400, ($controlHeight - 10))
        $label.Text = "$($phaseIndex + 1). $phase - Pending"  # Phase numbers included
        $label.Font = New-Object System.Drawing.Font("Segoe UI", 10)
        $label.ForeColor = [System.Drawing.Color]::Black
        $phasePanel.Controls.Add($label)
        $phaseLabels[$phase] = $label

        # Set tooltips with descriptions for each phase
        switch ($phase) {
            "Network Check" { $toolTip.SetToolTip($label, "Checks internet connectivity to ensure all subsequent downloads and installations can proceed.") }
            "Install Git" { $toolTip.SetToolTip($label, "Installs Git, a version control tool, to enable repository cloning and version management.") }
            "Install Python" { $toolTip.SetToolTip($label, "Installs Python, a necessary programming language for running the automation scripts.") }
            "Install pip" { $toolTip.SetToolTip($label, "Installs pip, the package installer for Python, used to install required Python packages.") }
            "Install Chrome" { $toolTip.SetToolTip($label, "Installs Google Chrome, which is required for web automation tasks.") }
            "Clone Repository" { $toolTip.SetToolTip($label, "Clones the Git repository containing the job application automation scripts.") }
            "Install Requirements" { $toolTip.SetToolTip($label, "Installs all necessary Python libraries listed in the requirements file for the scripts.") }
            "Install ChromeDriver" { $toolTip.SetToolTip($label, "Installs ChromeDriver, which is used to control Chrome for automated web interactions.") }
            "Configure Files" { $toolTip.SetToolTip($label, "Opens configuration files for customization, such as personal information and application preferences.") }
            "Run Main Script" { $toolTip.SetToolTip($label, "Runs the main automation script to start the job application process on LinkedIn.") }
        }

        # Phase Button
        $button = New-Object System.Windows.Forms.Button
        $button.Location = New-Object System.Drawing.Point(450, 2)
        $button.Size = New-Object System.Drawing.Size(70, ($controlHeight - 4))
        $button.Text = "Run"
        $button.Tag = $phase
        $button.Enabled = ($phaseIndex -eq 0)  # Enable only the first phase button initially
        $button.BackColor = [System.Drawing.Color]::White
        $button.ForeColor = [System.Drawing.Color]::Black
        $button.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
        $button.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
        $button.Add_Click({
            Run-Phase -phase $this.Tag -keys $keys -phaseButtons $phaseButtons -phaseLabels $phaseLabels -progressBar $progressBar -statusLog $statusLog
        })
        $phasePanel.Controls.Add($button)
        $phaseButtons[$phase] = $button

        # Set tooltips for each button
        switch ($phase) {
            "Network Check" { $toolTip.SetToolTip($button, "Initiate network connectivity check to proceed.") }
            "Install Git" { $toolTip.SetToolTip($button, "Start Git installation to enable repository management.") }
            "Install Python" { $toolTip.SetToolTip($button, "Begin Python installation, required for running scripts.") }
            "Install pip" { $toolTip.SetToolTip($button, "Install pip, used for managing Python package installations.") }
            "Install Chrome" { $toolTip.SetToolTip($button, "Install Google Chrome for web automation tasks.") }
            "Clone Repository" { $toolTip.SetToolTip($button, "Clone the automation script repository from GitHub.") }
            "Install Requirements" { $toolTip.SetToolTip($button, "Install necessary Python packages from the requirements file.") }
            "Install ChromeDriver" { $toolTip.SetToolTip($button, "Install ChromeDriver to control Google Chrome for automation.") }
            "Configure Files" { $toolTip.SetToolTip($button, "Open configuration files to customize details for automation.") }
            "Run Main Script" { $toolTip.SetToolTip($button, "Run the main job application automation script.") }
        }

        $form.Controls.Add($phasePanel)
        $currentYPos += $controlHeight + $verticalSpacing
        $phaseIndex++
    }

    # Adjust the size of the form based on the number of phases
    $formHeight = $currentYPos + 200  # Additional space for progress bar and status log
    $form.Size = New-Object System.Drawing.Size(600, $formHeight)

    # Progress Bar (moved closer to the completion steps)
    $progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Location = New-Object System.Drawing.Point(20, ($currentYPos + 10))  # Positioned closer to the completion steps
    $progressBar.Size = New-Object System.Drawing.Size(540, 30)  # Consistent size for better alignment
    $progressBar.Minimum = 0
    $progressBar.Maximum = $phaseStatus.Count
    $progressBar.Value = 0
    $progressBar.ForeColor = $progressAccentColor  # Set progress bar color to stand out
    $form.Controls.Add($progressBar)

    # Status Log
    $statusLogHeight = 200
    $statusLog = New-Object System.Windows.Forms.TextBox
    $statusLog.Location = New-Object System.Drawing.Point(20, ($currentYPos + 50))  # Below the progress bar
    $statusLog.Size = New-Object System.Drawing.Size(540, $statusLogHeight)
    $statusLog.Multiline = $true
    $statusLog.ScrollBars = [System.Windows.Forms.ScrollBars]::Vertical
    $statusLog.ReadOnly = $true
    $statusLog.BackColor = $secondaryColor
    $statusLog.ForeColor = [System.Drawing.Color]::Black
    $form.Controls.Add($statusLog)

    # Update form height if necessary
    $formHeight = $statusLog.Location.Y + $statusLogHeight + 50
    $form.Size = New-Object System.Drawing.Size(600, $formHeight)

    # Initial button state update
    Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar

    # Show the form
    $form.Add_Shown({ $form.Activate() })
    [void]$form.ShowDialog()
}

# Function to update phase statuses
function Update-PhaseStatus {
    param($phase, $status)
    $script:phaseStatus[$phase] = $status
}

# Function to update phase labels
function Update-PhaseLabel {
    param($phase, $phaseLabels)
    $label = $phaseLabels[$phase]
    if ($phaseStatus[$phase]) {
        $label.Text = "$phase - Completed"
        $label.ForeColor = $accentColor  # Use forest green to indicate completion
    } else {
        $label.Text = "$phase - Failed"
        $label.ForeColor = [System.Drawing.Color]::Red  # Red is acceptable as an accent for errors
    }
}

# Function to update button states
function Update-ButtonStates {
    param($keys, $phaseButtons, $progressBar)
    for ($i = 0; $i -lt $keys.Count; $i++) {
        $currentPhase = $keys[$i]
        $button = $phaseButtons[$currentPhase]
        if ($phaseStatus[$currentPhase]) {
            $button.Enabled = $false
            $button.BackColor = [System.Drawing.Color]::LightGray  # Grey out completed buttons
        } elseif ($i -eq 0) {
            # First phase button is enabled if not completed
            $button.Enabled = -not $phaseStatus[$currentPhase]
        } else {
            $previousPhase = $keys[$i - 1]
            $button.Enabled = $phaseStatus[$previousPhase] -and (-not $phaseStatus[$currentPhase])
        }
    }
    # Update progress bar
    $completedPhases = ($phaseStatus.Values | Where-Object { $_ -eq $true }).Count
    $progressBar.Value = $completedPhases
}

# Function to log messages to the status log
function Log-Message {
    param($message, $statusLog)
    $statusLog.AppendText("$message`r`n")
    $statusLog.SelectionStart = $statusLog.Text.Length
    $statusLog.ScrollToCaret()
}

# Function to check if previous phase is completed
function Check-PreviousPhase {
    param($currentPhase, $requiredPhase, $statusLog)
    if ($phaseStatus[$requiredPhase]) {
        return $true
    } else {
        Log-Message -message "Please complete the '$requiredPhase' phase before proceeding to '$currentPhase'." -statusLog $statusLog
        return $false
    }
}

# Override Show-Error to display messages in the status log
function Show-Error {
    param($message, $statusLog)
    Log-Message -message "Error: $message" -statusLog $statusLog
}

# Function to test network connectivity
function Test-NetworkConnection {
    param($statusLog)
    try {
        Invoke-WebRequest -Uri "https://www.google.com" -UseBasicParsing -TimeoutSec 10 | Out-Null
        return $true
    } catch {
        Show-Error -message "Network connectivity test failed. Please check your internet connection." -statusLog $statusLog
        return $false
    }
}

# Function to install Git
function Install-Git {
    param($statusLog)
    try {
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            $gitInstaller = "GitInstaller.exe"
            $downloadUrl = "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.1/Git-2.42.0-64-bit.exe"
            Invoke-WebRequest -Uri $downloadUrl -OutFile $gitInstaller -ErrorAction Stop
            Start-Process -FilePath ".\$gitInstaller" -ArgumentList "/VERYSILENT" -Wait -ErrorAction Stop
            Remove-Item $gitInstaller
            # Refresh environment variables
            [Environment]::SetEnvironmentVariable("Path", $Env:Path + ";C:\Program Files\Git\cmd", [EnvironmentVariableTarget]::Machine)
            $Env:Path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
            if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
                Show-Error -message "Git installation failed or Git is not in PATH." -statusLog $statusLog
                return $false
            }
        }
        return $true
    } catch {
        Show-Error -message "An error occurred during Git installation: $_" -statusLog $statusLog
        return $false
    }
}

# Function to install Python
function Install-Python {
    param($statusLog)
    try {
        if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
            Start-Process "ms-windows-store://pdp/?productid=9NRWMJP3717K"
            [System.Windows.Forms.MessageBox]::Show("Please install Python 3 from the Microsoft Store, then click OK to continue.", "Install Python", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
            # Refresh environment variables
            [Environment]::SetEnvironmentVariable("Path", $Env:Path + ";$env:LOCALAPPDATA\Microsoft\WindowsApps", [EnvironmentVariableTarget]::Machine)
            $Env:Path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
            if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
                Show-Error -message "Python installation not detected. Please ensure Python 3 is installed and added to PATH." -statusLog $statusLog
                return $false
            }
        }
        return $true
    } catch {
        Show-Error -message "An error occurred during Python installation: $_" -statusLog $statusLog
        return $false
    }
}

# Function to install pip
function Install-Pip {
    param($statusLog)
    try {
        if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
            $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
            Invoke-WebRequest -Uri $getPipUrl -OutFile get-pip.py -ErrorAction Stop
            & python get-pip.py
            Remove-Item get-pip.py
            if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
                Show-Error -message "pip installation failed." -statusLog $statusLog
                return $false
            }
        }
        return $true
    } catch {
        Show-Error -message "An error occurred during pip installation: $_" -statusLog $statusLog
        return $false
    }
}

# Function to install Google Chrome
function Install-Chrome {
    param($statusLog)
    try {
        $chromePaths = @(
            "C:\Program Files\Google\Chrome\Application\chrome.exe",
            "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        )
        $chromeInstalled = $false
        foreach ($path in $chromePaths) {
            if (Test-Path $path) {
                $chromeInstalled = $true
                break
            }
        }
        if (-not $chromeInstalled) {
            $chromeInstaller = "ChromeSetup.exe"
            $downloadUrl = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
            Invoke-WebRequest -Uri $downloadUrl -OutFile $chromeInstaller -ErrorAction Stop
            Start-Process -FilePath ".\$chromeInstaller" -ArgumentList "/silent", "/install" -Wait -ErrorAction Stop
            Remove-Item $chromeInstaller
            # Check installation
            foreach ($path in $chromePaths) {
                if (Test-Path $path) {
                    $chromeInstalled = $true
                    break
                }
            }
            if (-not $chromeInstalled) {
                Show-Error -message "Google Chrome installation failed." -statusLog $statusLog
                return $false
            }
        }
        return $true
    } catch {
        Show-Error -message "An error occurred during Google Chrome installation: $_" -statusLog $statusLog
        return $false
    }
}

# Function to clone the repository
function Clone-Repository {
    param($statusLog)
    try {
        if (-not (Test-Path "Auto_job_applier_linkedIn")) {
            & git clone "https://github.com/GodsScion/Auto_job_applier_linkedIn.git"
            if (-not (Test-Path "Auto_job_applier_linkedIn")) {
                Show-Error -message "Repository cloning failed." -statusLog $statusLog
                return $false
            }
        }
        return $true
    } catch {
        Show-Error -message "An error occurred during repository cloning: $_" -statusLog $statusLog
        return $false
    }
}

# Function to install requirements
function Install-Requirements {
    param($statusLog)
    try {
        & python -m pip install -r "Auto_job_applier_linkedIn\requirements.txt"
        return $true
    } catch {
        Show-Error -message "An error occurred during package installation: $_" -statusLog $statusLog
        return $false
    }
}

# Function to install ChromeDriver
function Install-ChromeDriver {
    param($statusLog)
    try {
        # Step 1: Get the latest stable Chrome version information
        $versionsInfoUrl = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'
        $versionsInfoResponse = Invoke-WebRequest -Uri $versionsInfoUrl -UseBasicParsing -ErrorAction Stop
        $versionsInfo = $versionsInfoResponse.Content | ConvertFrom-Json

        if (-not $versionsInfo) {
            Show-Error -message "Failed to retrieve latest Chrome versions information." -statusLog $statusLog
            return $false
        }

        # Step 2: Extract the latest stable version number
        $latestVersion = $versionsInfo.channels.Stable.version
        if (-not $latestVersion) {
            Show-Error -message "Failed to extract the latest stable Chrome version." -statusLog $statusLog
            return $false
        }

        Log-Message -message "Latest ChromeDriver version: $latestVersion" -statusLog $statusLog

        # Step 3: Construct the ChromeDriver download URL
        $chromeDriverUrl = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$latestVersion/win64/chromedriver-win64.zip"
        Log-Message -message "Downloading ChromeDriver from URL: $chromeDriverUrl" -statusLog $statusLog

        # Step 4: Download ChromeDriver
        Invoke-WebRequest -Uri $chromeDriverUrl -OutFile 'chromedriver.zip' -ErrorAction Stop

        # Step 5: Extract ChromeDriver
        $chromeInstallDir = "C:\Program Files\Google\Chrome"
        if (-not (Test-Path $chromeInstallDir)) {
            New-Item -Path $chromeInstallDir -ItemType Directory | Out-Null
        }

        Expand-Archive -Path 'chromedriver.zip' -DestinationPath $chromeInstallDir -Force
        Remove-Item 'chromedriver.zip'

        # Step 6: Move chromedriver.exe to the application directory
        $chromedriverDir = Join-Path $chromeInstallDir 'chromedriver-win64'
        $chromedriverExe = Join-Path $chromedriverDir 'chromedriver.exe'
        if (-not (Test-Path $chromedriverExe)) {
            Show-Error -message "ChromeDriver executable not found after extraction." -statusLog $statusLog
            return $false
        }

        $destinationPath = $chromeInstallDir
        Move-Item -Path $chromedriverExe -Destination $destinationPath -Force

        # Remove the now empty chromedriver-win64 directory
        Remove-Item -Path $chromedriverDir -Recurse -Force

        Log-Message -message "ChromeDriver installed successfully at $destinationPath" -statusLog $statusLog

        return $true
    } catch {
        Show-Error -message "An error occurred during ChromeDriver installation: $_" -statusLog $statusLog
        return $false
    }
}

# Function to configure files
function Configure-Files {
    param($statusLog)
    try {
        $configDir = "Auto_job_applier_linkedIn\config"
        $configFiles = @("personals.py", "questions.py", "search.py", "secrets.py", "settings.py")
        foreach ($file in $configFiles) {
            $filePath = Join-Path $configDir $file
            if (-not (Test-Path $filePath)) {
                Show-Error -message "Configuration file not found: $filePath" -statusLog $statusLog
                return $false
            }
            [System.Windows.Forms.MessageBox]::Show("Please configure the file`n$filePath.`nClick OK to open it for editing.", "Configure Files", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
            Invoke-Item $filePath
            $result = [System.Windows.Forms.MessageBox]::Show("Did you complete editing $file?", "Configure Files", [System.Windows.Forms.MessageBoxButtons]::YesNo, [System.Windows.Forms.MessageBoxIcon]::Question)
            if ($result -ne [System.Windows.Forms.DialogResult]::Yes) {
                return $false
            }
        }
        return $true
    } catch {
        Show-Error -message "An error occurred during configuration: $_" -statusLog $statusLog
        return $false
    }
}

# Function to run the main script
function Run-MainScript {
    param($statusLog)
    try {
        $scriptPath = "Auto_job_applier_linkedIn\runAiBot.py"
        if (-not (Test-Path $scriptPath)) {
            Show-Error -message "Main script not found: $scriptPath" -statusLog $statusLog
            return $false
        }
        $result = [System.Windows.Forms.MessageBox]::Show("Do you want to run the main script now?", "Run Main Script", [System.Windows.Forms.MessageBoxButtons]::YesNo, [System.Windows.Forms.MessageBoxIcon]::Question)
        if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
            Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "python $scriptPath" -WindowStyle Normal
            return $true
        } else {
            [System.Windows.Forms.MessageBox]::Show("You can run the script later by executing`npython $scriptPath", "Run Main Script", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
            return $true
        }
    } catch {
        Show-Error -message "An error occurred while running the main script: $_" -statusLog $statusLog
        return $false
    }
}

# Function to run all phases sequentially
function Run-AllPhases {
    param($keys, $phaseButtons, $phaseLabels, $progressBar, $statusLog)
    foreach ($phase in $keys) {
        if (-not $phaseStatus[$phase]) {
            Run-Phase -phase $phase -keys $keys -phaseButtons $phaseButtons -phaseLabels $phaseLabels -progressBar $progressBar -statusLog $statusLog
            Start-Sleep -Milliseconds 500  # Small delay for better UX
            if (-not $phaseStatus[$phase]) {
                Log-Message -message "Phase '$phase' failed. Stopping execution." -statusLog $statusLog
                break
            }
        }
    }
}

# Function to run a specific phase
function Run-Phase {
    param($phase, $keys, $phaseButtons, $phaseLabels, $progressBar, $statusLog)
    Log-Message -message "Starting phase $phase" -statusLog $statusLog
    switch ($phase) {
        "Network Check" {
            if (-not $phaseStatus["Network Check"]) {
                if (Test-NetworkConnection -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Network Check" -status $true
                    Log-Message -message "Network Check completed successfully." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Network Check" -status $false
                    Log-Message -message "Network Check failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Network Check" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        "Install Git" {
            if (Check-PreviousPhase -currentPhase $phase -requiredPhase "Network Check" -statusLog $statusLog) {
                if (Install-Git -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Install Git" -status $true
                    Log-Message -message "Git installed successfully." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Install Git" -status $false
                    Log-Message -message "Git installation failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Install Git" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        "Install Python" {
            if (Check-PreviousPhase -currentPhase $phase -requiredPhase "Install Git" -statusLog $statusLog) {
                if (Install-Python -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Install Python" -status $true
                    Log-Message -message "Python installed successfully." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Install Python" -status $false
                    Log-Message -message "Python installation failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Install Python" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        "Install pip" {
            if (Check-PreviousPhase -currentPhase $phase -requiredPhase "Install Python" -statusLog $statusLog) {
                if (Install-Pip -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Install pip" -status $true
                    Log-Message -message "pip installed successfully." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Install pip" -status $false
                    Log-Message -message "pip installation failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Install pip" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        "Install Chrome" {
            if (Check-PreviousPhase -currentPhase $phase -requiredPhase "Install pip" -statusLog $statusLog) {
                if (Install-Chrome -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Install Chrome" -status $true
                    Log-Message -message "Google Chrome installed successfully." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Install Chrome" -status $false
                    Log-Message -message "Google Chrome installation failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Install Chrome" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        "Clone Repository" {
            if (Check-PreviousPhase -currentPhase $phase -requiredPhase "Install Chrome" -statusLog $statusLog) {
                if (Clone-Repository -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Clone Repository" -status $true
                    Log-Message -message "Repository cloned successfully." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Clone Repository" -status $false
                    Log-Message -message "Repository cloning failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Clone Repository" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        "Install Requirements" {
            if (Check-PreviousPhase -currentPhase $phase -requiredPhase "Clone Repository" -statusLog $statusLog) {
                if (Install-Requirements -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Install Requirements" -status $true
                    Log-Message -message "Requirements installed successfully." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Install Requirements" -status $false
                    Log-Message -message "Requirements installation failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Install Requirements" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        "Install ChromeDriver" {
            if (Check-PreviousPhase -currentPhase $phase -requiredPhase "Install Requirements" -statusLog $statusLog) {
                if (Install-ChromeDriver -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Install ChromeDriver" -status $true
                    Log-Message -message "ChromeDriver installed successfully." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Install ChromeDriver" -status $false
                    Log-Message -message "ChromeDriver installation failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Install ChromeDriver" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        "Configure Files" {
            if (Check-PreviousPhase -currentPhase $phase -requiredPhase "Install ChromeDriver" -statusLog $statusLog) {
                if (Configure-Files -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Configure Files" -status $true
                    Log-Message -message "Files configured successfully." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Configure Files" -status $false
                    Log-Message -message "Files configuration failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Configure Files" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        "Run Main Script" {
            if (Check-PreviousPhase -currentPhase $phase -requiredPhase "Configure Files" -statusLog $statusLog) {
                if (Run-MainScript -statusLog $statusLog) {
                    Update-PhaseStatus -phase "Run Main Script" -status $true
                    Log-Message -message "Main script executed." -statusLog $statusLog
                } else {
                    Update-PhaseStatus -phase "Run Main Script" -status $false
                    Log-Message -message "Main script execution failed." -statusLog $statusLog
                }
                Update-PhaseLabel -phase "Run Main Script" -phaseLabels $phaseLabels
                Update-ButtonStates -keys $keys -phaseButtons $phaseButtons -progressBar $progressBar
            }
        }
        default {
            Show-Error -message "Invalid phase selected." -statusLog $statusLog
        }
    }
}

# Start the setup process
Start-Setup
