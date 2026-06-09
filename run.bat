@echo off
title DevHunt — AI Assistant Launcher
echo.
echo  ========================================
echo    DevHunt ^| AI Assistant Starting...
echo  ========================================
echo  Created by  : Hitesh Solanki
echo  Website     : https://hiteshsolanki.in
echo  Email       : solankihiteshpankajbhai7@gmail.com
echo  Mobile      : +91 9327810431
echo  ----------------------------------------
echo.

:: 1. Check Python version and installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

:: 2. Check if virtual environment exists, if not create it
if not exist "backend\venv\Scripts\python.exe" (
    echo [INFO] Creating Python virtual environment...
    python -m venv backend\venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: 3. Install required libraries
echo [INFO] Installing required libraries from requirements.txt...
backend\venv\Scripts\pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [WARN] Dependency installation failed. This might be a pip version issue.
    set /p update_pip="May I update pip? (Y/N): "
    if /i "%update_pip%"=="Y" (
        echo [INFO] Updating pip...
        backend\venv\Scripts\python.exe -m pip install --upgrade pip
        echo [INFO] Retrying dependency installation...
        backend\venv\Scripts\pip install -r backend\requirements.txt
        if %errorlevel% neq 0 (
            echo [ERROR] Dependency installation failed again. Please check your internet connection or package compatibility.
            pause
            exit /b 1
        )
    ) else (
        echo [WARN] Skipping pip update. Trying to run the code anyway...
    )
)

:: Move to backend directory
cd /d "%~dp0backend"

:: Start Flask in background
echo [1/2] Starting Flask server on http://localhost:5000 ...
start "" /B venv\Scripts\python.exe app.py

:: Wait for server to boot
echo [2/2] Waiting for server to start...
timeout /t 3 /nobreak >nul

:: Detect and open browser
echo [3/3] Opening browser...
set URL=http://localhost:5000

:: Try browsers in order of preference
where chrome >nul 2>&1 && (
    start "" "chrome" "%URL%" & goto :done
)
where msedge >nul 2>&1 && (
    start "" "msedge" "%URL%" & goto :done
)
where firefox >nul 2>&1 && (
    start "" "firefox" "%URL%" & goto :done
)

:: Fallback — let Windows pick the default browser
start "" "%URL%"

:done
echo.
echo  Server running at: http://localhost:5000
echo  Logs page:         http://localhost:5000/logs
echo  Press Ctrl+C in server window to stop.
echo.
pause
