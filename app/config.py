import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # Configuración general
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-segura-por-defecto'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///data/database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # DeepSeek API (prioridad)
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    DEEPSEEK_MODEL = os.environ.get('DEEPSEEK_MODEL') or 'deepseek-chat'
    
    # OpenAI API (secundario)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or 'gpt-3.5-turbo'
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # Preferencia de servicio de NLP (deepseek, openai o fallback)
    # 'auto' intentará usar DeepSeek primero, luego OpenAI, y finalmente fallback
    NLP_SERVICE = os.environ.get('NLP_SERVICE') or 'auto'
    
    # Seguridad
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # Limitar tamaño de las solicitudes a 1MB