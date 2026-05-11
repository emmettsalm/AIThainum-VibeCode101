@echo off
:: Re-launch in a persistent CMD window so it never flashes and closes
if "%LAUNCHED%"=="" (
    set LAUNCHED=1
    cmd /k ""%~f0""
    exit
)

cd /d "%~dp0"
echo ==============================
echo  Thai Numeral Recognition
echo  http://localhost:5000
echo ==============================

:: Check if path is too long (Windows limit is 260 chars)
set "CURRENT_PATH=%~dp0"
if not "%CURRENT_PATH:~200,1%"=="" (
    echo [ERROR] โฟลเดอร์อยู่ลึกเกินไป path ยาวเกิน 200 ตัวอักษร
    echo         กรุณาย้ายโฟลเดอร์นี้ไปไว้ที่ C:\CS462\ แล้วลองใหม่
    echo         เช่น C:\CS462\AIThainum-VibeCode101-main\
    goto :end
)

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
    goto :end
)

echo [SETUP] Creating virtual environment with %PYEXE% ...
%PYEXE% -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    goto :end
)

echo [SETUP] Installing dependencies (this may take a few minutes)...
venv\Scripts\pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    goto :end
)
echo [SETUP] Done.

:run
echo [OK] Starting server...
venv\Scripts\python.exe app.py

echo.
set /p RESTART=Server stopped. Run again? (Y/N):
if /i "%RESTART%"=="Y" goto :run

:end
echo Closed.

