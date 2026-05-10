@echo off
cd /d "%~dp0"
echo ==============================
echo  Thai Numeral Recognition
echo  http://localhost:5000
echo ==============================

if not exist venv\Scripts\python.exe (
    echo [SETUP] Creating virtual environment...
    py -3.10 -m venv venv
    if errorlevel 1 (
        echo [ERROR] Python 3.10 not found. Install from https://www.python.org/downloads/release/python-31011/
        pause
        exit /b 1
    )
    echo [SETUP] Installing dependencies ^(this may take a few minutes^)...
    venv\Scripts\pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [SETUP] Done.
)

start "" /b cmd /c "timeout /t 3 /nobreak > nul && start http://localhost:5000"
echo [OK] Starting server...
venv\Scripts\python.exe app.py
pause
