import pandas as pd
import numpy as np
from .models import DashboardKPIs


def calcular_analitica_dataset(df: pd.DataFrame):
    """
    Recibe un DataFrame de Pandas limpio y calcula todas las métricas
    obligatorias de la guía, guardándolas en la base de datos.
    """
    total = len(df)
    if total == 0:
        return None

    # 1. Detección de Pacientes Críticos
    # Presión sistólica > 180 Ó Glucosa > 300 Ó Saturación < 85
    col_sistolica = 'presión_sistólica' if 'presión_sistólica' in df.columns else 'presion_sistolica'
    col_glucosa = 'glucosa'
    col_saturacion = 'saturación_oxígeno' if 'saturación_oxígeno' in df.columns else 'saturacion_oxigeno'

    condicion_critica = (
        (df[col_sistolica] > 180) |
        (df[col_glucosa] > 300) |
        (df[col_saturacion] < 85)
    )
    criticos = int(df[condicion_critica].shape[0])

    # 2. KPIs de Control Epidemiológico
    # Hipertensión y Diabetes se derivan de la columna diagnóstico_preliminar
    col_diag = 'diagnóstico_preliminar' if 'diagnóstico_preliminar' in df.columns else 'diagnostico_preliminar'
    hipertensos = 0
    diabeticos = 0
    if col_diag in df.columns:
        diag_series = df[col_diag].astype(str).str.lower().str.strip()
        hipertensos = int(diag_series.str.contains('hipertens', na=False).sum())
        diabeticos = int(diag_series.str.contains('diabet', na=False).sum())

    fumadores = int(df['fumador'].sum()) if 'fumador' in df.columns else 0

    # Riesgo promedio
    col_riesgo = 'riesgo_enfermedad' if 'riesgo_enfermedad' in df.columns else 'riesgo_clinico'
    riesgo_prom = 0.0
    if col_riesgo in df.columns:
        mapeo_riesgo = {'Bajo': 0.25, 'Medio': 0.50, 'Alto': 0.75, 'Crítico': 1.0}
        riesgo_prom = float(df[col_riesgo].map(mapeo_riesgo).fillna(0.0).mean())

    # 3. Estadística Descriptiva
    col_edad = 'edad'
    e_media = float(df[col_edad].mean())
    e_mediana = float(df[col_edad].median())
    e_moda = float(df[col_edad].mode()[0]) if not df[col_edad].mode().empty else 0.0
    e_desviacion = float(df[col_edad].std()) if len(df) > 1 else 0.0

    g_media = float(df[col_glucosa].mean())
    g_desviacion = float(df[col_glucosa].std()) if len(df) > 1 else 0.0

    # 4. Guardar el reporte analítico
    kpi_reporte = DashboardKPIs.objects.create(
        total_registros=total,
        pacientes_criticos=criticos,
        pacientes_hipertensos=hipertensos,
        pacientes_diabeticos=diabeticos,
        pacientes_fumadores=fumadores,
        riesgo_promedio=round(riesgo_prom * 100, 2),
        edad_media=round(e_media, 2),
        edad_mediana=round(e_mediana, 2),
        edad_moda=round(e_moda, 2),
        edad_desviacion=round(e_desviacion, 2),
        glucosa_media=round(g_media, 2),
        glucosa_desviacion=round(g_desviacion, 2),
    )

    return kpi_reporte
