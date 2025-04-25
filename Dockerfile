FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear archivo .env vacío si no existe
RUN touch .env

# Crear directorio para la base de datos
RUN mkdir -p data

# Exponer el puerto que utilizará Flask
EXPOSE 5000

# Comando para ejecutar la aplicación con gunicorn con logs detallados
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--log-level", "debug", "--access-logfile", "-", "--error-logfile", "-", "run:app"]