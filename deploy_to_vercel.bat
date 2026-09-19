@echo off
title Push Fixes to Vercel
echo ========================================================
echo   BloodChain AI - Push Vercel 500 Fix to GitHub
echo ========================================================
echo.
cd /d "%~dp0"

echo [1] Checking Git status...
git status

echo.
echo [2] Adding all updated files (api/index.py, vercel.json, app.py, database.py)...
git add .

echo.
echo [3] Committing Vercel Serverless configuration fix...
git commit -m "Fix Vercel 500 Function Not Found error: add api/index.py and vercel.json rewrites"

echo.
echo [4] Pushing to your GitHub repository...
git push origin main

echo.
echo ========================================================
echo   Done! Vercel is now building your latest deployment.
echo   Visit: https://sri-umber.vercel.app/
echo ========================================================
pause
