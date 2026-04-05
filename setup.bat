@echo off
REM Quick setup script for development on Windows

setlocal enabledelayedexpansion

echo.
echo 🚀 Setting up Text Summarization Project...
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✓ Python version: %python_version%

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📚 Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating .env file from template...
    copy .env.example .env
    echo    💡 Remember to customize .env if needed
) else (
    echo ✓ .env file already exists
)

REM Run tests
echo 🧪 Running tests...
pytest tests\ -v --tb=short
if errorlevel 1 (
    echo ⚠️  Some tests may have failed - check output above
)

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo    1. Activate environment: venv\Scripts\activate
echo    2. Run app: streamlit run app.py
echo    3. Open browser: http://localhost:8501
echo.
echo 🔗 Useful commands:
echo    - pytest              : Run tests
echo    - black src\ tests\    : Format code
echo    - flake8 src\ tests\   : Lint code
echo    - mypy src\            : Type check
echo.

pause
