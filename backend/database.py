"""
Módulo de base de datos para guardar pacientes e historial
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    """Gestiona la base de datos de pacientes e historial"""
    
    def __init__(self, db_path='diabetes_patients.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Crea las tablas si no existen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de pacientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email TEXT,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de historial de predicciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                exercise_minutes REAL,
                carbohydrates REAL,
                protein REAL,
                fats REAL,
                glucose REAL,
                predicted_dose REAL,
                user_input TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_patient(self, name: str, email: str = None, age: int = None) -> int:
        """Agrega un nuevo paciente o retorna ID si ya existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO patients (name, email, age)
                VALUES (?, ?, ?)
            ''', (name, email, age))
            conn.commit()
            patient_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # El paciente ya existe
            cursor.execute('SELECT id FROM patients WHERE name = ?', (name,))
            patient_id = cursor.fetchone()[0]
        
        conn.close()
        return patient_id
    
    def get_patient(self, name: str) -> Optional[Dict]:
        """Obtiene información de un paciente por nombre"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, age, created_at
            FROM patients
            WHERE name = ?
        ''', (name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'age': result[3],
                'created_at': result[4]
            }
        return None
    
    def get_all_patients(self) -> List[Dict]:
        """Obtiene todos los pacientes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, age, created_at
            FROM patients
            ORDER BY updated_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        patients = []
        for row in results:
            patients.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3],
                'created_at': row[4]
            })
        return patients
    
    def save_prediction(self, patient_id: int, exercise: float, carbs: float, 
                       protein: float, fats: float, glucose: float, 
                       predicted_dose: float, user_input: str) -> int:
        """Guarda una predicción en el historial"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (patient_id, exercise_minutes, carbohydrates, protein, fats, glucose, predicted_dose, user_input)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, exercise, carbs, protein, fats, glucose, predicted_dose, user_input))
        
        conn.commit()
        prediction_id = cursor.lastrowid
        conn.close()
        
        return prediction_id
    
    def get_patient_history(self, patient_id: int, limit: int = 50) -> List[Dict]:
        """Obtiene el historial de predicciones de un paciente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, exercise_minutes, carbohydrates, protein, fats, glucose, predicted_dose, user_input, created_at
            FROM predictions
            WHERE patient_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (patient_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'id': row[0],
                'exercise_minutes': row[1],
                'carbohydrates': row[2],
                'protein': row[3],
                'fats': row[4],
                'glucose': row[5],
                'predicted_dose': row[6],
                'user_input': row[7],
                'created_at': row[8]
            })
        return history
    
    def get_patient_statistics(self, patient_id: int) -> Dict:
        """Obtiene estadísticas del paciente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de predicciones
        cursor.execute('SELECT COUNT(*) FROM predictions WHERE patient_id = ?', (patient_id,))
        total_predictions = cursor.fetchone()[0]
        
        # Promedio de glucosa
        cursor.execute('SELECT AVG(glucose) FROM predictions WHERE patient_id = ? AND glucose > 0', (patient_id,))
        avg_glucose = cursor.fetchone()[0]
        
        # Promedio de dosis recomendada
        cursor.execute('SELECT AVG(predicted_dose) FROM predictions WHERE patient_id = ?', (patient_id,))
        avg_dose = cursor.fetchone()[0]
        
        # Promedio de ejercicio
        cursor.execute('SELECT AVG(exercise_minutes) FROM predictions WHERE patient_id = ?', (patient_id,))
        avg_exercise = cursor.fetchone()[0]
        
        # Promedio de carbohidratos
        cursor.execute('SELECT AVG(carbohydrates) FROM predictions WHERE patient_id = ? AND carbohydrates > 0', (patient_id,))
        avg_carbs = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_predictions': total_predictions,
            'avg_glucose': round(avg_glucose, 1) if avg_glucose else 0,
            'avg_dose': round(avg_dose, 1) if avg_dose else 0,
            'avg_exercise': round(avg_exercise, 1) if avg_exercise else 0,
            'avg_carbohydrates': round(avg_carbs, 1) if avg_carbs else 0
        }

# Instancia global de la base de datos
db = Database()
