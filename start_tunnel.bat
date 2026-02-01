@echo off
REM ============================================
REM Script de inicio: Backend + Túnel Cloudflare
REM ============================================

echo ========================================
echo   NotebookLM API - Inicio con Tunel
echo ========================================
echo.

echo [1/3] Iniciando servidor FastAPI...
start "FastAPI Backend" cmd /k "cd /d %~dp0 && python api_server.py"

echo [2/3] Esperando 3 segundos para que el servidor arranque...
timeout /t 3 /nobreak >nul

echo [3/3] Iniciando tunel Cloudflare...
start "Cloudflare Tunnel" cmd /k "cd /d %~dp0 && .\cloudflared.bat tunnel run notebooklm-api"

echo.
echo ========================================
echo   TODO LISTO!
echo ========================================
echo.
echo - Backend:    http://localhost:8000
echo - Tunel:      https://notebooklm.carrysoft.com
echo - Swagger:    http://localhost:8000/docs
echo.
echo Para detener: Cierra las ventanas de terminal
echo ========================================

pause
