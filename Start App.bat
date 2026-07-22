@echo off
setlocal enabledelayedexpansion
title Image Caption Generator - Startup

echo ============================================================
echo   Image Caption Generator - Startup
echo ============================================================
echo.

REM ---------------------------------------------------------------
REM 1. Verify Python is installed
REM ---------------------------------------------------------------
echo [1/6] Checking for Python...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found on this computer.
    echo Please install Python 3.12 or newer from https://www.python.org/downloads/
    echo During installation, make sure to check "Add Python to PATH".
    echo.
    echo See INSTRUCTION.md for a full step-by-step guide.
    goto :error_exit
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VERSION=%%v
echo       Found Python %PY_VERSION%
echo.

REM ---------------------------------------------------------------
REM 2. Create a virtual environment if it does not already exist
REM ---------------------------------------------------------------
echo [2/6] Checking for virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo       No virtual environment found. Creating one now...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create the virtual environment.
        goto :error_exit
    )
    echo       Virtual environment created.
) else (
    echo       Virtual environment already exists.
)
echo.

REM ---------------------------------------------------------------
REM 3. Activate the virtual environment
REM ---------------------------------------------------------------
echo [3/6] Activating virtual environment...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo.
    echo ERROR: Failed to activate the virtual environment.
    goto :error_exit
)
echo       Activated.
echo.

REM ---------------------------------------------------------------
REM 4. Install dependencies
REM ---------------------------------------------------------------
echo [4/6] Installing dependencies (this may take a minute the first time)...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install required Python packages.
    echo Check your internet connection and try again.
    goto :error_exit
)
echo       Dependencies installed.
echo.

REM ---------------------------------------------------------------
REM 5. Verify the .env file exists and contains an API key
REM ---------------------------------------------------------------
echo [5/6] Checking configuration...
if not exist ".env" (
    echo       No .env file found. Creating one from .env.example...
    copy /Y ".env.example" ".env" >nul
    echo.
    echo ============================================================
    echo   ACTION REQUIRED
    echo   A new .env file was created for you.
    echo   Open it in a text editor and set OPENAI_API_KEY to your
    echo   own OpenAI API key, then run this script again.
    echo   See INSTRUCTION.md, section "Obtaining an OpenAI API key".
    echo ============================================================
    goto :error_exit
)

findstr /C:"OPENAI_API_KEY=sk-your-api-key-here" ".env" >nul
if not errorlevel 1 (
    echo.
    echo ============================================================
    echo   ACTION REQUIRED
    echo   Your .env file still contains the placeholder API key.
    echo   Open .env in a text editor and replace it with your real
    echo   OpenAI API key, then run this script again.
    echo   See INSTRUCTION.md, section "Obtaining an OpenAI API key".
    echo ============================================================
    goto :error_exit
)
echo       Configuration looks good.
echo.

REM ---------------------------------------------------------------
REM 6. Launch the application
REM ---------------------------------------------------------------
echo [6/6] Starting the Image Caption Generator...
echo       Once started, open http://127.0.0.1:8000 in your browser.
echo       Press CTRL+C in this window to stop the server.
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: The application exited unexpectedly. See the messages above.
    goto :error_exit
)

goto :end

:error_exit
echo.
echo ------------------------------------------------------------
echo   Startup did not complete successfully.
echo   Review the messages above, or see INSTRUCTION.md for help.
echo ------------------------------------------------------------
pause
exit /b 1

:end
pause
