from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.etl.models import Perfil


class Command(BaseCommand):
    help = 'Puebla la base de datos con los usuarios iniciales del ecosistema VITA'

    def handle(self, *args, **options):
        usuarios_datos = [
            {"username": "admin@vita.com", "email": "admin@vita.com", "password": "Admin123", "rol": "ADMIN"},
            {"username": "analista@vita.com", "email": "analista@vita.com", "password": "Analista123", "rol": "ANALISTA"},
            {"username": "medico@vita.com", "email": "medico@vita.com", "password": "Medico123", "rol": "MEDICO"},
        ]

        for u in usuarios_datos:
            if not User.objects.filter(username=u["username"]).exists():
                user_obj = User.objects.create_user(
                    username=u["username"],
                    email=u["email"],
                    password=u["password"]
                )
                Perfil.objects.update_or_create(user=user_obj, defaults={"rol": u["rol"]})
                self.stdout.write(self.style.SUCCESS(f'Usuario creado con éxito: {u["username"]} [{u["rol"]}]'))
            else:
                self.stdout.write(self.style.WARNING(f'El usuario {u["username"]} ya se encuentra registrado.'))
