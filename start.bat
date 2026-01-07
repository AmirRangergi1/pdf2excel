@echo off
echo 🚀 PDF to Excel Converter - Quick Start
echo ========================================
echo.
echo Setting up Backend...
echo.

cd backend

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

REM Start backend
echo Starting FastAPI backend on http://localhost:8000...
start cmd /k python main.py

timeout /t 2

echo.
echo Setting up Frontend...
echo.

cd ..\frontend

REM Install dependencies
echo Installing frontend dependencies...
npm install

REM Start frontend
echo Starting Vue.js frontend on http://localhost:5173...
echo.
echo ✅ Application is ready! Open http://localhost:5173 in your browser
echo.
echo To stop the application, press Ctrl+C in both windows
echo.

npm run dev
