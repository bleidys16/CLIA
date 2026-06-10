import os
from celery import Celery

# Establecer las variables de entorno por defecto para Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('vita_clinical')

# Leer la configuración de Celery desde el settings.py de Django usando el prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubrir tareas automáticamente en todas las apps registradas
app.autodiscover_tasks()