@echo off
cd /d "%~dp0"
echo ==============================
echo  Thai Numeral Recognition
echo  http://localhost:5000
echo ==============================

if not exist venv\Scripts\activate.bat (
    echo [SETUP] Creating virtual environment...
    py -3.10 -m venv venv
    if errorlevel 1 (
        echo [ERROR] Python 3.10 not found. Install from https://www.python.org/downloads/release/python-31011/
        pause
        exit /b 1
    )
    echo [SETUP] Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo [SETUP] Done.
) else (
    call venv\Scripts\activate.bat
)

python app.py
pause
