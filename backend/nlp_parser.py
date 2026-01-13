"""
Módulo NLP para interpretar descripciones de alimentos y ejercicio
Convierte lenguaje natural a valores numéricos
"""

import re
from typing import Dict, Tuple
from difflib import SequenceMatcher

import re
from typing import Dict, Tuple
from difflib import SequenceMatcher

class SpellingCorrector:
    """Corrige errores ortográficos comunes y jerga en descripciones médicas"""
    
    # Diccionario de palabras mal escritas comunes
    SPELLING_CORRECTIONS = {
        # Errores de "horas"
        'hiras': 'horas',
        'oras': 'horas',
        'hora': 'horas',
        'hors': 'horas',
        'joras': 'horas',
        
        # Errores de "ejercicio"
        'egercicios': 'ejercicios',
        'ejercicio': 'ejercicios',
        'ejecicio': 'ejercicio',
        'ejercisios': 'ejercicios',
        'ejerciios': 'ejercicios',
        'excersio': 'ejercicio',
        
        # Errores de "glucosa"
        'glucoза': 'glucosa',
        'glucoza': 'glucosa',
        'glucosa': 'glucosa',
        
        # Errores de "comida"
        'comidas': 'comida',
        'comí': 'comida',
        'comimos': 'comida',
        'comiste': 'comida',
        
        # Errores de "carbohidratos"
        'carbohidratos': 'carbohidratos',
        'carbs': 'carbohidratos',
        'carboitratos': 'carbohidratos',
        'carboidratos': 'carbohidratos',
    }
    
    # Diccionario de jerga y variantes informales
    SLANG_CORRECTIONS = {
        # Variantes de ejercicio
        'traba': 'trabajo',
        'labur': 'trabajo',
        'laburo': 'trabajo',
        'chamb': 'trabajo',
        'curro': 'trabajo',
        'entreno': 'entrenamiento',
        'entreni': 'entrenamiento',
        
        # Variantes de tiempo
        'rato': 'tiempo',
        'momentico': 'poco tiempo',
        'ratito': 'poco tiempo',
        'un toquecito': 'poco tiempo',
        
        # Variantes de comida
        'merienda': 'comida ligera',
        'tentempié': 'comida ligera',
        'picadita': 'comida ligera',
        'golosina': 'dulce',
        'caramelo': 'dulce',
        'chucherías': 'dulce',
        
        # Intensidad
        'chamba': 'trabajo',
        'quilombo': 'ejercicio intenso',
        'madrugar': 'mañana temprano',
        'pajizo': 'poco esfuerzo',
        'mandador': 'trabajo pesado',
    }
    
    # Números mal escritos
    NUMBER_CORRECTIONS = {
        'dos': '2',
        'tres': '3',
        'cuatro': '4',
        'cinco': '5',
        'seis': '6',
        'siete': '7',
        'ocho': '8',
        'nueve': '9',
        'diez': '10',
        'once': '11',
        'doce': '12',
        'quince': '15',
        'veinte': '20',
        'treinta': '30',
        'cuarenta': '40',
        'cincuenta': '50',
        'sesenta': '60',
    }
    
    @classmethod
    def find_similar_word(cls, word: str, dictionary: Dict, threshold=0.75) -> str:
        """
        Encuentra la palabra más similar en un diccionario usando SequenceMatcher
        threshold: 0-1, qué tan similar debe ser (0.75 = 75% similitud)
        """
        word_lower = word.lower().strip()
        best_match = word_lower
        best_score = 0
        
        for key in dictionary.keys():
            ratio = SequenceMatcher(None, word_lower, key).ratio()
            if ratio > best_score and ratio > threshold:
                best_score = ratio
                best_match = key
        
        return best_match if best_score > threshold else word_lower
    
    @classmethod
    def correct_text(cls, text: str) -> Tuple[str, Dict]:
        """
        Corrige el texto de entrada y retorna (texto_corregido, correcciones_realizadas)
        """
        corrected_text = text.lower()
        corrections = {
            'spelling': [],
            'slang': [],
            'numbers': [],
            'original': text
        }
        
        # Procesar palabra por palabra
        words = corrected_text.split()
        corrected_words = []
        
        for word in words:
            # Limpiar puntuación
            word_clean = re.sub(r'[^\w]', '', word)
            word_with_punct = re.sub(r'[^\w]', '', word)
            
            original_word = word_clean
            corrected_word = word_clean
            correction_type = None
            
            # 1. Verificar números en texto
            if word_clean in cls.NUMBER_CORRECTIONS:
                corrected_word = cls.NUMBER_CORRECTIONS[word_clean]
                correction_type = 'number'
            
            # 2. Verificar errores de ortografía
            elif word_clean in cls.SPELLING_CORRECTIONS:
                corrected_word = cls.SPELLING_CORRECTIONS[word_clean]
                correction_type = 'spelling'
            
            # 3. Verificar jerga
            elif word_clean in cls.SLANG_CORRECTIONS:
                corrected_word = cls.SLANG_CORRECTIONS[word_clean]
                correction_type = 'slang'
            
            # 4. Búsqueda fuzzy para palabras similares (si no hay match exacto)
            else:
                similar_spelling = cls.find_similar_word(word_clean, cls.SPELLING_CORRECTIONS, threshold=0.78)
                if similar_spelling != word_clean:
                    corrected_word = cls.SPELLING_CORRECTIONS[similar_spelling]
                    correction_type = 'spelling'
                else:
                    similar_slang = cls.find_similar_word(word_clean, cls.SLANG_CORRECTIONS, threshold=0.75)
                    if similar_slang != word_clean:
                        corrected_word = cls.SLANG_CORRECTIONS[similar_slang]
                        correction_type = 'slang'
            
            # Registrar correcciones realizadas
            if correction_type and original_word != corrected_word:
                if correction_type == 'spelling':
                    corrections['spelling'].append(f"{original_word} → {corrected_word}")
                elif correction_type == 'slang':
                    corrections['slang'].append(f"{original_word} → {corrected_word}")
                elif correction_type == 'number':
                    corrections['numbers'].append(f"{original_word} → {corrected_word}")
            
            corrected_words.append(corrected_word)
        
        corrected_text = ' '.join(corrected_words)
        
        return corrected_text, corrections

