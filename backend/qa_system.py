"""
Módulo QA (Question Answering) mejorado para preguntas sobre diabetes
Integra múltiples corpus médicos y proporciona respuestas de alta calidad
"""

import pandas as pd
import os
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

# Importar corpus integrado
try:
    from corpus_integration import integrated_corpus
    CORPUS_AVAILABLE = True
except Exception as e:
    print(f"[WARN] No se pudo cargar corpus integrado: {e}")
    CORPUS_AVAILABLE = False

class DiabetesKnowledgeBase:
    """Base de conocimiento completa para diabetes"""
    
    DIABETES_KNOWLEDGE = {
        'síntomas': {
            'titulo': '📋 Síntomas de la Diabetes:',
            'contenido': [
                '• Sed excesiva (polidipsia)',
                '• Micción frecuente (poliuria)',
                '• Fatiga y debilidad extrema',
                '• Visión borrosa',
                '• Heridas que cicatrizan lentamente',
                '• Entumecimiento u hormigueo en manos/pies',
                '• Infecciones frecuentes',
                '• Irritabilidad o cambios de humor'
            ]
        },
        'tipos_diabetes': {
            'titulo': '🏥 Tipos de Diabetes:',
            'contenido': [
                '• Diabetes Tipo 1: Autoinmune, requiere insulina desde el diagnóstico',
                '• Diabetes Tipo 2: Más común, resistencia a la insulina',
                '• Diabetes Gestacional: Durante el embarazo',
                '• Prediabetes: Niveles de glucosa elevados pero no diabéticos'
            ]
        },
        'alimentos_recomendados': {
            'titulo': '✓ Alimentos Recomendados:',
            'contenido': [
                '• Verduras (brócoli, espinacas, lechuga, tomate, calabaza)',
                '• Frutas bajas en azúcar (fresas, arándanos, manzanas verdes)',
                '• Proteínas magras (pollo, pavo, pescado, huevos)',
                '• Granos integrales (avena, arroz integral, trigo)',
                '• Productos lácteos bajos en grasa (yogur natural, queso)',
                '• Legumbres (lentejas, garbanzos, frijoles)',
                '• Frutos secos sin sal (almendras, nueces)',
                '• Aceites saludables (oliva, aguacate)',
            ]
        },
        'alimentos_evitar': {
            'titulo': '✗ Alimentos a Evitar:',
            'contenido': [
                '✗ Alimentos muy azucarados (pasteles, dulces, caramelos)',
                '✗ Refrescos y bebidas azucaradas',
                '✗ Alimentos fritos (papas fritas, pollo frito)',
                '✗ Carbohidratos refinados (pan blanco, pasta blanca)',
                '✗ Jugos de frutas concentrados',
                '✗ Productos ultraprocesados',
                '✗ Alcohol en exceso',
                '✗ Sal en exceso'
            ]
        },
        'ejercicio': {
            'titulo': '🏃 Recomendaciones de Ejercicio:',
            'contenido': [
                '• 150 minutos semanales de ejercicio moderado',
                '• Caminar 30 minutos diarios',
                '• Nadar o ciclismo 2-3 veces por semana',
                '• Entrenamiento de fuerza 2 veces por semana',
                '• Yoga o estiramientos diarios',
                '• Evitar ejercicio intenso sin monitoreo de glucosa',
                '• Revisar glucosa antes y después de ejercitar',
                '• Llevar carbohidratos rápidos durante ejercicio prolongado'
            ]
        },
        'monitoreo': {
            'titulo': '📊 Monitoreo de Glucosa:',
            'contenido': [
                '• Rango normal en ayunas: 70-100 mg/dL',
                '• Rango normal después de comer: < 140 mg/dL',
                '• Hipoglucemia: < 70 mg/dL',
                '• Hiperglucemia: > 200 mg/dL',
                '• Monitorear 2-4 veces diarias (pacientes con insulina)',
                '• HbA1c objetivo: < 7% (si es posible)',
                '• Llevar registro de lecturas',
                '• Revisar glucosa ante síntomas de hipo o hiperglucemia'
            ]
        },
        'complicaciones': {
            'titulo': '⚠️ Complicaciones de la Diabetes:',
            'contenido': [
                '• Nefropatía diabética (daño renal)',
                '• Retinopatía diabética (daño ocular)',
                '• Neuropatía diabética (daño nervioso)',
                '• Enfermedad cardiovascular',
                '• Pie diabético (úlceras, infecciones)',
                '• Cetoacidosis diabética (emergencia)',
                '• Síndrome hiperosmolar (emergencia)',
                '• Hipoglucemia severa'
            ]
        },
        'medicamentos': {
            'titulo': '💊 Medicamentos Comunes:',
            'contenido': [
                '• Insulina: Se inyecta, actúa rápidamente',
                '• Metformina: Primera línea para tipo 2',
                '• Sulfonilureas: Estimulan producción de insulina',
                '• Inhibidores DPP-4: Aumentan GLP-1',
                '• Agonistas GLP-1: Mejoran control glucémico',
                '• Inhibidores SGLT2: Reducen glucosa en orina',
                '• Tiazolidindionas: Mejoran sensibilidad a insulina',
                '• Acarbosa: Ralentiza absorción de carbohidratos'
            ]
        },
        'insulina': {
            'titulo': '💉 Tipos de Insulina:',
            'contenido': [
                '• Insulina Rápida: Actúa en 10-15 minutos',
                '• Insulina Corta: Actúa en 30 minutos',
                '• Insulina Intermedia: Actúa en 2-4 horas',
                '• Insulina Larga: Cubre 24 horas',
                '• Mezclas de insulina: Combinan rápida + intermedia',
                '• Bombas de insulina: Infusión continua',
                '• Regla de los 500: 500 ÷ dosis diaria = gramos por unidad',
                '• Ajustar según glucosa y comidas'
            ]
        },
        'hipoglucemia': {
            'titulo': '🚨 Hipoglucemia (Glucosa Baja):',
            'contenido': [
                '• Síntomas: Temblores, sudoración, confusión, ansiedad',
                '• Glucosa < 70 mg/dL',
                '• Tratamiento inmediato: 15g carbohidratos simples',
                '• Usar: Jugo, gaseosa, caramelos, miel',
                '• Esperar 15 minutos y revalorar',
                '• Si no mejora: Glucagón inyectable',
                '• Llamar emergencia si no responde',
                '• Llevar glucagón y identificación médica'
            ]
        },
        'hiperglucemia': {
            'titulo': '⚡ Hiperglucemia (Glucosa Alta):',
            'contenido': [
                '• Síntomas: Sed, micción frecuente, fatiga, visión borrosa',
                '• Glucosa > 200 mg/dL',
                '• Causas: Poco medicamento, comida, estrés, infección',
                '• Tratamiento: Aumentar actividad física, agua, revisión médica',
                '• Verificar cetonas si glucosa > 250 mg/dL',
                '• Si hay cetosis: Acudir a emergencia',
                '• Ajustar medicamentos con médico',
                '• Revisar técnica de inyección'
            ]
        },
        'nutricion': {
            'titulo': '🍎 Guía de Nutrición:',
            'contenido': [
                '• Distribuir comidas cada 3-4 horas',
                '• Incluir proteína en cada comida',
                '• Carbohidratos complejos: arroz integral, avena',
                '• Grasas saludables: aguacate, oliva, frutos secos',
                '• Fibra: ayuda a controlar glucosa y peso',
                '• Limitar sodio a < 2300 mg/día',
                '• Beber 2-3 litros de agua diarios',
                '• Evitar ayunar'
            ]
        },
        'estilo_vida': {
            'titulo': '🌟 Cambios en Estilo de Vida:',
            'contenido': [
                '• Dormir 7-9 horas diarias',
                '• Reducir estrés (meditación, yoga)',
                '• Dejar de fumar',
                '• Limitar alcohol',
                '• Mantener peso saludable',
                '• Revisiones médicas cada 3-6 meses',
                '• Educación continua sobre diabetes',
                '• Apoyo familiar y grupos de apoyo'
            ]
        },
        'embarazo': {
            'titulo': '🤰 Diabetes y Embarazo:',
            'contenido': [
                '• Mayor riesgo de complicaciones',
                '• Control glucémico más estricto',
                '• Revisiones más frecuentes',
                '• Algunos medicamentos no son seguros',
                '• Insulina es primera línea en embarazo',
                '• Monitoreo fetal importante',
                '• Riesgo de diabetes gestacional',
                '• Planificación previa al embarazo recomendada'
            ]
        },
        'viajes': {
            'titulo': '✈️ Diabetes y Viajes:',
            'contenido': [
                '• Llevar documentación médica',
                '• Duplicar medicinas en equipaje de mano',
                '• Mantener insulina refrigerada',
                '• Ajustar horarios de medicamentos',
                '• Llevar carbohidratos rápidos de emergencia',
                '• Informar sobre cambios de zona horaria',
                '• Usar cinturones de identificación médica',
                '• Tener números de emergencia'
            ]
        }
    }
    
    def __init__(self):
        self.general_data = None
        self.medical_data = None
        self.load_data()
        
    def load_data(self):
        """Carga los CSV de datos médicos"""
        data_dir = 'data'
        
        try:
            general_path = os.path.join(data_dir, 'data_general.csv')
            if os.path.exists(general_path):
                self.general_data = pd.read_csv(general_path)
                print(f"[OK] Datos generales cargados: {len(self.general_data)} registros")
            
            medical_path = os.path.join(data_dir, 'data_medical.csv')
            if os.path.exists(medical_path):
                self.medical_data = pd.read_csv(medical_path)
                print(f"[OK] Datos médicos cargados: {len(self.medical_data)} registros")
        except Exception as e:
            print(f"[WARN] Error cargando datos: {e}")
    
    def search_answer(self, query: str, threshold: float = 0.4) -> Dict:
        """Busca respuesta completa a una pregunta sobre diabetes"""
        query_lower = query.lower()
        best_answer = None
        best_source = 'unknown'
        best_score = 0.0
        
        # Estrategia 0: Detectar tipo de pregunta en base de conocimiento local
        for topic, info in self.DIABETES_KNOWLEDGE.items():
            keywords = topic.split('_')
            if any(keyword in query_lower for keyword in keywords):
                best_answer = self._format_answer(info)
                best_source = 'builtin_local'
                best_score = 0.95
                break
        
        if best_answer and best_source == 'builtin_local':
            return {
                'found': True,
                'answer': best_answer,
                'confidence': best_score,
                'source': best_source,
                'question_type': 'diabetes'
            }
        
        # Estrategia 1: Buscar en corpus integrado
        if CORPUS_AVAILABLE and best_score < 0.8:
            corpus_results = integrated_corpus.search(query, threshold=threshold, top_k=3)
            
            if corpus_results:
                best_result = corpus_results[0]
                best_answer = best_result['answer']
                best_source = f"corpus_{best_result['source']}"
                best_score = best_result['similarity']
        
        # Estrategia 2: Búsqueda en datos generales por similitud
        if self.general_data is not None and best_score < 0.8:
            for idx, row in self.general_data.iterrows():
                try:
                    question = str(row.get('short_question', '')).lower()
                    if not question:
                        continue
                    
                    similarity = SequenceMatcher(None, query_lower, question).ratio()
                    
                    if similarity > best_score and similarity > threshold:
                        best_score = similarity
                        best_answer = row.get('short_answer', '')
                        best_source = 'general_csv'
                except:
                    pass
        
        # Estrategia 3: Búsqueda por palabras clave en tags
        if best_score < 0.6 and self.general_data is not None:
            diabetes_keywords = ['diabetes', 'glucosa', 'insulina', 'azúcar', 'alimento', 
                               'comida', 'ejercicio', 'síntoma', 'medicamento', 'dieta']
            
            for keyword in diabetes_keywords:
                if keyword in query_lower:
                    for idx, row in self.general_data.iterrows():
                        try:
                            tags = str(row.get('tags', '')).lower()
                            if keyword in tags:
                                best_answer = row.get('short_answer', '')
                                best_source = 'general_tags'
                                best_score = 0.75
                                break
                        except:
                            pass
                    if best_answer:
                        break
        
        # Estrategia 4: Buscar en datos médicos
        if self.medical_data is not None and best_score < 0.7:
            for idx, row in self.medical_data.iterrows():
                try:
                    question = str(row.get('input', '')).lower()
                    if not question:
                        continue
                    
                    similarity = SequenceMatcher(None, query_lower, question).ratio()
                    
                    if similarity > best_score and similarity > threshold:
                        best_score = similarity
                        best_answer = row.get('output', '')
                        best_source = 'medical_csv'
                except:
                    pass
        
        # Respuesta por defecto si no encuentra nada
        if not best_answer:
            best_answer = (
                'No tengo información específica sobre eso. '
                'Por favor, consulta con tu médico o endocrinólogo para una respuesta más precisa. '
                'Puedo ayudarte con preguntas sobre síntomas, alimentos, ejercicio, medicamentos, etc.'
            )
            best_score = 0.3
            best_source = 'default'
        
        return {
            'found': best_answer is not None,
            'answer': best_answer,
            'confidence': round(best_score, 2),
            'source': best_source,
            'question_type': 'diabetes'
        }
    
    def _format_answer(self, info_dict: Dict) -> str:
        """Formatea la respuesta con título y contenido"""
        titulo = info_dict.get('titulo', '')
        contenido = '\n'.join(info_dict.get('contenido', []))
        return f"{titulo}\n{contenido}"
    
    def get_related_topics(self, query: str) -> List[str]:
        """Obtiene tópicos relacionados a una pregunta"""
        query_lower = query.lower()
        related = []
        
        for topic in self.DIABETES_KNOWLEDGE.keys():
            keywords = topic.split('_')
            # Si la consulta menciona keywords relacionados, agregar tópicos relacionados
            if any(kw in query_lower for kw in keywords):
                # Agregar tópicos relacionados pero no el mismo
                for other_topic in self.DIABETES_KNOWLEDGE.keys():
                    if other_topic != topic and other_topic not in related:
                        related.append(other_topic)
        
        return related[:3]  # Retornar máximo 3 tópicos relacionados

# Instancia global del sistema QA
knowledge_base = DiabetesKnowledgeBase()

if __name__ == '__main__':
    # Test del sistema QA
    test_queries = [
        'qué síntomas tiene la diabetes',
        'qué alimentos puedo comer',
        'cuánto ejercicio debo hacer',
        'qué es la hipoglucemia',
        'cómo tratar la hiperglucemia',
        'cuál es el rango normal de glucosa',
        'qué medicamentos existen',
        'tipos de insulina',
    ]
    
    for q in test_queries:
        result = knowledge_base.search_answer(q)
        print(f"\n{'='*60}")
        print(f"Pregunta: {q}")
        print(f"Confianza: {result['confidence']:.0%}")
        print(f"Fuente: {result['source']}")
        print(f"Respuesta:\n{result['answer'][:300]}")
