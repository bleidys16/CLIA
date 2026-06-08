from django.db.models import Avg, StdDev, Count, Q
from apps.etl.models import Paciente
import numpy as np

class IndicadoresClinicosService:
    
    @staticmethod
    def obtener_estadisticas_descriptivas():
        """
        Calcula Media, Mediana (vía Python/Numpy sobre el QuerySet) y Desviación Estándar 
        de las variables clínicas clave requeridas por la IPS.
        """
        # Extraemos las métricas agregadas base directamente de PostgreSQL (Media y Desviación Estándar)
        agregaciones = Paciente.objects.aggregate(
            # Edad
            edad_promedio=Avg('edad'),
            edad_std=StdDev('edad'),
            # Glucosa
            glucosa_promedio=Avg('glucosa'),
            glucosa_std=StdDev('glucosa'),
            # Colesterol
            colesterol_promedio=Avg('colesterol'),
            colesterol_std=StdDev('colesterol'),
            # Presión Sistólica
            sistolica_promedio=Avg('presion_sistolica'),
            sistolica_std=StdDev('presion_sistolica'),
            # IMC
            imc_promedio=Avg('imc'),
            imc_std=StdDev('imc')
        )
        
        # Para la mediana, al no ser una función nativa estándar en todas las BDs, 
        # extraemos los valores en listas y usamos NumPy para máxima precisión.
        valores_pacientes = Paciente.objects.values_list('edad', 'glucosa', 'colesterol', 'presion_sistolica', 'imc')
        
        if not valores_pacientes:
            return {}
            
        edades, glucosas, colesteroles, sistolicas, imcs = zip(*valores_pacientes)
        
        return {
            "edad": {
                "media": round(agregaciones['edad_promedio'] or 0, 2),
                "mediana": round(float(np.median(edades)), 2),
                "desviacion_estandar": round(agregaciones['edad_std'] or 0, 2)
            },
            "glucosa": {
                "media": round(agregaciones['glucosa_promedio'] or 0, 2),
                "mediana": round(float(np.median(glucosas)), 2),
                "desviacion_estandar": round(agregaciones['glucosa_std'] or 0, 2)
            },
            "colesterol": {
                "media": round(agregaciones['colesterol_promedio'] or 0, 2),
                "mediana": round(float(np.median(colesteroles)), 2),
                "desviacion_estandar": round(agregaciones['colesterol_std'] or 0, 2)
            },
            "presion_sistolica": {
                "media": round(agregaciones['sistolica_promedio'] or 0, 2),
                "mediana": round(float(np.median(sistolicas)), 2),
                "desviacion_estandar": round(agregaciones['sistolica_std'] or 0, 2)
            },
            "imc": {
                "media": round(agregaciones['imc_promedio'] or 0, 2),
                "mediana": round(float(np.median(imcs)), 2),
                "desviacion_estandar": round(agregaciones['imc_std'] or 0, 2)
            }
        }

    @staticmethod
    def obtener_kpis_dashboard():
        """
        Consolida los KPIs e indicadores institucionales solicitados por la IPS.
        """
        total_pacientes = Paciente.objects.count()
        if total_pacientes == 0:
            return {}

        # 1. Conteo de patologías basado en diagnósticos preliminares normalizados
        # (Usamos filtros Q para hacer búsquedas inteligentes e insensibles a mayúsculas)
        conteo_patologias = Paciente.objects.aggregate(
            hipertensos=Count('id_paciente', filter=Q(diagnostico_preliminar__icontains='Hipertensión')),
            diabeticos=Count('id_paciente', filter=Q(diagnostico_preliminar__icontains='Diabetes')),
            obesos=Count('id_paciente', filter=Q(clasificacion_imc='Obesidad')),
            criticos=Count('id_paciente', filter=Q(riesgo_enfermedad__icontains='Crítico'))
        )

        # 2. Distribución y porcentajes de niveles de riesgo médico
        distribucion_riesgo = Paciente.objects.values('riesgo_enfermedad').annotate(total=Count('id_paciente'))
        segmentacion_riesgo = {}
        for item in distribucion_riesgo:
            riesgo = item['riesgo_enfermedad'] or 'No Clasificado'
            cantidad = item['total']
            porcentaje = round((cantidad / total_pacientes) * 100, 2)
            segmentacion_riesgo[riesgo] = {
                "cantidad": cantidad,
                "porcentaje": porcentaje
            }

        # 3. Segmentación demográfica por sexo
        distribucion_sexo = Paciente.objects.values('sexo').annotate(total=Count('id_paciente'))
        segmentacion_sexo = {item['sexo']: item['total'] for item in distribucion_sexo}

        return {
            "resumen_general": {
                "total_pacientes_atendidos": total_pacientes,
                "pacientes_estado_critico": conteo_patologias['criticos']
            },
            "alertas_epidemiologicas_ips": {
                "total_hipertensos": conteo_patologias['hipertensos'],
                "total_diabeticos": conteo_patologias['diabeticos'],
                "total_obesos": conteo_patologias['obesos']
            },
            "distribucion_riesgos_porcentaje": segmentacion_riesgo,
            "demografia_sexo": segmentacion_sexo
            }