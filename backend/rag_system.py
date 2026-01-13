"""
Módulo RAG (Retrieval-Augmented Generation) para búsqueda de información médica
Integra UMLS y Vademecum para proporcionar información más precisa
"""

import json
import os
from typing import List, Dict, Tuple
from datetime import datetime

class VademecumDatabase:
    """Base de datos de medicamentos y tratamientos"""
    
    MEDICATIONS = {
        # Insulinas
        'insulina humana': {
            'type': 'Insulina',
            'brands': ['Humulin', 'Actrapid'],
            'onset': '30 min',
            'peak': '2-4 horas',
            'duration': '8-12 horas',
            'indications': ['Diabetes tipo 1', 'Diabetes tipo 2'],
            'side_effects': ['Hipoglucemia', 'Alergia local'],
            'contraindications': ['Hipoglucemia activa']
        },
        'insulina rapida': {
            'type': 'Insulina Rápida',
            'brands': ['Humalog', 'NovoLog'],
            'onset': '10-15 min',
            'peak': '1-2 horas',
            'duration': '4-6 horas',
            'indications': ['Diabetes tipo 1', 'Diabetes tipo 2'],
            'side_effects': ['Hipoglucemia', 'Alergia']
        },
        'insulina lenta': {
            'type': 'Insulina Basal',
            'brands': ['Lantus', 'Levemir'],
            'onset': '2-4 horas',
            'peak': '6-12 horas',
            'duration': '20-24 horas',
            'indications': ['Diabetes tipo 1', 'Diabetes tipo 2']
        },
        # Antidiabéticos orales
        'metformina': {
            'type': 'Biguanida',
            'brands': ['Glucophage', 'Diabex'],
            'indications': ['Diabetes tipo 2', 'Prediabetes'],
            'mechanism': 'Reduce gluconeogénesis hepática',
            'side_effects': ['Acidosis láctica', 'Diarrea', 'Náuseas'],
            'max_dose': '2550 mg/día'
        },
        'glibenclamida': {
            'type': 'Sulfonilurea',
            'brands': ['Daonil', 'Euglucon'],
            'indications': ['Diabetes tipo 2'],
            'mechanism': 'Estimula liberación de insulina',
            'side_effects': ['Hipoglucemia', 'Ganancia de peso']
        },
        'sitagliptina': {
            'type': 'Inhibidor DPP-4',
            'brands': ['Januvia'],
            'indications': ['Diabetes tipo 2'],
            'mechanism': 'Incrementa GLP-1',
            'side_effects': ['Infección respiratoria']
        }
    }
    
    DIETARY_CARBS = {
        'arroz': 45,
        'pan': 15,
        'pasta': 40,
        'papa': 20,
        'platano': 27,
        'manzana': 25,
        'naranja': 15,
        'pastel': 45,
        'galleta': 15,
        'avena': 50,
        'leche': 12,
        'yogur': 15
    }
    
    @classmethod
    def get_medication(cls, med_name: str) -> Dict:
        """Obtiene información de un medicamento"""
        med_name_lower = med_name.lower()
        for med, info in cls.MEDICATIONS.items():
            if med in med_name_lower or any(brand.lower() in med_name_lower for brand in info.get('brands', [])):
                return info
        return None
    
    @classmethod
    def get_carb_info(cls, food_name: str) -> int:
        """Obtiene información de carbohidratos de un alimento"""
        return cls.DIETARY_CARBS.get(food_name.lower(), 0)

class UMLSIntegration:
    """Integración con UMLS (Unified Medical Language System)"""
    
    UMLS_CONCEPTS = {
        'hyperglycemia': {
            'cui': 'C0020456',
            'definition': 'Nivel alto de glucosa en sangre',
            'symptoms': ['Polidipsia', 'Poliuria', 'Fatiga'],
            'causes': ['Diabetes', 'Infecciones', 'Estrés']
        },
        'hypoglycemia': {
            'cui': 'C0020615',
            'definition': 'Nivel bajo de glucosa en sangre',
            'symptoms': ['Temblores', 'Sudoración', 'Confusión'],
            'treatment': ['Glucosa rápida', 'Glucagón']
        },
        'diabetic_ketoacidosis': {
            'cui': 'C0011847',
            'definition': 'Complicación grave de diabetes con cetosis',
            'symptoms': ['Respiración rápida', 'Aliento a frutas', 'Náuseas'],
            'emergency': True
        },
        'insulin_resistance': {
            'cui': 'C0021655',
            'definition': 'Reducida respuesta a insulina',
            'risk_factors': ['Obesidad', 'Sedentarismo', 'Genética']
        }
    }
    
    @classmethod
    def search_concept(cls, query: str) -> Dict:
        """Busca conceptos UMLS"""
        query_lower = query.lower()
        for concept, data in cls.UMLS_CONCEPTS.items():
            if concept in query_lower or query_lower in concept:
                return data
        return None
    
    @classmethod
    def get_related_concepts(cls, concept: str) -> List[str]:
        """Obtiene conceptos relacionados"""
        if concept.lower() in cls.UMLS_CONCEPTS:
            return list(cls.UMLS_CONCEPTS.keys())
        return []