class FoodParser:
    """Parsea descripciones de comida a carbohidratos"""
    
    # Base de datos de alimentos comunes con carbohidratos por porción
    FOODS_DATABASE = {
        # Granos y carbohidratos
        'arroz': {'carbs': 45, 'protein': 4, 'fats': 0.5, 'unit': 'taza'},
        'pan': {'carbs': 15, 'protein': 3, 'fats': 1, 'unit': 'rebanada'},
        'pasta': {'carbs': 40, 'protein': 8, 'fats': 1, 'unit': 'taza'},
        'papa': {'carbs': 20, 'protein': 2, 'fats': 0, 'unit': 'mediana'},
        'tortilla': {'carbs': 15, 'protein': 3, 'fats': 1.5, 'unit': 'pieza'},
        'platano': {'carbs': 27, 'protein': 1, 'fats': 0.3, 'unit': 'mediano'},
        'mazorca': {'carbs': 17, 'protein': 3, 'fats': 1, 'unit': 'pieza'},
        
        # Frutas
        'manzana': {'carbs': 25, 'protein': 0.5, 'fats': 0.3, 'unit': 'mediana'},
        'naranja': {'carbs': 15, 'protein': 1, 'fats': 0.3, 'unit': 'mediana'},
        'platano': {'carbs': 27, 'protein': 1, 'fats': 0.3, 'unit': 'mediano'},
        'uva': {'carbs': 27, 'protein': 0.9, 'fats': 0.3, 'unit': 'taza'},
        'sandia': {'carbs': 11, 'protein': 0.6, 'fats': 0.3, 'unit': 'taza'},
        'fresa': {'carbs': 11, 'protein': 1, 'fats': 0.3, 'unit': 'taza'},
        
        # Proteínas
        'pollo': {'carbs': 0, 'protein': 26, 'fats': 3.5, 'unit': '100g'},
        'carne': {'carbs': 0, 'protein': 26, 'fats': 11, 'unit': '100g'},
        'pescado': {'carbs': 0, 'protein': 25, 'fats': 1.5, 'unit': '100g'},
        'huevo': {'carbs': 0.6, 'protein': 6, 'fats': 5, 'unit': 'pieza'},
        'leche': {'carbs': 12, 'protein': 8, 'fats': 7.5, 'unit': 'taza'},
        'queso': {'carbs': 0.7, 'protein': 7, 'fats': 9, 'unit': '30g'},
        
        # Verduras (bajo carb)
        'broccoli': {'carbs': 7, 'protein': 2.8, 'fats': 0.4, 'unit': 'taza'},
        'zanahoria': {'carbs': 12, 'protein': 0.9, 'fats': 0.2, 'unit': 'mediana'},
        'lechuga': {'carbs': 1, 'protein': 0.6, 'fats': 0.1, 'unit': 'taza'},
        'tomate': {'carbs': 5, 'protein': 0.9, 'fats': 0.2, 'unit': 'mediano'},
        
        # Papas y preparaciones
        'papas fritas': {'carbs': 35, 'protein': 3, 'fats': 15, 'unit': 'porcion'},
        'papas': {'carbs': 20, 'protein': 2, 'fats': 0, 'unit': 'mediana'},
        'papas al horno': {'carbs': 25, 'protein': 3, 'fats': 1, 'unit': 'porcion'},
        'papas cocidas': {'carbs': 20, 'protein': 2, 'fats': 0.1, 'unit': 'porcion'},
        
        # Bebidas/Postres
        'jugo': {'carbs': 30, 'protein': 0, 'fats': 0, 'unit': 'vaso'},
        'soda': {'carbs': 39, 'protein': 0, 'fats': 0, 'unit': 'lata'},
        'cerveza': {'carbs': 13, 'protein': 0.6, 'fats': 0, 'unit': 'vaso'},
        'pastel': {'carbs': 45, 'protein': 3, 'fats': 15, 'unit': 'porcion'},
        'cake': {'carbs': 45, 'protein': 3, 'fats': 15, 'unit': 'porcion'},
        'postre': {'carbs': 40, 'protein': 3, 'fats': 8, 'unit': 'porcion'},
        'dulce': {'carbs': 25, 'protein': 0, 'fats': 5, 'unit': 'porcion'},
        'chocolate': {'carbs': 10, 'protein': 1.5, 'fats': 9, 'unit': 'onza'},
        'galleta': {'carbs': 15, 'protein': 2, 'fats': 5, 'unit': 'pieza'},
        'donas': {'carbs': 20, 'protein': 2, 'fats': 10, 'unit': 'pieza'},
        'dona': {'carbs': 20, 'protein': 2, 'fats': 10, 'unit': 'pieza'},
        'helado': {'carbs': 20, 'protein': 3, 'fats': 10, 'unit': 'porcion'},
        'arroz con leche': {'carbs': 35, 'protein': 4, 'fats': 5, 'unit': 'porcion'},
    }
    
    # Multiplicadores para cantidades relativas
    QUANTITY_MULTIPLIERS = {
        'poco': 0.5,
        'poco de': 0.5,
        'muy poco': 0.25,
        'un poco': 0.5,
        'medio': 0.5,
        'media': 0.5,
        'bastante': 1.5,
        'mucho': 2.0,
        'mucha': 2.0,
        'muy': 1.5,
        'dos': 2.0,
        'doble': 2.0,
        'triple': 3.0,
        'uno': 1.0,
        'una': 1.0,
    }
    
    @classmethod
    def parse_food_description(cls, description: str) -> Tuple[float, float, float]:
        """
        Parsea descripción de comida y retorna (carbohidratos, proteína, grasas)
        """
        description = description.lower().strip()
        
        total_carbs = 0
        total_protein = 0
        total_fats = 0
        
        # Buscar alimentos en la descripción
        for food, nutrition in cls.FOODS_DATABASE.items():
            if food in description:
                # Buscar multiplicador de cantidad
                multiplier = 1.0
                for quantity, mult in cls.QUANTITY_MULTIPLIERS.items():
                    pattern = f"{quantity}\\s+{food}"
                    if re.search(pattern, description, re.IGNORECASE):
                        multiplier = mult
                        break
                
                total_carbs += nutrition['carbs'] * multiplier
                total_protein += nutrition['protein'] * multiplier
                total_fats += nutrition['fats'] * multiplier
        
        return round(total_carbs, 1), round(total_protein, 1), round(total_fats, 1)


