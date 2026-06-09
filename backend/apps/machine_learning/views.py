from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.machine_learning.services import PredictorRiesgoService

class TrainModelView(APIView):
    """
    Endpoint para disparar el entrenamiento del modelo predictivo y obtener sus métricas de precisión médica
    """
    def post(self, request, format=None):
        try:
            predictor = PredictorRiesgoService()
            reporte_metricas = predictor.entrenar_modelo()
            
            return Response({
                "status": "success",
                "modelo": "Random Forest Classifier - VITA Engine",
                "metricas_evaluacion": reporte_metricas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Fallo al entrenar el modelo predictivo: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)