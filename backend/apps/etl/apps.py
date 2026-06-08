from django.apps import AppConfig


class EtlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # pyrefly: ignore
    name = 'apps.etl'
