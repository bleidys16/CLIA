from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdministrador, IsAnalista
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .services import PipelineETL
from .models import Paciente, HistorialETL


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
