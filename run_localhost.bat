@echo off
setlocal enabledelayedexpansion
title BloodChain AI - Localhost Server (Mobile & Desktop)
color 0B

echo ====================================================================
echo       BLOODCHAIN AI - PREDICTIVE BLOOD SUPPLY MANAGEMENT
echo          Hackwell 2.0 - Team Outliers (#H2O080)
echo ====================================================================
echo.

:: Get the directory of this script
cd /d "%~dp0"

:: 1. Detect Local Network IP for Mobile Connection
echo [*] Detecting Local Wi-Fi / LAN IP for Mobile connection...
set "LOCAL_IP=localhost"
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address" /c:"IP Address"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set "LOCAL_IP=%%b"
        goto :ip_found
    )
)
:ip_found
echo.
echo ====================================================================
echo   ACCESS URLS:
echo   ------------------------------------------------------------------
echo   [Desktop View]:  http://localhost:5000
echo   [Mobile View]:   http://%LOCAL_IP%:5000 (Open on your Phone's Wi-Fi!)
echo ====================================================================
echo.

:: 2. Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python is not detected in your system PATH.
    echo [*] Launching the standalone interactive prototype directly in Chrome/Edge...
    echo.
    start "" "%~dp0prototype.html"
    pause
    exit /b
)

:: 3. Check & Install Flask dependencies if needed
echo [*] Checking required packages...
pip show flask >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Installing Flask and dependencies...
    pip install flask pandas scikit-learn numpy >nul 2>&1
)

:: 4. Ensure database is initialized
if not exist "bloodchain.db" (
    echo [*] Initializing database with demo records...
    python database.py >nul 2>&1
)

:: 5. Launch Browser Windows
echo [*] Launching Desktop and Mobile Preview windows...

:: Launch Desktop View
start http://localhost:5000

:: If Chrome or Edge exists, also open an instant dedicated Mobile-sized window!
set "BROWSER_FOUND=0"
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --app=http://localhost:5000 --window-size=412,870 --window-position=950,50
    set "BROWSER_FOUND=1"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" --app=http://localhost:5000 --window-size=412,870 --window-position=950,50
    set "BROWSER_FOUND=1"
) else if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --app=http://localhost:5000 --window-size=412,870 --window-position=950,50
    set "BROWSER_FOUND=1"
)

echo.
echo ====================================================================
echo  Flask Server is now running on port 5000!
echo  Press Ctrl + C in this terminal window to stop the server.
echo ====================================================================
echo.

python app.py

pause
