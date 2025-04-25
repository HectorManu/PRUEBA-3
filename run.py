from app import create_app
from app.models.database import init_db
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Crear la aplicación
app = create_app()

# Configurar el logger de la aplicación
app.logger.setLevel(logging.DEBUG)

# Inicializar la base de datos dentro del contexto de la aplicación
with app.app_context():
    # Asegurarse de que la carpeta data existe
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Inicializar la base de datos con datos de ejemplo
    init_db()
    app.logger.info("Base de datos inicializada correctamente.")

# Asegurarse de que la clave API de DeepSeek está configurada si se proporciona
deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY') or app.config.get('DEEPSEEK_API_KEY')
if deepseek_api_key:
    app.logger.info("DeepSeek API Key configurada: {}...{}".format(
        deepseek_api_key[:4], 
        deepseek_api_key[-4:] if len(deepseek_api_key) > 8 else ''
    ))
else:
    app.logger.warning("DEEPSEEK_API_KEY no configurada.")

# Asegurarse de que la clave API de OpenAI está configurada si se proporciona
openai_api_key = os.environ.get('OPENAI_API_KEY') or app.config.get('OPENAI_API_KEY')
if openai_api_key:
    app.logger.info("OpenAI API Key configurada: {}...{}".format(
        openai_api_key[:4], 
        openai_api_key[-4:] if len(openai_api_key) > 8 else ''
    ))
else:
    app.logger.warning("OPENAI_API_KEY no configurada.")

# Configurar el modo de detección de intenciones
nlp_service = os.environ.get('NLP_SERVICE') or app.config.get('NLP_SERVICE', 'auto')
app.config['NLP_SERVICE'] = nlp_service
app.logger.info(f"Modo de detección de intenciones: {nlp_service}")

# Mostrar la URL base para DeepSeek
app.logger.info("URL base para DeepSeek: https://api.deepseek.com")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)