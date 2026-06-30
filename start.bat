@echo off
echo ============================================
echo   Market Research Agent - Starting...
echo ============================================
echo.
echo Make sure Ollama is running: ollama serve
echo.

REM Start FastAPI in a new window
start "FastAPI - Market Research Agent" cmd /k "uvicorn api.main:app --reload --port 8000"

REM Wait 3 seconds for API to boot
timeout /t 3 /nobreak >nul

REM Start Streamlit in a new window
start "Streamlit UI - Market Research Agent" cmd /k "streamlit run ui/app.py"

echo.
echo Both services started!
echo  - API:  http://localhost:8000/docs
echo  - UI:   http://localhost:8501
echo.
echo Close the terminal windows to stop the services.
pause
