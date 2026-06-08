from django.db import models
from django.contrib.auth.models import User


class Paciente(models.Model):
    # Identificación básica (id_paciente del CSV como llave primaria)
    id_paciente = models.IntegerField(unique=True, primary_key=True)
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=20)

    # Variables de Antropometría (Peso y Talla)
    peso = models.FloatField(null=True, blank=True)
    altura = models.FloatField(null=True, blank=True)
    imc = models.FloatField(null=True, blank=True)  # Calculado en ETL
    clasificacion_imc = models.CharField(max_length=50, null=True, blank=True)  # Calculado en ETL

    # Signos Vitales y Paraclínicos
    presion_sistolica = models.IntegerField(null=True, blank=True)
    presion_diastolica = models.IntegerField(null=True, blank=True)
    frecuencia_cardiaca = models.IntegerField(null=True, blank=True)
    glucosa = models.FloatField(null=True, blank=True)
    colesterol = models.FloatField(null=True, blank=True)
    saturacion_oxigeno = models.FloatField(null=True, blank=True)
    temperatura = models.FloatField(null=True, blank=True)

    # Antecedentes y Estilo de Vida
    antecedentes_familiares = models.BooleanField(default=False)
    fumador = models.BooleanField(default=False)
    consumo_alcohol = models.BooleanField(default=False)
    actividad_fisica = models.CharField(max_length=50, null=True, blank=True)

    # Diagnóstico y Gestión de Riesgo
    diagnostico_preliminar = models.CharField(max_length=250, null=True, blank=True)
    riesgo_enfermedad = models.CharField(max_length=50, null=True, blank=True)  # Calculado/Validado en ETL
    fecha_consulta = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - ID: {self.id_paciente}"


class HistorialETL(models.Model):
    # Control de auditoría para el proceso de carga masiva
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    registros_procesados = models.IntegerField()
    tiempo_ejecucion = models.FloatField()  # En segundos
    estado = models.CharField(max_length=50)  # 'Exitoso' o 'Fallido'

    def __str__(self):
        return f"Ejecución ETL {self.id} - {self.estado} ({self.fecha})"  # pyrefly: ignore
