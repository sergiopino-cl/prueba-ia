FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias (si aplica)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación
COPY . .

# Exponer el puerto de Streamlit
EXPOSE 8501

# Configurar comando para iniciar Streamlit accesible desde cualquier IP en el contenedor
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
