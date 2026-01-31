FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y archivo de API
COPY requirements.txt .
COPY api_server.py .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Puerto que expone el contenedor
EXPOSE 8000

# Variables de entorno por defecto (se sobreescriben en el dashboard de la nube)
ENV PYTHONUNBUFFERED=1

# Comando de inicio
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
