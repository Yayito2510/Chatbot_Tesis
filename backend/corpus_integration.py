"""
Módulo de Integración de Corpus Médicos
Integra múltiples archivos CSV en un sistema de búsqueda unificado
"""

import pandas as pd
import os
import json
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

class CorpusIntegration:
    """Integra múltiples corpus médicos en un sistema de búsqueda unificado"""
    
    def __init__(self):
        self.corpus_data = None
        self.corpus_metadata = {
            'total_records': 0,
            'sources': {},
            'loaded_files': []
        }
        self.load_all_corpus()
    
    def load_all_corpus(self):
        """Carga y integra todos los corpus disponibles"""
        data_dir = 'data'
        corpus_files = [
            ('data_general.csv', 'general'),
            ('data_medical.csv', 'medical'),
            ('ChatDoctor_HealthCareMagic_train.csv', 'healthcare'),
            ('DiabetesQA_train.csv', 'diabetes_qa'),
            ('diabetes_qa_train.csv', 'diabetes_qa_v2'),
            ('medicine_qa_diabetes_train.csv', 'medicine_qa'),
            ('train.csv', 'generic_train')
        ]
        
        all_data = []
        
        for filename, source_name in corpus_files:
            filepath = os.path.join(data_dir, filename)
            try:
                if os.path.exists(filepath):
                    df = pd.read_csv(filepath)
                    
                    # Normalizar columnas
                    normalized_df = self._normalize_dataframe(df, source_name)
                    
                    if len(normalized_df) > 0:
                        all_data.append(normalized_df)
                        
                        self.corpus_metadata['sources'][source_name] = {
                            'filename': filename,
                            'records': len(normalized_df),
                            'columns': list(df.columns)
                        }
                        self.corpus_metadata['loaded_files'].append(filename)
                        
                        print(f"[OK] {source_name}: {len(normalized_df)} registros")
            except Exception as e:
                print(f"[WARN] Error cargando {filename}: {e}")
        
        if all_data:
            self.corpus_data = pd.concat(all_data, ignore_index=True)
            self.corpus_metadata['total_records'] = len(self.corpus_data)
            print(f"\n[OK] Corpus integrado: {self.corpus_metadata['total_records']} registros totales")
            print(f"[OK] Fuentes: {', '.join(self.corpus_metadata['sources'].keys())}")
        else:
            print("[WARN] No se cargaron corpus")
    
    def _normalize_dataframe(self, df: pd.DataFrame, source_name: str) -> pd.DataFrame:
        """Normaliza un DataFrame al formato estándar"""
        normalized = pd.DataFrame()
        
        # Mapeo flexible de columnas
        question_cols = ['question', 'short_question', 'query', 'input', 'text', 'query_text']
        answer_cols = ['answer', 'short_answer', 'response', 'output', 'label', 'diagnosis']
        
        # Encontrar columnas de pregunta y respuesta
        question_col = None
        answer_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if not question_col and any(q in col_lower for q in question_cols):
                question_col = col
            if not answer_col and any(a in col_lower for a in answer_cols):
                answer_col = col
        
        # Si no se encuentran, usar las primeras dos columnas
        if not question_col and len(df.columns) > 0:
            question_col = df.columns[0]
        if not answer_col and len(df.columns) > 1:
            answer_col = df.columns[1]
        
        if question_col and answer_col:
            normalized['question'] = df[question_col].astype(str)
            normalized['answer'] = df[answer_col].astype(str)
            normalized['source'] = source_name
            
            # Limpiar datos vacíos
            normalized = normalized[normalized['question'].str.strip() != '']
            normalized = normalized[normalized['answer'].str.strip() != '']
        
        return normalized
    
    def search(self, query: str, threshold: float = 0.3, top_k: int = 5) -> List[Dict]:
        """Busca en todos los corpus integrados"""
        if self.corpus_data is None or len(self.corpus_data) == 0:
            return []
        
        query_lower = query.lower()
        results = []
        
        for idx, row in self.corpus_data.iterrows():
            question = str(row['question']).lower()
            similarity = SequenceMatcher(None, query_lower, question).ratio()
            
            if similarity > threshold:
                results.append({
                    'question': row['question'],
                    'answer': row['answer'],
                    'source': row['source'],
                    'similarity': round(similarity, 2),
                    'index': idx
                })
        
        # Ordenar por similitud
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def search_by_keywords(self, keywords: List[str], top_k: int = 10) -> List[Dict]:
        """Busca registros que contengan palabras clave"""
        if self.corpus_data is None:
            return []
        
        results = []
        
        for idx, row in self.corpus_data.iterrows():
            question = str(row['question']).lower()
            answer = str(row['answer']).lower()
            
            # Contar coincidencias de palabras clave
            matches = sum(1 for kw in keywords if kw.lower() in question or kw.lower() in answer)
            
            if matches > 0:
                results.append({
                    'question': row['question'],
                    'answer': row['answer'],
                    'source': row['source'],
                    'keyword_matches': matches,
                    'index': idx
                })
        
        # Ordenar por número de coincidencias
        results.sort(key=lambda x: x['keyword_matches'], reverse=True)
        return results[:top_k]
    
    def get_statistics(self) -> Dict:
        """Retorna estadísticas del corpus integrado"""
        return {
            'total_records': self.corpus_metadata['total_records'],
            'sources': self.corpus_metadata['sources'],
            'loaded_files': self.corpus_metadata['loaded_files'],
            'unique_sources': len(self.corpus_metadata['sources'])
        }
    
    def export_search_index(self, output_file: str = 'corpus_index.json'):
        """Exporta un índice de búsqueda para acceso rápido"""
        if self.corpus_data is None:
            return False
        
        try:
            index = {
                'metadata': self.corpus_metadata,
                'total_entries': len(self.corpus_data),
                'sample_queries': self.corpus_data['question'].head(100).tolist()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            
            print(f"[OK] Índice exportado a {output_file}")
            return True
        except Exception as e:
            print(f"[ERROR] No se pudo exportar índice: {e}")
            return False
    
    def get_source_breakdown(self) -> Dict:
        """Retorna desglose de registros por fuente"""
        if self.corpus_data is None:
            return {}
        
        breakdown = {}
        for source, group in self.corpus_data.groupby('source'):
            breakdown[source] = {
                'count': len(group),
                'percentage': round(len(group) / len(self.corpus_data) * 100, 2)
            }
        
        return breakdown

# Instancia global del corpus integrado
integrated_corpus = CorpusIntegration()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SISTEMA DE CORPUS INTEGRADO")
    print("="*60)
    
    # Mostrar estadísticas
    stats = integrated_corpus.get_statistics()
    print(f"\n📊 Total de registros: {stats['total_records']}")
    print(f"📁 Fuentes cargadas: {stats['unique_sources']}")
    
    # Mostrar desglose
    breakdown = integrated_corpus.get_source_breakdown()
    print("\n📈 Desglose por fuente:")
    for source, data in breakdown.items():
        print(f"  • {source}: {data['count']} registros ({data['percentage']}%)")
    
    # Ejemplos de búsqueda
    print("\n" + "="*60)
    print("EJEMPLOS DE BÚSQUEDA")
    print("="*60)
    
    test_queries = [
        "síntomas de diabetes",
        "glucosa elevada",
        "insulina",
        "alimentos diabetes",
        "complicaciones"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Buscando: '{query}'")
        results = integrated_corpus.search(query, threshold=0.25, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n  Resultado {i}:")
            print(f"  ├─ Fuente: {result['source']}")
            print(f"  ├─ Similitud: {result['similarity']:.0%}")
            print(f"  ├─ Pregunta: {result['question'][:80]}...")
            print(f"  └─ Respuesta: {result['answer'][:100]}...")
    
    # Exportar índice
    integrated_corpus.export_search_index()