class RAGRetriever:
    """Sistema RAG para recuperar información médica relevante"""
    
    MEDICAL_KNOWLEDGE = {
        'carbohidratos_insulina': {
            'rule': 'Por cada 10g de carbohidratos se necesita ~1 unidad de insulina rápida',
            'source': 'Endocrinología clínica',
            'confidence': 0.85
        },
        'ejercicio_glucosa': {
            'rule': 'El ejercicio reduce glucosa: 30 min = ~30-50 mg/dL',
            'source': 'Fisiología del ejercicio en diabetes',
            'confidence': 0.80
        },
        'glucosa_optima': {
            'rule': 'Rango óptimo en ayunas: 80-130 mg/dL',
            'source': 'American Diabetes Association',
            'confidence': 0.90
        },
        'insulina_basal': {
            'rule': 'Insulina basal debe cubrir gluconeogénesis hepática: ~50% del total diario',
            'source': 'Guías de insulinización',
            'confidence': 0.85
        },
        'hipoglucemia_sintomas': {
            'rule': 'Glucosa < 70 mg/dL: temblores, sudoración, confusión',
            'source': 'Endocrinología',
            'confidence': 0.95
        }
    }
    
    @classmethod
    def retrieve_relevant_info(cls, query: str) -> List[Tuple[str, Dict]]:
        """Recupera información relevante basada en la consulta"""
        results = []
        query_lower = query.lower()
        
        for topic, info in cls.MEDICAL_KNOWLEDGE.items():
            # Búsqueda simple por palabras clave
            if any(keyword in query_lower for keyword in topic.split('_')):
                results.append((topic, info))
        
        # Ordenar por confianza
        results.sort(key=lambda x: x[1].get('confidence', 0), reverse=True)
        return results
    
    @classmethod
    def generate_medical_context(cls, patient_glucose: float, exercise: float, carbs: float) -> str:
        """Genera contexto médico basado en los datos del paciente"""
        context = []
        
        # Análisis de glucosa
        if patient_glucose > 150:
            context.append("Glucosa elevada: Se recomienda aumentar actividad física y revisar medicación")
        elif patient_glucose < 80:
            context.append("Glucosa baja: Riesgo de hipoglucemia. Tomar carbohidratos rápidos")
        else:
            context.append("Glucosa en rango óptimo")
        
        # Análisis de ejercicio
        if exercise > 60:
            context.append("Ejercicio intenso: Puede causar hipoglucemia tardía. Monitorear")
        elif exercise < 10:
            context.append("Poco ejercicio: Considerar aumentar actividad física")
        
        # Análisis de carbohidratos
        if carbs > 100:
            context.append("Alto consumo de carbohidratos: Requiere mayor dosis de insulina")
        elif carbs == 0:
            context.append("Sin carbohidratos detectados")
        
        return "\n".join(context)
    
    @classmethod
    def get_medication_recommendations(cls, glucose: float, exercise: float, carbs: float) -> List[str]:
        """Obtiene recomendaciones de medicamentos basadas en datos del paciente"""
        recommendations = []
        
        # Basar en la consulta para vademecum
        if glucose > 200:
            recommendations.append("Considerar insulina rápida adicional")
            recommendations.append("Revisar con endocrinólogo")
        
        if glucose < 80 and exercise > 30:
            recommendations.append("Riesgo de hipoglucemia post-ejercicio")
            recommendations.append("Consumir carbohidratos después del ejercicio")
        
        if carbs > 80:
            recommendations.append("Tomar metformina si no la usa (reducción de absorción)")
        
        return recommendations

class RAGSystem:
    """Sistema completo de RAG integrando UMLS y Vademecum"""
    
    def __init__(self):
        self.retriever = RAGRetriever()
        self.umls = UMLSIntegration()
        self.vademecum = VademecumDatabase()
    
    def search_medical_info(self, query: str) -> Dict:
        """Busca información médica completa"""
        result = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'sources': []
        }
        
        # Búsqueda en RAG
        rag_results = self.retriever.retrieve_relevant_info(query)
        result['rag_results'] = [{'topic': topic, 'info': info} for topic, info in rag_results]
        
        # Búsqueda en UMLS
        umls_result = self.umls.search_concept(query)
        if umls_result:
            result['umls_concept'] = umls_result
            result['sources'].append('UMLS')
        
        # Búsqueda en Vademecum
        med_info = self.vademecum.get_medication(query)
        if med_info:
            result['medication'] = med_info
            result['sources'].append('Vademecum')
        
        return result
    
    def enhance_prediction(self, patient_data: Dict) -> Dict:
        """Mejora la predicción con información RAG"""
        enhancement = {
            'medical_context': self.retriever.generate_medical_context(
                patient_data.get('glucose', 0),
                patient_data.get('exercise_minutes', 0),
                patient_data.get('carbohydrates', 0)
            ),
            'recommendations': self.retriever.get_medication_recommendations(
                patient_data.get('glucose', 0),
                patient_data.get('exercise_minutes', 0),
                patient_data.get('carbohydrates', 0)
            ),
            'related_concepts': []
        }
        
        # Buscar conceptos relacionados si hay síntomas
        if patient_data.get('symptoms'):
            for symptom in patient_data['symptoms']:
                related = self.umls.get_related_concepts(symptom)
                enhancement['related_concepts'].extend(related)
        
        return enhancement

# Instancia global
rag_system = RAGSystem()
