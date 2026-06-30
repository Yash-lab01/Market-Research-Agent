@echo off
echo ============================================
echo   Market Research Agent - Setup
echo ============================================
echo.

REM Check if .env exists
if not exist .env (
    echo [1/3] Creating .env from template...
    copy .env.example .env
    echo.
    echo  *** IMPORTANT: Open .env and fill in your API keys ***
    echo  *** TAVILY_API_KEY and GEMINI_API_KEY are required  ***
    echo.
    pause
)

echo [2/3] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [3/3] Creating data directories...
if not exist data\reports mkdir data\reports
if not exist data\chroma  mkdir data\chroma

echo.
echo ============================================
echo   Setup complete!
echo   Run start.bat to launch the application.
echo ============================================
pause
