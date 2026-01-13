"""
Módulo QA (Question Answering) para responder preguntas generales
sobre diabetes, alimentación, ejercicio y síntomas
"""

import pandas as pd
import os
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

class DiabetesKnowledgeBase:
    """Base de conocimiento para preguntas generales sobre diabetes"""
    
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
    
    def search_answer(self, query: str, threshold: float = 0.5) -> Dict:
        """
        Busca respuesta a una pregunta en los datos
        
        Busca por similitud en preguntas-respuestas existentes
        """
        query_lower = query.lower()
        best_match = None
        best_score = 0
        best_answer = None
        best_source = None
        
        # Estrategia 0: Detectar tipo de pregunta y usar información builtin
        if any(word in query_lower for word in ['síntoma', 'señal', 'signo', 'presentar']):
            best_answer = self.get_diabetes_info('síntomas')
            best_source = 'builtin'
            best_score = 0.9
        elif any(word in query_lower for word in ['alimento', 'comida', 'comer', 'puedo']) and \
             any(word in query_lower for word in ['qué', 'cuál', 'puedo', 'debo', 'evitar', 'recomend']):
            if 'evitar' in query_lower or 'no' in query_lower:
                best_answer = self.get_diabetes_info('alimentos_a_evitar')
            else:
                best_answer = self.get_diabetes_info('alimentos_recomendados')
            best_source = 'builtin'
            best_score = 0.9
        elif any(word in query_lower for word in ['ejercicio', 'deporte', 'actividad', 'física', 'entrenar']):
            best_answer = self.get_diabetes_info('ejercicio')
            best_source = 'builtin'
            best_score = 0.9
        
        # Si ya encontró con source builtin, retornar
        if best_answer and best_source == 'builtin':
            return {
                'found': True,
                'answer': best_answer,
                'confidence': best_score,
                'source': best_source
            }
        
        # Estrategia 1: Buscar en datos generales
        if self.general_data is not None:
            for idx, row in self.general_data.iterrows():
                question = str(row['short_question']).lower()
                
                # Similitud simple por palabras clave
                similarity = SequenceMatcher(None, query_lower, question).ratio()
                
                if similarity > best_score and similarity > threshold:
                    best_score = similarity
                    best_match = question
                    best_answer = row['short_answer']
                    best_source = 'general'
        
        # Estrategia 2: Buscar por tags (palabras clave)
        if best_score < 0.3 and self.general_data is not None:
            keywords = ['diabetes', 'alimento', 'comida', 'ejercicio', 'síntoma', 'síntomas',
                       'glucosa', 'azúcar', 'insulina', 'dieta', 'fruit', 'food', 'exercise']
            
            for keyword in keywords:
                if keyword in query_lower:
                    # Buscar en tags
                    for idx, row in self.general_data.iterrows():
                        try:
                            tags = str(row['tags']).lower()
                            if keyword in tags:
                                best_answer = row['short_answer']
                                best_source = 'tags'
                                best_score = 0.6
                                break
                        except:
                            pass
                    if best_answer:
                        break
        
        # Estrategia 3: Buscar en datos médicos
        if best_score < 0.4 and self.medical_data is not None:
            for idx, row in self.medical_data.iterrows():
                question = str(row['input']).lower()
                
                similarity = SequenceMatcher(None, query_lower, question).ratio()
                
                if similarity > best_score and similarity > threshold:
                    best_score = similarity
                    best_match = question
                    best_answer = row['output']
                    best_source = 'medical'
        
        return {
            'found': best_answer is not None,
            'answer': best_answer if best_answer else 'No encontré información sobre esto.',
            'confidence': best_score,
            'source': best_source
        }
    
    def get_diabetes_info(self, topic: str) -> str:
        """Obtiene información específica sobre tópicos de diabetes"""
        
        info_base = {
            'síntomas': [
                '• Sed excesiva',
                '• Micción frecuente',
                '• Fatiga',
                '• Visión borrosa',
                '• Heridas que cicatrizan lentamente',
                '• Entumecimiento en manos/pies',
            ],
            'alimentos_recomendados': [
                '✓ Verduras (brócoli, lechuga, tomate)',
                '✓ Frutas bajas en azúcar (fresas, manzanas)',
                '✓ Proteínas magras (pollo, pescado)',
                '✓ Granos integrales (avena)',
                '✓ Lácteos bajos en grasa',
            ],
            'alimentos_a_evitar': [
                '✗ Alimentos muy azucarados (pasteles, caramelos)',
                '✗ Refrescos azucarados',
                '✗ Alimentos fritos',
                '✗ Carbohidratos refinados',
                '✗ Jugos de frutas concentrados',
            ],
            'ejercicio': [
                '• 150 minutos de actividad moderada por semana',
                '• Caminar 30 minutos diarios',
                '• Natación, ciclismo, trote',
                '• Ejercicios de fuerza 2-3 veces/semana',
                '• Evitar periodos largos sedentario',
            ],
        }
        
        topic_lower = topic.lower()
        
        # Buscar match
        for key in info_base.keys():
            if key.split('_')[0] in topic_lower:
                return '\n'.join(info_base[key])
        
        return "Tema no encontrado. Pregunta sobre: síntomas, alimentos_recomendados, alimentos_a_evitar, ejercicio"

# Instancia global
knowledge_base = DiabetesKnowledgeBase()

if __name__ == '__main__':
    # Test
    queries = [
        'qué síntomas tiene la diabetes',
        'qué alimentos puedo comer',
        'cuánto ejercicio debo hacer',
    ]
    
    for q in queries:
        result = knowledge_base.search_answer(q)
        print(f"\nPregunta: {q}")
        print(f"Respuesta: {result['answer'][:200]}...")
        print(f"Confianza: {result['confidence']:.2%}")
