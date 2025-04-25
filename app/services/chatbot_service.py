from app.services.fallback_service import FallbackService
from app.services.openai_service import OpenAIService
from app.models.database import (
    consultar_mejores_compradores,
    consultar_deudores_altos,
    contar_compradores,
    contar_deudores
)
from flask import current_app
import traceback

class ChatbotService:
    def __init__(self):
        self.deepseek_service = None
        self.openai_service = None
        self.fallback_service = None
        self.nlp_service_preference = None
    
    def initialize(self):
        """Inicializa los servicios de detección de intenciones según configuración"""
        try:
            # Inicializar el servicio de fallback siempre (es nuestro respaldo)
            if self.fallback_service is None:
                if current_app:
                    current_app.logger.info("Inicializando servicio de fallback...")
                self.fallback_service = FallbackService().initialize()
                if current_app:
                    current_app.logger.info("Servicio de fallback inicializado correctamente")
            
            # Inicializar DeepSeek con prioridad
            if self.deepseek_service is None:
                if current_app:
                    current_app.logger.info("Inicializando servicio DeepSeek...")
                self.deepseek_service = OpenAIService(use_deepseek=True).initialize()
                if self.deepseek_service is not None and current_app:
                    current_app.logger.info("Servicio DeepSeek inicializado correctamente")
                else:
                    current_app.logger.warning("No se pudo inicializar el servicio DeepSeek")
            
            # Inicializar OpenAI como respaldo secundario
            if self.openai_service is None:
                if current_app:
                    current_app.logger.info("Inicializando servicio OpenAI...")
                self.openai_service = OpenAIService(use_deepseek=False).initialize()
                if self.openai_service is not None and current_app:
                    current_app.logger.info("Servicio OpenAI inicializado correctamente")
                else:
                    current_app.logger.warning("No se pudo inicializar el servicio OpenAI")
            
            # Determinar la preferencia de servicio NLP
            if self.nlp_service_preference is None:
                self.nlp_service_preference = current_app.config.get('NLP_SERVICE', 'auto')
                if current_app:
                    current_app.logger.info(f"Preferencia de servicio NLP configurada: {self.nlp_service_preference}")
                
            return self
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error al inicializar servicios del chatbot: {str(e)}")
                current_app.logger.error(traceback.format_exc())
            return self  # Devolver self incluso con error para que al menos tengamos el fallback
    
    def process_message(self, user_message):
        """
        Procesa el mensaje del usuario y genera una respuesta basada en la intención detectada
        """
        try:
            # Inicializar los servicios si es necesario
            if self.deepseek_service is None or self.openai_service is None or self.fallback_service is None:
                if current_app:
                    current_app.logger.info("Servicios no inicializados, inicializando ahora...")
                self.initialize()
            
            # Detectar la intención según la configuración
            if current_app:
                current_app.logger.info(f"Procesando mensaje: '{user_message}'")
            
            intent_data = self._detect_intent(user_message)
            intent = intent_data.get('intent', 'desconocido')
            parameters = intent_data.get('parameters', {})
            
            # Registrar la intención detectada
            if current_app:
                current_app.logger.info(f"Intención detectada: {intent}, parámetros: {parameters}")
            
            # Procesar la intención detectada
            if intent == "mejores_compradores":
                if current_app:
                    current_app.logger.info("Manejando intención: mejores_compradores")
                return self._handle_mejores_compradores(parameters)
            elif intent == "deudores_altos":
                if current_app:
                    current_app.logger.info("Manejando intención: deudores_altos")
                return self._handle_deudores_altos(parameters)
            elif intent == "contar_compradores":
                if current_app:
                    current_app.logger.info("Manejando intención: contar_compradores")
                return self._handle_contar_compradores()
            elif intent == "contar_deudores":
                if current_app:
                    current_app.logger.info("Manejando intención: contar_deudores")
                return self._handle_contar_deudores()
            else:
                if current_app:
                    current_app.logger.warning(f"Intención desconocida: {intent}")
                return {
                    "status": "error",
                    "message": "No he entendido tu consulta. Por favor, intenta preguntar sobre los compradores o deudores de nuestra base de datos."
                }
        
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error en el procesamiento del chatbot: {str(e)}")
                current_app.logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": "Ocurrió un error al procesar tu consulta."
            }
    
    def _detect_intent(self, user_message):
        """Detecta la intención utilizando el servicio apropiado según configuración"""
        service_to_use = self.nlp_service_preference
        
        # Si está configurado como 'auto', decidir basado en disponibilidad
        if service_to_use == 'auto':
            if self.deepseek_service is not None:
                service_to_use = 'deepseek'
            elif self.openai_service is not None:
                service_to_use = 'openai'
            else:
                service_to_use = 'fallback'
        
        # Registrar el servicio seleccionado
        if current_app:
            current_app.logger.info(f"Servicio seleccionado para detectar intención: {service_to_use}")
        
        # Usar DeepSeek
        if service_to_use == 'deepseek' and self.deepseek_service is not None:
            try:
                if current_app:
                    current_app.logger.info("Intentando detectar intención con DeepSeek...")
                
                intent_data = self.deepseek_service.detect_intent(user_message)
                
                # Verificar si hay error en la respuesta
                if 'error' in intent_data and intent_data.get('intent') == 'desconocido':
                    if current_app:
                        current_app.logger.warning(f"Error con DeepSeek: {intent_data.get('error')}. Intentando con OpenAI.")
                    
                    # Intentar con OpenAI como segundo respaldo
                    if self.openai_service is not None:
                        try:
                            if current_app:
                                current_app.logger.info("Intentando detectar intención con OpenAI...")
                            
                            intent_data = self.openai_service.detect_intent(user_message)
                            
                            if 'error' not in intent_data or intent_data.get('intent') != 'desconocido':
                                if current_app:
                                    current_app.logger.info("Intención detectada correctamente con OpenAI")
                                return intent_data
                            else:
                                if current_app:
                                    current_app.logger.warning(f"Error con OpenAI: {intent_data.get('error')}. Usando fallback.")
                        except Exception as e:
                            if current_app:
                                current_app.logger.error(f"Excepción con OpenAI: {str(e)}")
                    
                    # Si todo falla, usar fallback
                    if current_app:
                        current_app.logger.info("Usando servicio de fallback como último recurso")
                    return self.fallback_service.detect_intent(user_message)
                
                if current_app:
                    current_app.logger.info("Intención detectada correctamente con DeepSeek")
                return intent_data
            
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Excepción al usar DeepSeek: {str(e)}")
                    current_app.logger.error(traceback.format_exc())
                    current_app.logger.info("Intentando con OpenAI después de excepción...")
                
                # Intentar con OpenAI como segundo respaldo
                if self.openai_service is not None:
                    try:
                        intent_data = self.openai_service.detect_intent(user_message)
                        if 'error' not in intent_data or intent_data.get('intent') != 'desconocido':
                            if current_app:
                                current_app.logger.info("Intención detectada correctamente con OpenAI después de fallar DeepSeek")
                            return intent_data
                    except Exception as e2:
                        if current_app:
                            current_app.logger.error(f"Excepción con OpenAI: {str(e2)}")
                
                # Si todo falla, usar fallback
                if current_app:
                    current_app.logger.info("Usando servicio de fallback como último recurso después de fallos")
                return self.fallback_service.detect_intent(user_message)
        
        # Usar OpenAI
        elif service_to_use == 'openai' and self.openai_service is not None:
            try:
                if current_app:
                    current_app.logger.info("Intentando detectar intención con OpenAI...")
                
                intent_data = self.openai_service.detect_intent(user_message)
                
                # Verificar si hay error en la respuesta
                if 'error' in intent_data and intent_data.get('intent') == 'desconocido':
                    if current_app:
                        current_app.logger.warning(f"Error con OpenAI: {intent_data.get('error')}. Usando fallback.")
                    return self.fallback_service.detect_intent(user_message)
                
                if current_app:
                    current_app.logger.info("Intención detectada correctamente con OpenAI")
                return intent_data
            
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Excepción al usar OpenAI: {str(e)}")
                    current_app.logger.error(traceback.format_exc())
                    current_app.logger.info("Usando servicio de fallback después de excepción con OpenAI")
                return self.fallback_service.detect_intent(user_message)
        
        # Usar fallback en cualquier otro caso
        if current_app:
            if service_to_use != 'fallback':
                current_app.logger.info(f"Servicio {service_to_use} no disponible, usando fallback.")
            else:
                current_app.logger.info("Usando servicio de fallback por configuración.")
                
        return self.fallback_service.detect_intent(user_message)
    
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
        
        if current_app:
            current_app.logger.info(f"Consultando mejores compradores con límite: {limite}")
        
        compradores = consultar_mejores_compradores(limite)
        
        if not compradores:
            if current_app:
                current_app.logger.warning("No se encontraron compradores")
            return {
                "status": "success",
                "message": "No hay compradores registrados en el sistema."
            }
        
        # Formato de la respuesta
        message = f"Los {len(compradores)} mejores compradores son:\n"
        for i, comprador in enumerate(compradores, 1):
            message += f"{i}. {comprador['nombre']} - ${comprador['total_compras']:.2f}\n"
        
        if current_app:
            current_app.logger.info(f"Respuesta generada para mejores compradores: {len(compradores)} resultados")
        
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
        
        if current_app:
            current_app.logger.info(f"Consultando deudores altos con límite: {limite}")
        
        deudores = consultar_deudores_altos(limite)
        
        if not deudores:
            if current_app:
                current_app.logger.warning("No se encontraron deudores")
            return {
                "status": "success",
                "message": "No hay deudores registrados en el sistema."
            }
        
        # Formato de la respuesta
        message = f"Los {len(deudores)} deudores con montos más altos son:\n"
        for i, deudor in enumerate(deudores, 1):
            message += f"{i}. {deudor['nombre']} - ${deudor['monto_adeudado']:.2f}\n"
        
        if current_app:
            current_app.logger.info(f"Respuesta generada para deudores altos: {len(deudores)} resultados")
        
        return {
            "status": "success",
            "message": message.strip(),
            "data": deudores
        }
    
    def _handle_contar_compradores(self):
        """Maneja la intención de contar el número total de compradores"""
        if current_app:
            current_app.logger.info("Contando compradores...")
        
        count = contar_compradores()
        
        if current_app:
            current_app.logger.info(f"Total de compradores: {count}")
        
        return {
            "status": "success",
            "message": f"Hay un total de {count} compradores registrados en el sistema.",
            "data": {"total_compradores": count}
        }
    
    def _handle_contar_deudores(self):
        """Maneja la intención de contar el número total de deudores"""
        if current_app:
            current_app.logger.info("Contando deudores...")
        
        count = contar_deudores()
        
        if current_app:
            current_app.logger.info(f"Total de deudores: {count}")
        
        return {
            "status": "success",
            "message": f"Hay un total de {count} deudores registrados en el sistema.",
            "data": {"total_deudores": count}
        }