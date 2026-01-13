# 🏥 Características del Chatbot de Diabetes

## Descripción General
Un asistente inteligente para la gestión de diabetes que combina **predicción de insulina** con un **sistema de preguntas y respuestas** basado en una base de conocimiento médica de 87,000+ registros.

---

## ✨ Características Principales

### 1. 🔮 Predicción de Dosis de Insulina
- **Modelo Machine Learning**: Random Forest con R² = 0.9993
- **Entrada de datos flexible**: Lenguaje natural o valores específicos
- **Parámetros considerados**:
  - Minutos de ejercicio
  - Gramos de carbohidratos
  - Gramos de proteína
  - Gramos de grasa
  - Glucosa actual en mg/dL
- **Salida**: Dosis de insulina recomendada con análisis detallado

### 2. 💬 Sistema QA Completo (Question & Answering)
Base de conocimiento sobre diabetes con respuestas a:

#### 📋 Síntomas
- Signos de diabetes tipo 1 y tipo 2
- Síntomas de hipoglucemia e hiperglucemia
- Cuándo buscar atención médica

#### 🏥 Tipos de Diabetes
- Diabetes Tipo 1 (autoinmune)
- Diabetes Tipo 2 (más común)
- Diabetes Gestacional
- Prediabetes

#### ✓ Alimentación Recomendada
- Verduras saludables
- Frutas bajas en azúcar
- Proteínas magras
- Granos integrales
- Productos lácteos bajos en grasa
- Legumbres y frutos secos

#### ✗ Alimentos a Evitar
- Bebidas azucaradas
- Carbohidratos refinados
- Alimentos fritos
- Productos ultraprocesados

#### 🏃 Recomendaciones de Ejercicio
- 150 minutos semanales de actividad moderada
- Tipos específicos: caminar, nadar, ciclismo
- Entrenamiento de fuerza
- Precauciones importantes

#### 📊 Monitoreo de Glucosa
- Rangos normales de glucosa
- Hipoglucemia (glucosa baja)
- Hiperglucemia (glucosa alta)
- Frecuencia de monitoreo recomendada

#### 💊 Medicamentos Comunes
- Tipos de insulina (rápida, lenta, intermedia, basal)
- Metformina y otros antidiabéticos
- Inhibidores DPP-4 y GLP-1
- Efectos secundarios y consideraciones

#### ⚠️ Complicaciones
- Nefropatía diabética (daño renal)
- Retinopatía (daño ocular)
- Neuropatía (daño nervioso)
- Enfermedad cardiovascular
- Pie diabético
- Emergencias médicas

#### 🍎 Nutrición y Estilo de Vida
- Distribución de comidas
- Hidratación
- Sueño y estrés
- Tabaco y alcohol

#### 🤰 Diabetes y Embarazo
- Consideraciones especiales
- Monitoreo fetal
- Medicamentos seguros

#### ✈️ Viajes y Diabetes
- Consejos prácticos
- Cambios de zona horaria
- Documentación necesaria

### 3. 🔤 Corrección de Texto Automática
- **Corrección ortográfica**: Detecta errores comunes
  - hiras → horas
  - egercicios → ejercicios
  - glucoza → glucosa
  
- **Jerga y lenguaje coloquial**: 
  - traba → trabajo
  - laburo → trabajo
  - entreno → entrenamiento
  
- **Conversión de números**: 
  - "dos" → "2"
  - "treinta" → "30"

### 4. 🧠 Procesamiento de Lenguaje Natural (NLP)
- **Detección de ejercicio múltiple**: 
  - Entrada: "40 min caminar y 10 min saltar"
  - Resultado: 50 minutos totales

- **Detección de glucosa flexible**:
  - "glucosa de 170"
  - "glucosa es 170"
  - "mi glucosa 170"

- **Extracción de alimentos**: Reconoce más de 20 alimentos comunes

- **Cálculo de macronutrientes**: Estima automáticamente carbohidratos, proteína y grasa

