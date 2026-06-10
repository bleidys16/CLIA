from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.etl.models import MetricasModeloML
from apps.machine_learning.services import PredictorRiesgoService


class TrainModelView(APIView):
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


class MetricasModeloMLView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        metricas = MetricasModeloML.objects.filter(modelo_activo=True).first()

        if not metricas:
            return Response({"modelo_entrenado": False}, status=status.HTTP_200_OK)

        cm = metricas.matriz_confusion

        heatmap_data = [
            {
                "name": "Sano Predicho (0)",
                "data": [
                    {"x": "Sano Real (0)", "y": cm["verdaderos_negativos"]},
                    {"x": "Enfermo Real (1)", "y": cm["falsos_negativos"]}
                ]
            },
            {
                "name": "Enfermo Predicho (1)",
                "data": [
                    {"x": "Sano Real (0)", "y": cm["falsos_positivos"]},
                    {"x": "Enfermo Real (1)", "y": cm["verdaderos_positivos"]}
                ]
            }
        ]

        return Response({
            "modelo_entrenado": True,
            "accuracy": round(metricas.accuracy * 100, 2),
            "precision": round(metricas.precision * 100, 2),
            "recall": round(metricas.recall * 100, 2),
            "f1_score": round(metricas.f1_score * 100, 2),
            "heatmap": heatmap_data
        }, status=status.HTTP_200_OK)
