# Script para iniciar Chatbot Diabetes (Backend + Frontend)

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CHATBOT DIABETES - Startup" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend")) {
    Write-Host "Error: No encontrado directorio 'backend'" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "Error: No encontrado directorio 'frontend'" -ForegroundColor Red
    exit 1
}

Write-Host "OK - Directorios encontrados" -ForegroundColor Green
Write-Host ""

# Instalar dependencias backend si es necesario
if (-not (Test-Path "backend\models")) {
    Write-Host "Entrenando modelo..." -ForegroundColor Yellow
    cd backend
    python train_model.py
    cd ..
    Write-Host "OK - Modelo entrenado" -ForegroundColor Green
}

Write-Host ""
Write-Host "OK - Iniciando servicios..." -ForegroundColor Green
Write-Host ""

# Iniciar Backend
Write-Host "Iniciando Backend en puerto 5000..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit -Command", "cd '$PWD\backend'; uvicorn main:app --port 5000 --reload"

# Esperar a que el backend se inicie
Start-Sleep -Seconds 3

# Iniciar Frontend
Write-Host "Iniciando Frontend en puerto 3000..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit -Command", "cd '$PWD\frontend'; npm start"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "OK - Servicios iniciados:" -ForegroundColor Green
Write-Host "  - Backend:  http://localhost:5000" -ForegroundColor Yellow
Write-Host "  - API Docs: http://localhost:5000/docs" -ForegroundColor Yellow
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Cierra estas ventanas cuando termines." -ForegroundColor Yellow
