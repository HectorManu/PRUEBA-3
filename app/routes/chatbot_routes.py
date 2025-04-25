from flask import Blueprint, request, jsonify
from app.services.chatbot_service import ChatbotService
from app.utils.security import validate_json_input
import time

chatbot_bp = Blueprint('chatbot', __name__)
chatbot_service = ChatbotService()

@chatbot_bp.route('/chatbot', methods=['POST'])
def process_chatbot_message():
    """
    Endpoint para procesar mensajes del chatbot
    Espera un JSON con el formato: {"message": "texto del mensaje"}
    """
    # Verificar que el contenido sea JSON
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "La solicitud debe ser en formato JSON"
        }), 400
    
    # Obtener datos de la solicitud
    data = request.get_json()
    
    # Validar la entrada
    is_valid, error_message = validate_json_input(data, required_fields=['message'])
    if not is_valid:
        return jsonify({
            "status": "error",
            "message": error_message
        }), 400
    
    # Obtener el mensaje del usuario
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({
            "status": "error",
            "message": "El mensaje no puede estar vacío"
        }), 400
    
    # Procesar el mensaje y generar respuesta
    start_time = time.time()
    response = chatbot_service.process_message(user_message)
    processing_time = time.time() - start_time
    
    # Agregar información de tiempo de procesamiento para debugging
    response["processing_time"] = f"{processing_time:.2f}s"
    
    return jsonify(response)

@chatbot_bp.route('/chatbot/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar que el servicio esté funcionando correctamente
    """
    return jsonify({
        "status": "success",
        "message": "El servicio del chatbot está funcionando correctamente"
    })