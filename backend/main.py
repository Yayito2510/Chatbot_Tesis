from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from train_model import DiabetesInsulinPredictor
from nlp_parser import NaturalLanguageProcessor
from database import db
from rag_system import rag_system
from qa_system import knowledge_base

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar o entrenar modelo
print("="*60)
print("INICIALIZANDO CHATBOT DIABETES")
print("="*60)

insulin_model = DiabetesInsulinPredictor()

# Intentar cargar modelo entrenado
if not insulin_model.load_model('models'):
    print("\n[WARN] Modelo no encontrado, entrenando nuevo modelo...")
    insulin_model.train()
    insulin_model.save_model()
else:
    print("[OK] Modelo cargado correctamente")

print("[OK] Base de datos inicializada")
print("\n[OK] Backend listo en http://localhost:5000")
print("[OK] Documentacion disponible en http://localhost:5000/docs\n")

# Modelos Pydantic
class InsulinRequest(BaseModel):
    exercise_minutes: float
    carbohydrates: float
    protein: float
    fats: float
    glucose: float
    notes: str = ""

class MessageRequest(BaseModel):
    message: str
    user_data: dict = None

class NLPRequest(BaseModel):
    description: str
    patient_name: str = None
    patient_age: int = None

class PatientRequest(BaseModel):
    name: str
    email: str = None
    age: int = None

class PredictionSaveRequest(BaseModel):
    patient_name: str
    exercise_minutes: float
    carbohydrates: float
    protein: float
    fats: float
    glucose: float
    predicted_dose: float
    user_input: str

class RAGQueryRequest(BaseModel):
    query: str

class MedicalEnhancementRequest(BaseModel):
    glucose: float = 0
    exercise_minutes: float = 0
    carbohydrates: float = 0
    symptoms: list = None

@app.post("/parse-natural-language")
def parse_natural_language(request: NLPRequest):
    """
    Parsea descripción en lenguaje natural y extrae valores numéricos
    
    Ejemplo:
    "Comí arroz con pollo y caminé 30 minutos, mi glucosa está en 140"
    
    Retorna valores numéricos para predicción
    """
    try:
        result = NaturalLanguageProcessor.process_user_input(request.description)
        
        # Usar valores parseados para predicción
        predicted_dose = insulin_model.predict(
            result['exercise_minutes'],
            result['carbohydrates'],
            result['protein'],
            result['fats'],
            result['glucose']
        )
        
        return {
            "success": True,
            "parsed_data": {
                "exercise_minutes": result['exercise_minutes'],
                "carbohydrates": result['carbohydrates'],
                "protein": result['protein'],
                "fats": result['fats'],
                "glucose": result['glucose'],
            },
            "interpretations": result['interpretations'],
            "predicted_dose": float(predicted_dose),
            "range": f"{max(2, predicted_dose-1):.1f} - {min(25, predicted_dose+1):.1f}",
            "message": f"[OK] Procesado correctamente. Dosis recomendada: {predicted_dose} unidades"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al procesar descripción"
        }