class ExerciseParser:
    """Parsea descripciones de ejercicio a minutos"""
    
    # Mapeo de actividades a minutos equivalentes
    EXERCISE_DATABASE = {
        'descanso': 0,
        'sedentario': 0,
        'no hice': 0,
        'no hizo': 0,
        'no haré': 0,
        'no hago': 0,
        'sin ejercicio': 0,
        'ninguno': 0,
        
        'caminata': 30,
        'caminé': 30,
        'caminar': 30, 
        'camino': 30,
        'paseo': 20,
        'paseé': 20,
        
        'corrida': 45,
        'correr': 45,
        'corrí': 45,
        'corro': 45,
        'trote': 40,

        'yoga': 60,
        'stretching': 15,
        'estiramiento': 15,
        
        'natación': 60,
        'nadar': 60,
        'nadé': 60,
        'piscina': 50,
        
        'ciclismo': 60,
        'bicicleta': 50,
        'monté bici': 50,
        'bike': 50,
        
        'gym': 60,
        'gimnasio': 60,
        'pesas': 50,
        'levantamiento': 60,
        'pesa': 45,
        
        'saltar': 45,
        'saltos': 45,
        'cuerda': 60,
        'saltar cuerda': 60,
        
        'futbol': 90,
        'fútbol': 90,
        'basketball': 80,
        'baloncesto': 80,
        'tenis': 75,
        'voley': 70,
        'vóley': 70,
        
        'trabajo': 30,
        'trabajé': 30,
        'laboral': 20,
        'trabajo pesado': 45,
        
        'limpieza': 25,
        'limpié': 25,
        'quehaceres': 30,
    }
    
    # Intensidad multipliers
    INTENSITY_MULTIPLIERS = {
        'poco': 0.5,
        'ligero': 0.7,
        'moderado': 1.0,
        'intenso': 1.5,
        'muy intenso': 2.0,
        'fuerte': 1.5,
        'duro': 1.5,
    }
    
    @classmethod
    def parse_exercise_description(cls, description: str) -> float:
        """
        Parsea descripción de ejercicio y retorna minutos
        Detecta múltiples ejercicios con números específicos
        Ejemplo: "40 minutos de caminar y 10 minutos de saltar" = 50 minutos
        """
        description = description.lower().strip()
        
        exercise_minutes = 0
        intensity_multiplier = 1.0
        
        # Buscar intensidad
        for intensity, mult in cls.INTENSITY_MULTIPLIERS.items():
            if intensity in description:
                intensity_multiplier = mult
                break
        
        # Estrategia 1: Buscar patrones con números específicos
        # "X minutos de [ejercicio]" o "X min de [ejercicio]"
        for exercise in cls.EXERCISE_DATABASE.keys():
            # Buscar patrón: número + minutos/min + de + ejercicio
            patterns = [
                rf'(\d+)\s+(?:minuto|min)[os]*\s+de\s+{exercise}',
                rf'(\d+)\s+(?:minuto|min)[os]*\s+{exercise}',
                rf'{exercise}\s+(\d+)\s+(?:minuto|min)[os]*',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, description)
                for match in matches:
                    exercise_minutes += int(match) * intensity_multiplier
        
        # Estrategia 2: Si no encontró números específicos, buscar ejercicios sin números
        if exercise_minutes == 0:
            for exercise, minutes in cls.EXERCISE_DATABASE.items():
                if exercise in description:
                    exercise_minutes += minutes * intensity_multiplier
        
        # Estrategia 3: Si aún no encontró nada, buscar números sin ejercicio específico
        if exercise_minutes == 0:
            numbers = re.findall(r'\d+', description)
            if numbers:
                if any(word in description for word in ['minuto', 'min', 'hora', 'oras']):
                    if 'hora' in description:
                        exercise_minutes = int(numbers[0]) * 60
                    else:
                        exercise_minutes = int(numbers[0])
        
        return round(exercise_minutes, 0)


