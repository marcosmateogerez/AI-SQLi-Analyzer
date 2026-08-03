FROM python:3.11-slim

WORKDIR /app

# Copiar e instalar dependencias de Python.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente.
COPY . .

# Comando de inicio.
CMD ["python", "main.py"]