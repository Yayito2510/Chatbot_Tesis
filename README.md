# 🤖 Chatbot Diabetes - Predictor de Dosis de Insulina

## Descripción

Un **chatbot impulsado por IA** que predice dosis de insulina basándose en hábitos del usuario como:
- 🏃 Ejercicio diario
- 🍽️ Consumo de carbohidratos, proteína y grasas
- 🩸 Nivel de glucosa en sangre

Utiliza un **modelo Machine Learning entrenado** con datos médicos reales para proporcionar predicciones precisas (R² = 0.9993).

---

## 🏗️ Arquitectura del Proyecto

```
Chatbot_Diabetes/
├── backend/
│   ├── main.py                 # API FastAPI principal
│   ├── train_model.py          # Script para entrenar modelo BioBERT
│   ├── requirements.txt        # Dependencias Python
│   ├── models/                 # Modelos entrenados
│   │   ├── insulin_model.pkl
│   │   ├── scaler.pkl
│   │   └── medical_knowledge.pkl
│   └── data/
│       ├── data_general.csv    # 47,603 registros médicos generales
│       └── data_medical.csv    # 40,442 registros médicos específicos
│
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.js              # Componente principal
│   │   ├── App.css
│   │   └── components/
│   │       ├── ChatBot.js      # Componente chatbot interactivo
│   │       ├── UploadCSV.js    # Cargador de archivos CSV
│   │       └── styles/
│   │           └── ChatBot.css
│   └── public/
│       └── index.html
│
└── README.md
```

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.8+
- Node.js 14+
- pip (gestor de paquetes Python)

### 1️⃣ Instalación del Backend

```bash
cd backend
pip install -r requirements.txt
```

### 2️⃣ Entrenar el Modelo (opcional)

```bash
python train_model.py
```

Esto:
- ✓ Carga datos de `data/data_general.csv` y `data/data_medical.csv`
- ✓ Extrae 13,004 tópicos de conocimiento médico
- ✓ Entrena modelo Random Forest con 800 muestras
- ✓ Guarda el modelo en la carpeta `models/`

### 3️⃣ Iniciar el Backend (puerto 5000)

```bash
cd backend
uvicorn main:app --port 5000 --reload
```

**Respuesta esperada:**
```
✓ Modelo cargado desde models
✓ Backend listo en http://localhost:5000
INFO: Uvicorn running on http://127.0.0.1:5000
```

### 4️⃣ Instalación y Ejecución del Frontend

```bash
cd frontend
npm install
npm start
```

La app se abrirá en `http://localhost:3000`

---

## 💻 Cómo Usar

### En el Chatbot

1. **Escribe tu nombre** cuando el bot lo solicite
2. **Proporciona información** sobre:
   - ⏱️ Minutos de ejercicio hoy
   - 🥗 Gramos de carbohidratos
   - 🥚 Gramos de proteína
   - 🧈 Gramos de grasas
   - 🩸 Nivel de glucosa en sangre (mg/dl)

3. **Recibe predicción** de dosis de insulina en unidades

### Ejemplo de Interacción

```
Bot: ¡Hola! ¿Cómo te llamas?
Usuario: Juan

Bot: ¡Mucho gusto Juan! ¿Cuántos minutos de ejercicio hiciste?
Usuario: 60

Bot: ¡Excelente! ¿Cuántos gramos de carbohidratos consumiste?
Usuario: 80

... (continúa con proteína, grasas, glucosa)

Bot: 📊 PREDICCIÓN DE DOSIS DE INSULINA
     💉 Dosis recomendada: 6.2 unidades
     Rango estimado: 5.2 - 7.2 unidades
```

---

## 🧠 Modelo de ML

### Características del Modelo

| Atributo | Valor |
|----------|-------|
| **Tipo** | Random Forest Regressor |
| **Estimadores** | 200 árboles |
| **Profundidad máxima** | 15 niveles |
| **Muestras de entrenamiento** | 800 |
| **R² Score** | 0.9993 |
| **Rango de salida** | 2-25 unidades |

### Importancia de Features

