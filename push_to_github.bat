@echo off
set "PATH=C:\Users\sayan\AppData\Local\Programs\MinGit\cmd;%PATH%"
echo =======================================================
echo   AquaPulse - Push to GitHub (https://github.com/sayanrooj/aquapulse)
echo =======================================================
echo.
echo Step 1: Making sure repository is created on GitHub...
echo (If you haven't already, please create an empty repository named 'aquapulse' at https://github.com/new)
echo.
echo Step 2: Pushing main branch to origin...
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo =======================================================
    echo   SUCCESS! Uploaded to https://github.com/sayanrooj/aquapulse
    echo =======================================================
) else (
    echo.
    echo If prompted, please enter your GitHub username and Personal Access Token (PAT).
)
pause
