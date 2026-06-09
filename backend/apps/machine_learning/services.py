import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report
from apps.etl.models import Paciente

class PredictorRiesgoService:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()

    def preparar_datos(self):
        """Extrae los datos de PostgreSQL y los prepara para el modelo"""
        pacientes = Paciente.objects.all().values()
        if not pacientes:
            raise ValueError("No hay pacientes registrados en la base de datos.")
        
        df = pd.DataFrame(pacientes)
        
        # 1. FORZAR NUEVO SCORE CLÍNICO INTEGRAL (Quitamos el 'if' para que actúe siempre)
        score = (
            (df['glucosa'] > 100).astype(int) + 
            (df['presion_sistolica'] > 130).astype(int) + 
            (df['colesterol'] > 200).astype(int) +
            (df['imc'] >= 25).astype(int) +
            (df['frecuencia_cardiaca'] > 90).astype(int) +
            (df['saturacion_oxigeno'] < 95).astype(int) +
            (df['edad'] > 50).astype(int) +
            (df['fumador'] == True).astype(int)
        )
        
        # Inicializamos y sobreescribimos las etiquetas previas de la BD
        df['riesgo_enfermedad'] = 'Bajo'
        df.loc[score >= 1, 'riesgo_enfermedad'] = 'Medio'
        df.loc[score >= 3, 'riesgo_enfermedad'] = 'Alto'
        df.loc[score >= 5, 'riesgo_enfermedad'] = 'Crítico'
        
        # 2. Definir características (X) y variable objetivo (y)
        features = [
            'edad', 'peso', 'altura', 'imc', 
            'presion_sistolica', 'presion_diastolica', 
            'frecuencia_cardiaca', 'glucosa', 'colesterol', 
            'saturacion_oxigeno', 'temperatura',
            'antecedentes_familiares', 'fumador', 'consumo_alcohol'
        ]
        
        X = df[features].copy()
        
        # Convertir booleanos a enteros (0 o 1)
        for col in ['antecedentes_familiares', 'fumador', 'consumo_alcohol']:
            X[col] = X[col].astype(int)
            
        y = self.label_encoder.fit_transform(df['riesgo_enfermedad'])
        
        return X, y

    def entrenar_modelo(self):
        """Entrena el clasificador y retorna las métricas de evaluación de la IPS"""
        X, y = self.preparar_datos()
        
        # División del dataset: 80% Entrenamiento, 20% Prueba (exigido por buenas prácticas)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Escalado de características numéricas
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Ajustar modelo
        self.model.fit(X_train_scaled, y_train)
        
        # Predicciones para evaluación
        y_pred = self.model.predict(X_test_scaled)
        
        # Generar reporte de métricas en formato de diccionario
        target_names = self.label_encoder.classes_
        reporte_dict = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
        
        return reporte_dict