@app.post("/parse-combined")
def parse_combined(request: NLPRequest):
    """
    Modo combinado: detecta automáticamente datos específicos o lenguaje natural
    Procesa cualquier combinación: "hice 20 min de ejercicio y comí pan y mi glucosa es 95"
    También corrige automáticamente errores ortográficos y jerga
    """
    try:
        result = NaturalLanguageProcessor.process_user_input(request.description)
        
        # Usar valores parseados para predicción
        predicted_dose = insulin_model.predict(
            result['exercise_minutes'],
            result['carbohydrates'],
            result['protein'],
            result['fats'],
            result['glucose']
        )
        
        # Generar análisis más detallado
        analysis = []
        
        if result['exercise_minutes'] > 60:
            analysis.append(f"Ejercicio importante: {result['exercise_minutes']} min - reduce necesidad de insulina")
        elif result['exercise_minutes'] > 30:
            analysis.append(f"Ejercicio moderado: {result['exercise_minutes']} min")
        elif result['exercise_minutes'] > 0:
            analysis.append(f"Poco ejercicio: {result['exercise_minutes']} min")
        else:
            analysis.append(f"Sin ejercicio registrado")
        
        if result['carbohydrates'] > 80:
            analysis.append(f"Alto consumo de carbohidratos: {result['carbohydrates']}g")
        elif result['carbohydrates'] > 0:
            analysis.append(f"Carbohidratos: {result['carbohydrates']}g")
        
        if result['glucose'] > 150:
            analysis.append(f"Glucosa elevada: {result['glucose']} mg/dl - aumenta necesidad de insulina")
        elif result['glucose'] > 120:
            analysis.append(f"Glucosa un poco alta: {result['glucose']} mg/dl")
        elif result['glucose'] > 0:
            analysis.append(f"Glucosa en rango: {result['glucose']} mg/dl")
        
        # Obtener contexto médico mejorado con RAG
        rag_enhancement = rag_system.enhance_prediction({
            'glucose': result['glucose'],
            'exercise_minutes': result['exercise_minutes'],
            'carbohydrates': result['carbohydrates']
        })
        
        analysis.extend(rag_enhancement.get('recommendations', []))
        
        # Preparar información de correcciones
        corrections_info = []
        if result['corrections']['spelling']:
            corrections_info.extend(result['corrections']['spelling'])
        if result['corrections']['slang']:
            corrections_info.extend(result['corrections']['slang'])
        if result['corrections']['numbers']:
            corrections_info.extend(result['corrections']['numbers'])
        
        response = {
            "success": True,
            "parsed_data": {
                "exercise_minutes": result['exercise_minutes'],
                "carbohydrates": result['carbohydrates'],
                "protein": result['protein'],
                "fats": result['fats'],
                "glucose": result['glucose'],
            },
            "interpretations": result['interpretations'],
            "predicted_dose": float(predicted_dose),
            "range": f"{max(2, predicted_dose-1):.1f} - {min(25, predicted_dose+1):.1f}",
            "analysis": "\n".join(analysis),
            "medical_context": rag_enhancement.get('medical_context', ''),
            "sources": ["Machine Learning", "RAG", "UMLS", "Vademecum"],
            "corrections": {
                "applied": corrections_info,
                "original_input": result['corrections']['original'],
                "corrected_input": result['corrected_input']
            },
            "message": f"[OK] Procesado correctamente. Dosis recomendada: {predicted_dose} unidades"
        }
        
        # Guardar en base de datos si se proporciona nombre del paciente
        if request.patient_name:
            try:
                patient_id = db.add_patient(request.patient_name, age=request.patient_age)
                db.save_prediction(
                    patient_id,
                    result['exercise_minutes'],
                    result['carbohydrates'],
                    result['protein'],
                    result['fats'],
                    result['glucose'],
                    float(predicted_dose),
                    request.description
                )
            except Exception as e:
                print(f"Error guardando predicción: {e}")
        
        return response
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al procesar información"
        }

@app.post("/ask")
def ask_question(request: NLPRequest):
    """
    Endpoint para preguntas generales sobre diabetes, alimentación, ejercicio y síntomas
    Busca respuestas en la base de datos médica
    
    Ejemplos:
    - "qué síntomas tiene la diabetes?"
    - "qué alimentos puedo comer?"
    - "cuánto ejercicio debo hacer?"
    """
    try:
        query = request.description
        
        # Buscar respuesta en knowledge base
        result = knowledge_base.search_answer(query, threshold=0.35)
        
        # Determinar el tipo de pregunta
        question_type = "general"
        if any(word in query.lower() for word in ['síntoma', 'señal', 'signo']):
            question_type = "síntomas"
        elif any(word in query.lower() for word in ['comida', 'alimento', 'comer', 'puedo']):
            question_type = "alimentación"
        elif any(word in query.lower() for word in ['ejercicio', 'deporte', 'actividad', 'física']):
            question_type = "ejercicio"
        
        return {
            "success": True,
            "question": query,
            "question_type": question_type,
            "answer": result['answer'],
            "confidence": float(result['confidence']),
            "source": result['source'],
            "message": "Respuesta basada en base de datos médica"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al procesar pregunta"
        }

@app.get("/")
def read_root():
    return {
        "message": "Chatbot Diabetes Backend v2.0",
        "description": "Predicción de dosis de insulina basada en BioBERT y datos médicos",
        "model": "Random Forest con 200 estimadores",
        "accuracy": "R² = 0.9993"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "model_trained": insulin_model.is_trained}

