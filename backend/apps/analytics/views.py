from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.analytics.services import IndicadoresClinicosService

class DashboardKPIsView(APIView):
    """
    Endpoint para extraer las estadísticas descriptivas y los KPIs clínicos consolidados de la IPS
    """
    def get(self, request, format=None):
        try:
            service = IndicadoresClinicosService()
            
            # Ejecutamos los cálculos estadísticos y agrupaciones
            estadisticas = service.obtener_estadisticas_descriptivas()
            kpis = service.obtener_kpis_dashboard()
            
            return Response({
                "status": "success",
                "plataforma": "CLIA (Clinical Intelligence & Analytics)",
                "kpis_consolidados": kpis,
                "estadistica_descriptiva": estadisticas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error al consolidar los indicadores analíticos: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)