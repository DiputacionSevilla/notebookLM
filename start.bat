@echo off
echo ================================================
echo    NotebookLM Chat - Iniciando Servicios
echo ================================================
echo.

REM Iniciar FastAPI en segundo plano
echo [1/2] Iniciando servidor FastAPI en puerto 8000...
start "FastAPI Server" cmd /c "python api_server.py"

REM Esperar un momento para que FastAPI inicie
timeout /t 3 /nobreak > nul

REM Iniciar Streamlit
echo [2/2] Iniciando Streamlit en puerto 8501...
echo.
echo ================================================
echo    Abre http://localhost:8501 en tu navegador
echo ================================================
echo.

python -m streamlit run app.py