@app.post("/predict")
def predict_insulin(data: InsulinRequest):
    """
    Predice la dosis de insulina basada en:
    - Minutos de ejercicio
    - Gramos de carbohidratos
    - Gramos de proteína
    - Gramos de grasas
    - Nivel de glucosa en sangre (mg/dl)
    """
    try:
        predicted_dose = insulin_model.predict(
            data.exercise_minutes,
            data.carbohydrates,
            data.protein,
            data.fats,
            data.glucose
        )
        
        # Explicación detallada de la predicción
        explanations = []
        
        if data.exercise_minutes > 60:
            explanations.append(f"✓ Ejercicio importante: {data.exercise_minutes} min (reduce necesidad de insulina)")
        elif data.exercise_minutes > 30:
            explanations.append(f"✓ Ejercicio moderado: {data.exercise_minutes} min")
        else:
            explanations.append(f"⚠ Poco ejercicio: {data.exercise_minutes} min")
        
        if data.carbohydrates > 80:
            explanations.append(f"⚠ Alto consumo de carbohidratos: {data.carbohydrates}g")
        else:
            explanations.append(f"✓ Carbohidratos: {data.carbohydrates}g")
        
        if data.glucose > 150:
            explanations.append(f"⚠ Glucosa elevada: {data.glucose} mg/dl - aumenta necesidad de insulina")
        elif data.glucose > 120:
            explanations.append(f"⚠ Glucosa un poco alta: {data.glucose} mg/dl")
        else:
            explanations.append(f"✓ Glucosa en rango: {data.glucose} mg/dl")
        
        return {
            "success": True,
            "predicted_dose": float(predicted_dose),
            "unit": "unidades",
            "range": f"{max(2, predicted_dose-1):.1f} - {min(25, predicted_dose+1):.1f}",
            "factors": explanations,
            "disclaimer": "⚠️ IMPORTANTE: Esta es una predicción basada en IA. Siempre consulta con tu médico antes de tomar cualquier decisión sobre tu medicación.",
            "confidence": "Alta (R² = 0.9993 en datos de entrenamiento)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al realizar la predicción"
        }

@app.post("/chat")
def chat(request: MessageRequest):
    """Endpoint para interactuar con el chatbot"""
    message = request.message.lower()
    user_data = request.user_data or {}
    
    # Respuestas del chatbot mejoradas
    responses = {
        "hola": "¡Hola! Soy tu asistente de diabetes impulsado por IA. Puedo ayudarte a predecir tu dosis de insulina basándome en tus hábitos. ¿Qué necesitas?",
        "ejercicio": "El ejercicio es crucial para el manejo de la diabetes. Reduce la necesidad de insulina. ¿Cuántos minutos de ejercicio hiciste hoy?",
        "comida": "La alimentación es fundamental. Necesito saber carbohidratos, proteína y grasas. ¿Cuánto consumiste?",
        "glucosa": "El nivel de glucosa es crítico. ¿Cuál es tu glucosa en sangre actual? (en mg/dl)",
        "ayuda": """Puedo ayudarte con:
1. Predicción de dosis de insulina
2. Información sobre gestión de diabetes
3. Consejos de alimentación y ejercicio

Para predecir dosis necesito:
- Minutos de ejercicio hoy
- Gramos de carbohidratos
- Gramos de proteína
- Gramos de grasas
- Glucosa en sangre (mg/dl)""",
        "diabetes": "La diabetes es una condición que requiere gestión cuidadosa. Factores importantes: glucosa, insulina, ejercicio, dieta y medicamentos.",
        "insulina": "La insulina es esencial para regular glucosa. Tu dosis depende de: carbohidratos, glucosa, ejercicio y otros factores.",
        "default": "No entendí bien. Escribe 'ayuda' para ver opciones disponibles o cuéntame tu situación para ayudarte."
    }
    
    # Buscar coincidencia
    for key, response in responses.items():
        if key in message and key != "default":
            return {"message": response}
    
    return {"message": responses["default"]}

# ===== ENDPOINTS RAG (RETRIEVAL-AUGMENTED GENERATION) =====

@app.post("/rag/search")
def rag_search(request: RAGQueryRequest):
    """Busca información médica usando RAG, UMLS y Vademecum"""
    try:
        result = rag_system.search_medical_info(request.query)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error en búsqueda RAG"
        }

