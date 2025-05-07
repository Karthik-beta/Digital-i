# Define URLs for Docker Desktop and pgAdmin 4 installers
$dockerUrl = "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe"
$pgadminUrl = "https://ftp.postgresql.org/pub/pgadmin/pgadmin4/v6.18/windows/pgadmin4-6.18-x64.exe"

# Define file paths for the installers
$dockerInstaller = "DockerDesktopInstaller.exe"
$pgadminInstaller = "pgadmin4-6.18-x64.exe"

# Function to download files
function Download-Installer {
    param (
        [string]$url,
        [string]$output
    )

    Write-Output "Downloading $output..."
    Invoke-WebRequest -Uri $url -OutFile $output
}

# Function to install software
function Install-Software {
    param (
        [string]$installer,
        [string]$arguments = ""
    )

    Write-Output "Installing $installer..."
    Start-Process -FilePath $installer -ArgumentList $arguments -Wait
}

# Download Docker Desktop
Download-Installer -url $dockerUrl -output $dockerInstaller

# Download pgAdmin 4
Download-Installer -url $pgadminUrl -output $pgadminInstaller

# Install Docker Desktop
Install-Software -installer $dockerInstaller -arguments "/quiet install"

# Install pgAdmin 4
Install-Software -installer $pgadminInstaller -arguments "/quiet"

# Verify installations
Write-Output "Verifying Docker Desktop installation..."
if (Get-Command "docker" -ErrorAction SilentlyContinue) {
    docker --version
} else {
    Write-Output "Docker Desktop is not installed."
}

Write-Output "Verifying pgAdmin 4 installation..."
if (Test-Path "C:\Program Files\pgAdmin 4\bin\pgAdmin4.exe") {
    Write-Output "pgAdmin 4 is installed."
} else {
    Write-Output "pgAdmin 4 is not installed."
}

Write-Output "Installation complete."