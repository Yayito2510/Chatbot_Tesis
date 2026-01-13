# ⚡ QUICK START - Chatbot Diabetes

## 🚀 3 Pasos para Empezar

### Paso 1: Instalar Dependencias

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Paso 2: Iniciar Backend

```bash
cd backend
python -m uvicorn main:app --port 5000 --reload
```

**Esperado:**
```
✓ Modelo cargado desde models
✓ Backend listo en http://localhost:5000
INFO: Application startup complete
```

### Paso 3: Iniciar Frontend

```bash
cd frontend
npm start
```

**Abre**: http://localhost:3000

---

## ✅ ¿Está funcionando?

### Verificar Backend
```bash
curl http://localhost:5000/health
```

Respuesta esperada:
```json
{"status": "ok", "model_trained": true}
```

### Probar Predicción
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_minutes": 60,
    "carbohydrates": 80,
    "protein": 20,
    "fats": 10,
    "glucose": 140
  }'
```

### Usar el Chatbot
1. Abre http://localhost:3000
2. Escribe tu nombre
3. Sigue las preguntas
4. Recibe predicción

---

## 📚 Documentación Completa

- [README.md](README.md) - Guía principal
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Solución de problemas
- [DEPLOYMENT.md](DEPLOYMENT.md) - Despliegue en producción

---

## 🎯 URLs Locales

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:5000 |
| API Docs | http://localhost:5000/docs |

---

## ⚠️ Requisitos

- Python 3.8+
- Node.js 14+
- Puertos 5000 y 3000 disponibles

---

## 🔧 Scripts Automáticos

### Windows (CMD)
```bash
start.bat
```

### PowerShell
```powershell
.\start.ps1
```

---

**¡Eso es todo! Ya está funcionando.** 🎉
