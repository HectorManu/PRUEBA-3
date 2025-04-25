import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # Configuración general
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-segura-por-defecto'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///data/database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or 'gpt-3.5-turbo'
    
    # Seguridad
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # Limitar tamaño de las solicitudes a 1MB