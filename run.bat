@echo off
echo ==========================================
echo   Newton-Raphson App Launcher
echo ==========================================

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed! Please install Python from python.org.
    pause
    exit /b
)

:: 2. Check if the Virtual Environment exists. If not, create it.
:: Note: We use "venv" (no dot) for the folder name here.
if not exist "venv" (
    echo First time setup: Creating virtual environment...
    python -m venv venv

    echo Activating environment...
    call venv\Scripts\activate

    echo Installing dependencies - please wait...
    pip install -r requirements.txt
) else (
    echo Environment found. Activating...
    call venv\Scripts\activate
)

:: 3. Run the App
echo Starting the application...
python main.py

:: 4. Keep window open if it crashes
if %errorlevel% neq 0 pause