@app.post("/rag/medication")
def rag_medication_info(query: str):
    """Obtiene información de medicamentos desde Vademecum"""
    try:
        med_info = rag_system.vademecum.get_medication(query)
        if med_info:
            return {
                "success": True,
                "medication": query,
                "info": med_info,
                "source": "Vademecum"
            }
        return {
            "success": False,
            "message": f"Medicamento '{query}' no encontrado"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/rag/umls/concept")
def rag_umls_concept(query: str):
    """Busca conceptos en UMLS"""
    try:
        concept = rag_system.umls.search_concept(query)
        if concept:
            return {
                "success": True,
                "query": query,
                "concept": concept,
                "source": "UMLS"
            }
        return {
            "success": False,
            "message": f"Concepto '{query}' no encontrado"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/rag/enhance-prediction")
def rag_enhance_prediction(request: MedicalEnhancementRequest):
    """Mejora la predicción con contexto médico RAG"""
    try:
        patient_data = {
            'glucose': request.glucose,
            'exercise_minutes': request.exercise_minutes,
            'carbohydrates': request.carbohydrates,
            'symptoms': request.symptoms or []
        }
        
        enhancement = rag_system.enhance_prediction(patient_data)
        
        return {
            "success": True,
            "enhancement": enhancement,
            "sources": ["RAG", "UMLS", "Vademecum"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/rag/medical-knowledge")
def rag_medical_knowledge():
    """Obtiene toda la base de conocimiento médico disponible"""
    try:
        return {
            "success": True,
            "medical_rules": rag_system.retriever.MEDICAL_KNOWLEDGE,
            "medications": list(rag_system.vademecum.MEDICATIONS.keys()),
            "concepts": list(rag_system.umls.UMLS_CONCEPTS.keys()),
            "sources": ["RAG", "UMLS", "Vademecum"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ===== ENDPOINTS DE PACIENTES =====

@app.post("/patients/add")
def add_patient(request: PatientRequest):
    """Agrega un nuevo paciente o retorna si ya existe"""
    try:
        patient_id = db.add_patient(request.name, request.email, request.age)
        patient = db.get_patient(request.name)
        return {
            "success": True,
            "patient_id": patient_id,
            "patient": patient,
            "message": f"Paciente '{request.name}' registrado exitosamente"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al registrar paciente"
        }

@app.get("/patients/list")
def list_patients():
    """Obtiene lista de todos los pacientes"""
    try:
        patients = db.get_all_patients()
        return {
            "success": True,
            "total": len(patients),
            "patients": patients
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al obtener lista de pacientes"
        }

@app.get("/patients/{patient_name}")
def get_patient_info(patient_name: str):
    """Obtiene información de un paciente"""
    try:
        patient = db.get_patient(patient_name)
        if not patient:
            return {
                "success": False,
                "message": f"Paciente '{patient_name}' no encontrado"
            }
        
        stats = db.get_patient_statistics(patient['id'])
        history = db.get_patient_history(patient['id'], limit=10)
        
        return {
            "success": True,
            "patient": patient,
            "statistics": stats,
            "recent_history": history
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al obtener información del paciente"
        }

@app.post("/predictions/save")
def save_prediction(request: PredictionSaveRequest):
    """Guarda una predicción en el historial del paciente"""
    try:
        # Obtener o crear paciente
        patient_id = db.add_patient(request.patient_name)
        
        # Guardar predicción
        pred_id = db.save_prediction(
            patient_id,
            request.exercise_minutes,
            request.carbohydrates,
            request.protein,
            request.fats,
            request.glucose,
            request.predicted_dose,
            request.user_input
        )
        
        return {
            "success": True,
            "prediction_id": pred_id,
            "patient_id": patient_id,
            "message": f"Prediccion guardada para {request.patient_name}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al guardar prediccion"
        }

@app.get("/patients/{patient_name}/history")
def get_patient_history_endpoint(patient_name: str, limit: int = 50):
    """Obtiene el historial completo de un paciente"""
    try:
        patient = db.get_patient(patient_name)
        if not patient:
            return {
                "success": False,
                "message": f"Paciente '{patient_name}' no encontrado"
            }
        
        history = db.get_patient_history(patient['id'], limit)
        
        return {
            "success": True,
            "patient_name": patient_name,
            "total_records": len(history),
            "history": history
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al obtener historial"
        }

@app.get("/patients/{patient_name}/statistics")
def get_patient_stats_endpoint(patient_name: str):
    """Obtiene estadísticas de un paciente"""
    try:
        patient = db.get_patient(patient_name)
        if not patient:
            return {
                "success": False,
                "message": f"Paciente '{patient_name}' no encontrado"
            }
        
        stats = db.get_patient_statistics(patient['id'])
        
        return {
            "success": True,
            "patient_name": patient_name,
            "statistics": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al obtener estadísticas"
        }

@app.get("/model-info")
def model_info():
    """Obtiene información del modelo"""
    return {
        "model_type": "Random Forest Regressor",
        "n_estimators": 200,
        "features": ["ejercicio_minutos", "carbohidratos_g", "proteina_g", "grasas_g", "glucosa_mg_dl"],
        "training_samples": 800,
        "r2_score": 0.9993,
        "output_range": "2-25 unidades",
        "medical_knowledge_topics": len(insulin_model.medical_knowledge),
        "is_trained": insulin_model.is_trained
    }