class GlucoseParser:
    """Parsea descripciones de glucosa"""
    
    GLUCOSE_LEVELS = {
        'bajo': 80,
        'muy bajo': 60,
        'normal': 120,
        'bien': 110,
        'alto': 160,
        'muy alto': 200,
        'elevado': 170,
    }
    
    @classmethod
    def parse_glucose_description(cls, description: str) -> float:
        """
        Parsea descripción de glucosa y retorna mg/dl
        Busca patrones como: "glucosa de 170", "glucosa es 170", "mi glucosa 170"
        """
        description = description.lower().strip()
        
        # Estrategia 1: Buscar patrones específicos con "glucosa"
        # Patrones: "glucosa de 170", "glucosa es 170", "glucosa 170", "mi glucosa es 170"
        glucose_patterns = [
            r'glucosa\s+de\s+(\d+)',      # glucosa de 170
            r'glucosa\s+es\s+(\d+)',      # glucosa es 170
            r'glucosa\s+(\d+)',           # glucosa 170
            r'glucosa está en\s+(\d+)',   # glucosa está en 170
            r'mi glucosa\s+(\d+)',        # mi glucosa 170
        ]
        
        for pattern in glucose_patterns:
            match = re.search(pattern, description)
            if match:
                glucose = int(match.group(1))
                if 60 <= glucose <= 400:  # Rango válido
                    return float(glucose)
        
        # Estrategia 2: Si no hay patrón de glucosa, buscar números generales
        # pero solo si mencionan "glucosa"
        if 'glucosa' in description or 'azúcar' in description or 'azucar' in description:
            numbers = re.findall(r'\d+', description)
            # Filtrar números que probablemente son glucosa (entre 60-400)
            for num_str in numbers:
                glucose = int(num_str)
                if 60 <= glucose <= 400:
                    return float(glucose)
        
        # Estrategia 3: Buscar descripciones cualitativas
        for level, glucose_value in cls.GLUCOSE_LEVELS.items():
            if level in description:
                return float(glucose_value)
        
        # Default: normal
        return 120.0


