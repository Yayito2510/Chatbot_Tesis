@echo off
REM Script para iniciar Chatbot Diabetes (Backend + Frontend)

echo.
echo ==========================================
echo   🤖 CHATBOT DIABETES - Startup
echo ==========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist backend\ (
    echo ❌ Error: No encontrado directorio 'backend'
    exit /b 1
)

if not exist frontend\ (
    echo ❌ Error: No encontrado directorio 'frontend'
    exit /b 1
)

echo ✓ Directorios encontrados
echo.

REM Instalar dependencias backend si es necesario
if not exist backend\venv\ (
    echo 📦 Instalando dependencias del backend...
    cd backend
    pip install -r requirements.txt -q
    cd ..
    echo ✓ Backend listo
)

echo.
echo ✓ Iniciando servicios...
echo.

REM Abrir Terminal 1: Backend
echo 🚀 Iniciando Backend en puerto 5000...
start cmd /k "cd backend && uvicorn main:app --port 5000 --reload"

REM Esperar un poco para que el backend se inicie
timeout /t 3 /nobreak

REM Abrir Terminal 2: Frontend
echo 🚀 Iniciando Frontend en puerto 3000...
start cmd /k "cd frontend && npm start"

echo.
echo ==========================================
echo ✓ Servicios iniciados:
echo   - Backend:  http://localhost:5000
echo   - API Docs: http://localhost:5000/docs
echo   - Frontend: http://localhost:3000
echo ==========================================
echo.
pause
