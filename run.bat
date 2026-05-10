@echo off
cd /d "%~dp0"
echo ==============================
echo  Thai Numeral Recognition
echo  http://localhost:5000
echo ==============================

if exist venv\Scripts\python.exe goto :run

echo [SETUP] Looking for Python 3.10 / 3.11 / 3.12 ...

set PYEXE=
py -3.12 --version >nul 2>&1 && set PYEXE=py -3.12
py -3.11 --version >nul 2>&1 && set PYEXE=py -3.11
py -3.10 --version >nul 2>&1 && set PYEXE=py -3.10

if not defined PYEXE (
    python --version >nul 2>&1 && set PYEXE=python
)

if not defined PYEXE (
    echo [ERROR] Python not found.
    echo         Install Python 3.10-3.12 from https://www.python.org/downloads/
    echo         Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [SETUP] Creating virtual environment with %PYEXE% ...
%PYEXE% -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [SETUP] Installing dependencies (this may take a few minutes)...
venv\Scripts\pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [SETUP] Done.

:run
echo [OK] Starting server...
venv\Scripts\python.exe app.py
pause
