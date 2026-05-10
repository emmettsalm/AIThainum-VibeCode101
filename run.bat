@echo off
cd /d "%~dp0"
echo ==============================
echo  Thai Numeral Recognition
echo  http://localhost:5000
echo ==============================

if not exist venv\Scripts\python.exe (
    echo [SETUP] Looking for compatible Python (3.10 / 3.11 / 3.12)...
    set PYEXE=
    for %%v in (3.10 3.11 3.12) do (
        if not defined PYEXE (
            py -%%v --version >nul 2>&1 && set PYEXE=%%v
        )
    )
    if not defined PYEXE (
        echo [ERROR] Python 3.10-3.12 not found.
        echo         Download: https://www.python.org/downloads/release/python-31011/
        pause
        exit /b 1
    )
    echo [SETUP] Using Python %PYEXE% — creating virtual environment...
    py -%PYEXE% -m venv venv
    echo [SETUP] Installing dependencies (this may take a few minutes)...
    venv\Scripts\pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [SETUP] Done.
)

echo [OK] Starting server...
venv\Scripts\python.exe app.py
pause
