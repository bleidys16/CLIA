from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdministrador, IsAnalista
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .services import PipelineETL
from .models import Paciente, HistorialETL, DashboardKPIs
from .analytics import calcular_analitica_dataset



@method_decorator(csrf_exempt, name='dispatch')
class ETLLogListView(View):
    def get(self, request, format=None):
        historial = HistorialETL.objects.all().order_by('-fecha')
        logs_records = []
        for h in historial:
            logs_records.append({
                'fecha_ejecucion': h.fecha.isoformat() if h.fecha else None,
                'registros_procesados': h.registros_procesados,
                'tiempo_ejecucion': h.tiempo_ejecucion,
                'usuario_responsable': h.usuario.username if h.usuario else 'Sistema',
                'estado': h.estado,
            })
        return JsonResponse(logs_records, safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ResetDataView(View):
    def delete(self, request, format=None):
        try:
            pacientes_borrados = Paciente.objects.count()
            Paciente.objects.all().delete()
            HistorialETL.objects.all().delete()
            DashboardKPIs.objects.all().delete()
            return JsonResponse({
                "status": "success",
                "message": f"Datos restablecidos. {pacientes_borrados} registros eliminados."
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error al restablecer datos: {str(e)}"
            }, status=500)


class RunETLView(APIView):
    permission_classes = [IsAuthenticated, (IsAdministrador | IsAnalista)]

    def post(self, request, format=None):
        if 'file' not in request.FILES:
            return Response({
                "status": "error",
                "message": "No se ha seleccionado ningún archivo para procesar."
            }, status=status.HTTP_400_BAD_REQUEST)

        archivo_subido = request.FILES['file']

        try:
            usuario_id = request.user.id if request.user.is_authenticated else None
            pipeline = PipelineETL(file_path=archivo_subido, usuario_id=usuario_id)

            filas_extraidas = pipeline.extract()
            pipeline.transform()
            exito, filas_cargadas = pipeline.load()

            return Response({
                "status": "success",
                "message": "Proceso ETL ejecutado con éxito en VITA.",
                "registros_leidos": filas_extraidas,
                "total_procesados": filas_cargadas,
                "registros_procesados": filas_cargadas,
                "errores_encontrados": filas_extraidas - filas_cargadas
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Ocurrió un error crítico durante el procesamiento: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardAnalyticsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ultimo_kpi = DashboardKPIs.objects.order_by('-fecha_calculo').first()
        if not ultimo_kpi:
            return Response({"sistema_vacio": True})

        return Response({
            "sistema_vacio": False,
            "kpis": {
                "total_registros": ultimo_kpi.total_registros,
                "pacientes_criticos": ultimo_kpi.pacientes_criticos,
                "pacientes_hipertensos": ultimo_kpi.pacientes_hipertensos,
                "pacientes_diabeticos": ultimo_kpi.pacientes_diabeticos,
                "pacientes_fumadores": ultimo_kpi.pacientes_fumadores,
                "riesgo_promedio": ultimo_kpi.riesgo_promedio,
            },
            "estadistica_descriptiva": {
                "edad": {
                    "media": ultimo_kpi.edad_media,
                    "mediana": ultimo_kpi.edad_mediana,
                    "moda": ultimo_kpi.edad_moda,
                    "desviacion": ultimo_kpi.edad_desviacion,
                },
                "glucosa": {
                    "media": ultimo_kpi.glucosa_media,
                    "desviacion": ultimo_kpi.glucosa_desviacion,
                },
            },
        })


class AuthMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        rol = user.perfil.rol if hasattr(user, 'perfil') else None
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": rol,
        })

class DashboardDataView(APIView):
    permission_classes = [IsAuthenticated] # Protegido por seguridad de roles

    def get(self, request, format=None):
        # Tomamos el último reporte calculado disponible en el sistema
        ultimo_kpi = DashboardKPIs.objects.first()
        
        if not ultimo_kpi:
            return Response({"sistema_vacio": True}, status=status.HTTP_200_OK)
            
        return Response({
            "sistema_vacio": False,
            "kpis": {
                "total_registros": ultimo_kpi.total_registros,
                "pacientes_criticos": ultimo_kpi.pacientes_criticos,
                "pacientes_hipertensos": ultimo_kpi.pacientes_hipertensos,
                "pacientes_diabeticos": ultimo_kpi.pacientes_diabeticos,
                "pacientes_fumadores": ultimo_kpi.pacientes_fumadores,
                "riesgo_promedio": round(ultimo_kpi.riesgo_promedio, 2)
            },
            "estadistica_descriptiva": {
                "edad": {
                    "media": round(ultimo_kpi.edad_media, 2),
                    "mediana": round(ultimo_kpi.edad_mediana, 2),
                    "moda": round(ultimo_kpi.edad_moda, 2),
                    "desviacion": round(ultimo_kpi.edad_desviacion, 2)
                },
                "glucosa": {
                    "media": round(ultimo_kpi.glucosa_media, 2),
                    "desviacion": round(ultimo_kpi.glucosa_desviacion, 2)
                }
            }
        }, status=status.HTTP_200_OK)