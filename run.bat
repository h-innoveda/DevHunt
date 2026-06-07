@echo off
title DevHunt — AI Assistant Launcher
echo.
echo  ========================================
echo    DevHunt ^| AI Assistant Starting...
echo  ========================================
echo.
echo  Created by  : Hitesh Solanki
echo  Website     : https://hiteshsolanki.in
echo  Email       : solankihiteshpankajbhai7@gmail.com
echo  Mobile      : +91 9327810431
echo  ----------------------------------------
echo.

:: Move to backend directory
cd /d "%~dp0backend"

:: Check venv exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Run: python -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

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
