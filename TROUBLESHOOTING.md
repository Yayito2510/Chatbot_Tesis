# 🔧 Guía de Troubleshooting - Chatbot Diabetes

## ❌ Problemas Comunes y Soluciones

### 1. Puerto ya en uso

**Problema**: `ERROR: Address already in use`

**Soluciones**:

#### Windows (CMD)
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

#### PowerShell
```powershell
Get-NetTCPConnection -LocalPort 5000 | Select-Object OwningProcess
Stop-Process -Id <PID> -Force
```

#### Alternativa: Usar otro puerto
```bash
uvicorn main:app --port 5001
# Cambiar también en ChatBot.js
```

---

### 2. Modelo no encontrado

**Problema**: `Model not found` o predicción falla

**Solución**:
```bash
cd backend
python train_model.py
```

**Esto:**
- ✓ Entrena nuevo modelo
- ✓ Guarda en `models/`
- ✓ Carga datos automáticamente

---

### 3. CORS Error

**Problema**: 
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solución**: Verificar URL en `frontend/src/components/ChatBot.js`
```javascript
// Debe ser http://localhost:5000 (no 8000)
const response = await fetch("http://localhost:5000/predict", {
```

---

### 4. Backend no responde

**Problema**: `Connection refused` o timeout

**Verificar**:
1. ¿Backend está corriendo?
2. ¿Puerto correcto? (5000)
3. ¿URL correcta en frontend?

**Verificar estado**:
```bash
curl http://localhost:5000/health
```

**Respuesta esperada**:
```json
{"status": "ok", "model_trained": true}
```

---

### 5. Frontend no carga

**Problema**: Blank page o errores en consola

**Soluciones**:
```bash
# Limpiar cache de npm
npm cache clean --force

# Reinstalar dependencias
rm -r node_modules package-lock.json
npm install

# Iniciar nuevamente
npm start
```

---

### 6. Dependencias faltantes

**Problema**: `ModuleNotFoundError` en Python

**Solución**:
```bash
cd backend
pip install -r requirements.txt --force-reinstall
```

---

### 7. Modelo toma mucho tiempo

**Problema**: Backend lento al iniciar

**Información**: El modelo se entrena la primera vez (~30 segundos)

**Soluciones futuras**:
- Usar modelo preentrenado
- Reducir tamaño del dataset
- Usar GPU si está disponible

---

### 8. Error: "Cannot import train_model"

**Problema**: `ImportError: cannot import name 'DiabetesInsulinPredictor'`

**Solución**:
```bash
cd backend
# Verificar que main.py puede importar train_model.py
python -c "from train_model import DiabetesInsulinPredictor; print('OK')"
```

---

### 9. React Warning: Unused variable

**Problema**: 
```
Warning: 'predictedDose' is assigned a value but never used
```

**Solución**: No afecta funcionamiento, es un warning menor que se puede ignorar.

**Para eliminar**:
```javascript
// Agregar comentario en ChatBot.js línea 18
// eslint-disable-next-line no-unused-vars
const [predictedDose, setPredictedDose] = useState(null);
```

---

### 10. Base de datos de modelos corrupta

**Problema**: Error al cargar modelo entrenado

**Solución**:
```bash
cd backend/models
# Eliminar archivos viejos
rm insulin_model.pkl scaler.pkl medical_knowledge.pkl

# Reentrenar
cd ..
python train_model.py
```

---

## 🧪 Verificación del Sistema

### Checklist de Diagnóstico

```bash
# 1. Verificar Python
python --version
# Debe ser 3.8+

# 2. Verificar Node.js
node --version
npm --version
# Node debe ser 14+

# 3. Verificar instalación backend
cd backend
python -c "import fastapi, uvicorn, sklearn, pandas; print('✓ OK')"

# 4. Verificar instalación frontend
cd frontend
npm ls react react-dom react-scripts

# 5. Verificar modelo
cd backend
python -c "from train_model import DiabetesInsulinPredictor; p = DiabetesInsulinPredictor(); print(p.load_model())"

# 6. Verificar API
curl http://localhost:5000/health
```

---

## 📊 Logs Útiles

### Backend Logs

Buscar estos mensajes en la terminal del backend:

```
✓ Modelo cargado desde models
✓ Backend listo en http://localhost:5000
INFO: Application startup complete
```

### Frontend Logs

Buscar estos mensajes en la terminal del frontend:

```
webpack compiled successfully
Compiled with warnings (normal)
```

### Browser Console

Abrir DevTools (F12) y revisar:
- Network: Verificar POST a `/predict`
- Console: Buscar errores rojos
- Application: Verificar localStorage

---

## 🆘 Cuando Nada Funciona

### Plan de Recuperación

1. **Reiniciar Todo**
```bash
# Matar procesos
# Borrar node_modules, __pycache__
# Reinstalar dependencias
# Reentrenar modelo
```

2. **Verificar Puertos**
```bash
# Linux/Mac
lsof -i :5000
lsof -i :3000

# Windows
netstat -ano | findstr :5000
netstat -ano | findstr :3000
```

3. **Limpiar Cache**
```bash
# npm
npm cache clean --force

# Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

4. **Revertir Cambios**
```bash
git status
git restore <archivo>
```

---

## 🎯 Testing Manual

### Test 1: API Health Check
```bash
curl http://localhost:5000/health
# Esperado: {"status": "ok", "model_trained": true}
```

### Test 2: Model Info
```bash
curl http://localhost:5000/model-info
# Esperado: Info del modelo
```

### Test 3: Predict
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
# Esperado: Predicción de dosis
```

### Test 4: Chat
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hola"}'
# Esperado: Respuesta del chatbot
```

---

## 📞 Contacto de Soporte

Si nada de esto funciona:

1. Revisar los logs completos
2. Captura de pantalla de errores
3. Información del sistema (Python, Node, SO)
4. Pasos específicos para reproducir

---

**Última actualización**: Enero 12, 2026  
**Versión**: 2.0.0
