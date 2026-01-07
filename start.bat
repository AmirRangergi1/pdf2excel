@echo off
echo 🚀 PDF to Excel Converter - Starting Application
echo ==================================================
echo.

REM Get the directory where this script is located
setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Build Frontend
echo �� Building Frontend...
echo.

cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Build the frontend
echo Building Vue.js application...
call npm run build

if errorlevel 1 (
    echo ❌ Frontend build failed!
    pause
    exit /b 1
)

echo ✅ Frontend built successfully!
echo.

REM Setup Backend
echo 🔧 Setting up Backend...
echo.

cd ..\backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing backend dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Backend setup failed!
    pause
    exit /b 1
)

echo ✅ Backend setup complete!
echo.

REM Start backend
echo 🌐 Starting FastAPI Backend...
echo     Backend: http://localhost:8000
echo.
echo ==========================================
echo Application is ready!
echo ==========================================
echo.
echo Open your browser to: http://localhost:8000
echo.
echo Press Ctrl+C to stop the application
echo.

python main.py

pause
