# Usar una imagen oficial de Python ligera
FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc en el disco y asegurar salida en consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configurar el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar conectores de PostgreSQL si se requiere
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar todo el código del backend al contenedor
COPY . /app/

# Exponer el puerto de Django
EXPOSE 8000