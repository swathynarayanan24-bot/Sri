@echo off
title BloodChain AI - Instant Prototype Opener
echo Opening BloodChain AI Prototype in Desktop and Mobile views...

:: Open Desktop View in Default Browser
start "" "%~dp0prototype.html"

:: If Chrome or Edge is installed, also open a dedicated Mobile-sized preview window side-by-side!
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --app="file:///%~dp0prototype.html" --window-size=414,896 --window-position=950,30
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" --app="file:///%~dp0prototype.html" --window-size=414,896 --window-position=950,30
) else if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --app="file:///%~dp0prototype.html" --window-size=414,896 --window-position=950,30
)

exit
