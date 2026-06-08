import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import PipelineETL

class RunETLView(APIView):
    """
    Endpoint para ejecutar manualmente la carga masiva y limpieza del dataset clínico
    """
    def post(self, request, format=None):
        # Para pruebas locales colocamos el archivo en una carpeta dentro de la raíz
        # Recuerda mover tu archivo CSV a la ruta 'backend/datasets/dataset_clinico.csv'
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'datasets', 'dataset_clinico.csv')
        
        try:
            # Instanciamos el pipeline pasando la ruta del dataset
            pipeline = PipelineETL(file_path=file_path, usuario_id=request.user.id)
            
            # Ejecutamos las fases secuencialmente
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