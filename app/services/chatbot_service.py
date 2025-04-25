from app.services.openai_service import OpenAIService
from app.models.database import (
    consultar_mejores_compradores,
    consultar_deudores_altos,
    contar_compradores,
    contar_deudores
)
from flask import current_app

class ChatbotService:
    def __init__(self):
        self.openai_service = OpenAIService()
    
    def process_message(self, user_message):
        """
        Procesa el mensaje del usuario y genera una respuesta basada en la intención detectada
        """
        try:
            # Detectar la intención del mensaje
            intent_data = self.openai_service.detect_intent(user_message)
            intent = intent_data.get('intent', 'desconocido')
            parameters = intent_data.get('parameters', {})
            
            # Procesar la intención detectada
            if intent == "mejores_compradores":
                return self._handle_mejores_compradores(parameters)
            elif intent == "deudores_altos":
                return self._handle_deudores_altos(parameters)
            elif intent == "contar_compradores":
                return self._handle_contar_compradores()
            elif intent == "contar_deudores":
                return self._handle_contar_deudores()
            else:
                return {
                    "status": "error",
                    "message": "No he entendido tu consulta. Por favor, intenta preguntar sobre los compradores o deudores de nuestra base de datos."
                }
        
        except Exception as e:
            current_app.logger.error(f"Error en el procesamiento del chatbot: {str(e)}")
            return {
                "status": "error",
                "message": "Ocurrió un error al procesar tu consulta."
            }
    
    def _handle_mejores_compradores(self, parameters):
        """Maneja la intención de consultar los mejores compradores"""
        limite = parameters.get('limite', 3)
        
        # Validar y convertir el límite
        try:
            limite = int(limite)
            if limite <= 0:
                limite = 3
        except (ValueError, TypeError):
            limite = 3
        
        compradores = consultar_mejores_compradores(limite)
        
        if not compradores:
            return {
                "status": "success",
                "message": "No hay compradores registrados en el sistema."
            }
        
        # Formato de la respuesta
        message = f"Los {len(compradores)} mejores compradores son:\n"
        for i, comprador in enumerate(compradores, 1):
            message += f"{i}. {comprador['nombre']} - ${comprador['total_compras']:.2f}\n"
        
        return {
            "status": "success",
            "message": message.strip(),
            "data": compradores
        }
    
    def _handle_deudores_altos(self, parameters):
        """Maneja la intención de consultar los deudores con montos más altos"""
        limite = parameters.get('limite', 3)
        
        # Validar y convertir el límite
        try:
            limite = int(limite)
            if limite <= 0:
                limite = 3
        except (ValueError, TypeError):
            limite = 3
        
        deudores = consultar_deudores_altos(limite)
        
        if not deudores:
            return {
                "status": "success",
                "message": "No hay deudores registrados en el sistema."
            }
        
        # Formato de la respuesta
        message = f"Los {len(deudores)} deudores con montos más altos son:\n"
        for i, deudor in enumerate(deudores, 1):
            message += f"{i}. {deudor['nombre']} - ${deudor['monto_adeudado']:.2f}\n"
        
        return {
            "status": "success",
            "message": message.strip(),
            "data": deudores
        }
    
    def _handle_contar_compradores(self):
        """Maneja la intención de contar el número total de compradores"""
        count = contar_compradores()
        
        return {
            "status": "success",
            "message": f"Hay un total de {count} compradores registrados en el sistema.",
            "data": {"total_compradores": count}
        }
    
    def _handle_contar_deudores(self):
        """Maneja la intención de contar el número total de deudores"""
        count = contar_deudores()
        
        return {
            "status": "success",
            "message": f"Hay un total de {count} deudores registrados en el sistema.",
            "data": {"total_deudores": count}
        }