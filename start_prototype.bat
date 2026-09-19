@echo off
title BloodChain AI - Prototype Runner
echo ========================================================
echo  BloodChain AI - Hackwell 2.0 Working Model Prototype
echo  Team Outliers (#H2O080) - Saranathan College of Engg
echo ========================================================
echo.
echo [1] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python was not found in PATH.
    echo [*] Opening the standalone interactive prototype directly in your browser...
    start "" "%~dp0prototype.html"
    pause
    exit /b
)

echo [2] Installing requirements (Flask, etc.)...
pip install -r "%~dp0requirements.txt" >nul 2>&1

echo [3] Initializing database & seed data...
python "%~dp0database.py"

echo.
echo ========================================================
echo  Starting Flask Server at http://127.0.0.1:5000
echo  Press Ctrl+C to stop the server
echo ========================================================
echo.
start "" "http://127.0.0.1:5000"
python "%~dp0app.py"
pause
