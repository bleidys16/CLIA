import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import PipelineETL

class RunETLView(APIView):
    """
    Endpoint para ejecutar manualmente la carga masiva y limpieza del dataset clínico
    """
    def post(self, request, format=None):
        file_path = os.path.join(settings.BASE_DIR, 'datasets', 'dataset_clinico_etl_1800_registros.xlsx')
        
        try:
            pipeline = PipelineETL(file_path=file_path, usuario_id=request.user.id)
            
            filas_extraidas = pipeline.extract()
            pipeline.transform()
            exito, filas_cargadas = pipeline.load()
            
            return Response({
                "status": "success",
                "message": "Proceso ETL ejecutado con éxito en CLIA.",
                "registros_leidos": filas_extraidas,
                "registros_guardados": filas_cargadas
            }, status=status.HTTP_200_OK)
            
        except FileNotFoundError:
            return Response({
                "status": "error",
                "message": f"No se encontró el archivo del dataset en la ubicación esperada."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Ocurrió un error crítico durante el procesamiento: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)