### 5. 📚 Integración con Sistemas Médicos
- **RAG (Retrieval-Augmented Generation)**: Base de datos Vademecum con medicamentos
- **UMLS Integration**: Conceptos médicos estandarizados
- **Contextualización médica**: Análisis de riesgos y recomendaciones

### 6. 💾 Gestión de Pacientes
- **Almacenamiento en SQLite**: Base de datos segura
- **Historial de predicciones**: Seguimiento de tendencias
- **Reconocimiento de pacientes**: Carga automática de datos anteriores

---

## 📱 Interfaz de Usuario

### Frontend (React)
- Diseño responsivo y amigable
- Chat interactivo en tiempo real
- Respuestas con código de colores
- Indicadores de confianza

### Backend (FastAPI)
- API REST bien documentada
- Endpoints interactivos en `/docs`
- Manejo de errores robusto
- CORS habilitado para desarrollo

---

## 🚀 Ejemplos de Uso

### Predicción de Insulina
```
Usuario: "Hice 35 min de ejercicio, comí pan y dos huevos, mi glucosa es 155"
Resultado: "Se recomiendan X unidades de insulina rápida"
```

### Preguntas sobre Síntomas
```
Usuario: "¿Qué síntomas tiene la diabetes?"
Resultado: [Lista completa de síntomas con explicaciones]
```

### Preguntas sobre Alimentos
```
Usuario: "¿Qué alimentos puedo comer?"
Resultado: [Categorías de alimentos recomendados con ejemplos]
```

### Preguntas sobre Medicamentos
```
Usuario: "¿Cuáles son los tipos de insulina?"
Resultado: [Información sobre insulina rápida, lenta, etc.]
```

---

## 🔧 Arquitectura Técnica

### Stack Tecnológico
- **Frontend**: React.js con CSS personalizado
- **Backend**: FastAPI + Uvicorn
- **ML**: Scikit-learn (Random Forest)
- **BD**: SQLite3
- **NLP**: Custom parser + difflib (SequenceMatcher)
- **Datos**: Pandas para procesamiento

### Base de Datos de Conocimiento
- **data_general.csv**: 47,603 preguntas/respuestas médicas generales
- **data_medical.csv**: 40,442 pares entrada/salida de diagnóstico y tratamiento
- **DIABETES_KNOWLEDGE**: 15 tópicos hardcoded con información completa

### Modelos de ML
- Random Forest: 200 árboles, precisión R² = 0.9993
- Entrenado en datos sintéticos realistas de diabetes
- Predicciones calibradas con reglas médicas

---

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| Registros CSV | 87,645 |
| Tópicos de Diabetes | 15+ |
| Precisión del Modelo | 99.93% (R²) |
| Idioma Principal | Español |
| Correcciones Ortográficas | 80+ |
| Mapeos de Jerga | 20+ |
| Alimentos Reconocibles | 20+ |

---

## 🎯 Casos de Uso

1. **Pacientes Nuevos**: Educación sobre diabetes
2. **Pacientes Establecidos**: Predicción de insulina diaria
3. **Soporte Médico**: Información complementaria para consultas
4. **Investigación**: Base de datos de Q&A para análisis
5. **Educación**: Herramienta pedagógica sobre diabetes

---

## ⚠️ Disclaimer

**Este chatbot es una herramienta educativa y de soporte.**

- NO reemplaza asesoramiento médico profesional
- Consulta siempre con tu endocrinólogo
- Las predicciones de insulina deben validarse con profesionales
- En emergencias, contacta servicios médicos de emergencia

---

## 🚀 Futuras Mejoras

- [ ] Integración con glucómetros digitales
- [ ] API de integración con historias clínicas
- [ ] Múltiples idiomas
- [ ] Análisis de tendencias avanzado
- [ ] Notificaciones inteligentes
- [ ] Integración con dispositivos wearables
- [ ] Reportes PDF automáticos
- [ ] Soporte móvil nativo

---

## 📄 Licencia

Proyecto educativo para tesis universitaria.

---

**Versión**: 1.0  
**Última actualización**: Enero 2026  
**Estado**: Producción
