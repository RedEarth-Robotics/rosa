@echo off
REM Script to install RedEarth-Robotics/rosa fork in editable mode (Windows)
REM This script clones the fork, creates a virtual environment, and installs ROSA

setlocal enabledelayedexpansion

REM Configuration
set REPO_URL=git@github.com:RedEarth-Robotics/rosa.git
set INSTALL_DIR=%USERPROFILE%\rosa-fork
set VENV_NAME=venv

echo 🤖 ROSA Fork Installation Script (Windows)
echo ==========================================
echo Repository: %REPO_URL%
echo Install directory: %INSTALL_DIR%
echo.

REM Check if git is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: git is not installed. Please install git first.
    pause
    exit /b 1
)

REM Check if python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: python is not installed. Please install Python 3.9+ first.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python version: %PYTHON_VERSION%

REM Create installation directory if it doesn't exist
if exist "%INSTALL_DIR%" (
    echo ⚠️  Installation directory already exists: %INSTALL_DIR%
    set /p REINSTALL="Do you want to remove it and reinstall? (y/N): "
    if /i "!REINSTALL!"=="y" (
        echo 🗑️  Removing existing directory...
        rmdir /s /q "%INSTALL_DIR%"
    ) else (
        echo ❌ Installation cancelled.
        pause
        exit /b 0
    )
)

REM Clone the repository
echo 📥 Cloning repository from %REPO_URL%...
git clone "%REPO_URL%" "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

REM Create virtual environment
echo 🐍 Creating virtual environment...
python -m venv %VENV_NAME%

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call %VENV_NAME%\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install ROSA in editable mode with all optional dependencies
echo 📦 Installing ROSA in editable mode with all LLM providers...
pip install -e ".[all]"

echo.
echo ✅ Installation completed successfully!
echo.
echo 📋 Next steps:
echo 1. Activate the virtual environment:
echo    %INSTALL_DIR%\%VENV_NAME%\Scripts\activate.bat
echo.
echo 2. Verify installation:
echo    python -c "import rosa; print(rosa.__version__)"
echo.
echo 3. To deactivate the virtual environment when done:
echo    deactivate
echo.
echo 🎉 Your ROSA fork is ready to use!

pause
