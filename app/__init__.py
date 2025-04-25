from flask import Flask
from app.config import Config
from app.routes.chatbot_routes import chatbot_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Registrar blueprints
    app.register_blueprint(chatbot_bp)
    
    # Mensaje de inicio
    @app.route('/')
    def index():
        return {"status": "API funcionando correctamente", 
                "endpoints": ["/chatbot"],
                "descripción": "API para chatbot con detección de intenciones"}
    
    return app