class NaturalLanguageProcessor:
    """Procesa descripciones en lenguaje natural completas"""
    
    @staticmethod
    def process_user_input(user_input: str) -> Dict:
        """
        Procesa entrada del usuario y extrae valores numéricos
        
        Retorna:
        {
            'exercise_minutes': float,
            'carbohydrates': float,
            'protein': float,
            'fats': float,
            'glucose': float,
            'interpretations': list,
            'corrections': dict
        }
        """
        # Aplicar corrección de ortografía y jerga
        corrected_input, corrections = SpellingCorrector.correct_text(user_input)
        
        lower_input = corrected_input.lower()
        interpretations = []
        
        # Agregar información sobre correcciones realizadas
        if corrections['spelling'] or corrections['slang'] or corrections['numbers']:
            correction_details = []
            if corrections['spelling']:
                correction_details.append(f"Ortografía: {', '.join(corrections['spelling'])}")
            if corrections['slang']:
                correction_details.append(f"Jerga: {', '.join(corrections['slang'])}")
            if corrections['numbers']:
                correction_details.append(f"Números: {', '.join(corrections['numbers'])}")
            
            interpretations.append(f"🔧 [CORRECCIONES] {' | '.join(correction_details)}")
        
        # Parsear ejercicio (usar texto corregido)
        exercise_minutes = ExerciseParser.parse_exercise_description(corrected_input)
        if exercise_minutes > 0:
            interpretations.append(f"[EJERCICIO] {int(exercise_minutes)} minutos")
        else:
            interpretations.append("[SIN EJERCICIO]")
        
        # Parsear comida (usar texto corregido)
        carbs, protein, fats = FoodParser.parse_food_description(corrected_input)
        if carbs > 0:
            interpretations.append(f"[ALIMENTOS] Carbohidratos: {carbs}g | Proteina: {protein}g | Grasas: {fats}g")
        else:
            interpretations.append("[INFO] No pude identificar alimentos especificos")
        
        # Parsear glucosa (usar texto corregido)
        glucose = GlucoseParser.parse_glucose_description(corrected_input)
        interpretations.append(f"[GLUCOSA] {int(glucose)} mg/dl")
        
        return {
            'exercise_minutes': exercise_minutes,
            'carbohydrates': carbs,
            'protein': protein,
            'fats': fats,
            'glucose': glucose,
            'interpretations': interpretations,
            'corrections': corrections,
            'corrected_input': corrected_input
        }
