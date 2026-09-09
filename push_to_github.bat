@echo off
title ProgressPro - Push to GitHub
echo ===================================================================
echo ProgressPro - Pushing to GitHub (https://github.com/ARUN-444/ProgressPro)
echo ===================================================================
set "PATH=C:\Program Files\Git\cmd;%PATH%"

echo Checking remote configuration...
git remote -v

echo.
echo Pushing branch 'main' to origin...
echo (If a browser window appears, click 'Authorize GitCredentialManager')
echo.
git push -u origin main

echo.
echo ===================================================================
pause
