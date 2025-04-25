from flask import Flask, render_template
from app.config import Config
from app.routes.chatbot_routes import chatbot_bp
from app.models.database import close_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configurar el manejo de cierre de base de datos
    app.teardown_appcontext(close_db)
    
    # Registrar blueprints
    app.register_blueprint(chatbot_bp)
    
    # Ruta principal para la interfaz de chat
    @app.route('/')
    def index():
        return render_template('chat.html')
    
    # Ruta de información API
    @app.route('/api')
    def api_info():
        return {"status": "API funcionando correctamente", 
                "endpoints": ["/chatbot"],
                "descripción": "API para chatbot con detección de intenciones"}
    
    return app