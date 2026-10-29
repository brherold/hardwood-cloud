@echo off
setlocal
cd /d "%~dp0"
echo ========================================================
echo Deploying changes to GitHub and Render...
echo ========================================================
git add .
set /p msg="Enter commit message (or press Enter for default): "
if "%msg%"=="" set msg=Update features and UI
git commit -m "%msg%"
git push origin main
if errorlevel 1 (
    echo.
    echo Push failed. Check your internet connection or git status.
    pause
) else (
    echo.
    echo ========================================================
    echo Successfully pushed to GitHub!
    echo Render will build and deploy your update shortly.
    echo ========================================================
    timeout /t 5
)
endlocal
