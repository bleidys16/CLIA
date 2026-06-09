import os
from django.core.management.base import BaseCommand, CommandError
from apps.etl.services import PipelineETL

class Command(BaseCommand):
    help = 'Ejecuta de forma secuencial el pipeline ETL de VITA para procesar el archivo Excel clínico'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n=== INICIANDO MOTOR AUTOMATIZADO ETL EN VITA ===\n'))
        
        # Construimos la ruta apuntando a backend/datasets/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        file_path = os.path.join(base_dir, 'datasets', 'dataset_clinico_etl_1800_registros.xlsx')
        
        self.stdout.write(f"Buscando archivo en: {file_path}")

        try:
            # Inicializar el servicio de VITA
            pipeline = PipelineETL(file_path=file_path)
            
            # 1. CAPA EXTRACT
            self.stdout.write(self.style.MIGRATE_LABEL('1. Ejecutando capa de Extracción (Extract)...'))
            leidos = pipeline.extract()
            self.stdout.write(self.style.SUCCESS(f'   ✔ Éxito: Se leyeron {leidos} filas originales del Excel.'))
            
            # 2. CAPA TRANSFORM
            self.stdout.write(self.style.MIGRATE_LABEL('2. Ejecutando capa de Transformación (Transform)...'))
            transformados = pipeline.transform()
            self.stdout.write(self.style.SUCCESS(f'   ✔ Éxito: Quedaron {transformados} registros tras normalizar nulos y limpiar duplicados.'))
            
            # 3. CAPA LOAD
            self.stdout.write(self.style.MIGRATE_LABEL('3. Ejecutando capa de Carga en PostgreSQL (Load)...'))
            exito, cargados = pipeline.load()
            
            self.stdout.write(self.style.SUCCESS(f'\n🚀 ¡PROCESO FINALIZADO CON ÉXITO!'))
            self.stdout.write(self.style.SUCCESS(f'Se insertaron {cargados} registros limpios de forma atómica en PostgreSQL.\n'))
            
        except FileNotFoundError:
            raise CommandError(
                f'\n[ERROR] No se pudo iniciar el proceso. El archivo Excel NO existe en la ruta:\n{file_path}\n'
                f'Por favor, asegúrate de colocar el archivo en la carpeta "backend/datasets/"'
            )
        except Exception as e:
            raise CommandError(f'\n[ERROR CRÍTICO] El pipeline falló debido a: {str(e)}')