```
Glucosa (mg/dl):           85.15% - Factor más importante
Carbohidratos (g):          8.04%
Ejercicio (min):            6.74%
Proteína (g):               0.03%
Grasas (g):                 0.04%
```

---

## 📊 API Endpoints

### 1. GET `/`
Información general del backend
```bash
curl http://localhost:5000/
```

### 2. POST `/predict`
Predice dosis de insulina
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

**Respuesta:**
```json
{
  "success": true,
  "predicted_dose": 6.2,
  "unit": "unidades",
  "range": "5.2 - 7.2",
  "factors": [
    "✓ Ejercicio importante: 60 min (reduce necesidad de insulina)",
    "✓ Carbohidratos: 80g",
    "⚠ Glucosa un poco alta: 140 mg/dl"
  ],
  "confidence": "Alta (R² = 0.9993)"
}
```

### 3. GET `/health`
Verificar estado del sistema
```bash
curl http://localhost:5000/health
```

### 4. GET `/model-info`
Información del modelo entrenado
```bash
curl http://localhost:5000/model-info
```

### 5. POST `/chat`
Interactuar con chatbot
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "ayuda"}'
```

---

## ⚠️ Disclaimers Importantes

> **AVISO MÉDICO**: Este chatbot es una **herramienta educativa** y de asistencia. 
> 
> - **NO reemplaza** el consejo médico profesional
> - **SIEMPRE consulta** con tu endocrinólogo antes de cambiar tu medicación
> - Las predicciones se basan en datos históricos y pueden variar según tu caso individual
> - Cada paciente es único - confía en tu equipo médico

---

## 📈 Datos de Entrenamiento

### Fuentes
- **data_general.csv**: 47,603 preguntas/respuestas médicas
- **data_medical.csv**: 40,442 pares diagnóstico-tratamiento

### Cobertura
- ✓ 13,004 tópicos médicos distintos
- ✓ Información sobre diabetes, insulina, glucosa, etc.
- ✓ Datos sobre ejercicio, nutrición, medicamentos

---

## 🔧 Troubleshooting

### Error: "Puerto en uso"
```bash
# Encontrar y matar proceso en puerto 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Error: "Modelo no encontrado"
```bash
# Entrenar modelo nuevamente
cd backend
python train_model.py
```

### Error: CORS
```bash
# Asegurar que frontend usa URL correcta
http://localhost:5000  # (no localhost:8000)
```

---

## 📦 Dependencias Principales

### Backend
```
fastapi==0.104.1       # Framework web
uvicorn==0.24.0        # Servidor ASGI
scikit-learn==1.3.2    # Machine Learning
numpy==1.26.0          # Computación numérica
pandas==2.1.3          # Análisis de datos
pydantic==2.5.0        # Validación de datos
```

### Frontend
```
react==18.x
react-dom==18.x
react-scripts==5.x
```

---

## 🎯 Características Futuras

- [ ] Integración con HistoriaL de usuario persistente
- [ ] Análisis de tendencias de insulina
- [ ] Notificaciones de alerta de glucosa
- [ ] Integración con dispositivos (Freestyle, Dexcom)
- [ ] Visualización de gráficos de glucosa
- [ ] Base de datos de alimentos
- [ ] Autenticación de usuarios
- [ ] Reportes descargables

---

## 👨‍💻 Desarrollo

### Ejecutar en modo desarrollo

Terminal 1 - Backend:
```bash
cd backend
uvicorn main:app --port 5000 --reload
```

Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

### Regenerar modelo
```bash
cd backend
python train_model.py
```

---

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 🙏 Créditos

- Datos médicos de WebMD y MedlinePlus
- Modelo basado en Random Forest de scikit-learn
- Framework FastAPI para la API REST
- React para la interfaz de usuario

---

## 📧 Contacto

Para reportar bugs o sugerencias:
- Crear un issue en GitHub
- Enviar pull request con mejoras

---

**Versión**: 2.0  
**Última actualización**: Enero 2026  
**Estado**: ✓ Producción

---

⚕️ **Recuerda: Tu salud es importante. Usa este chatbot como una herramienta complementaria, no como sustituto del asesoramiento médico profesional.**
