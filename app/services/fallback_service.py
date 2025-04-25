import re
from flask import current_app
from app.utils.security import sanitize_input

class FallbackService:
    """
    Servicio de detección de intenciones basado en expresiones regulares.
    No depende de APIs externas, lo que lo hace más robusto pero menos flexible.
    """
    
    def __init__(self):
        # Patrones para detectar intenciones
        self.intent_patterns = {
            'mejores_compradores': [
                r'mejores\s+compradores',
                r'compradores\s+(?:con\s+)?(?:más|mayor|mejor(?:es)?)\s+compras',
                r'quiénes\s+(?:son\s+)?(?:los\s+)?mejores\s+compradores',
                r'(?:los\s+)?compradores\s+(?:que\s+)?más\s+(?:compran|gastan|pagan)',
                r'top\s+compradores',
                r'compradores\s+(?:más|mayores)',
                r'principales\s+compradores',
                r'más\s+compras'
            ],
            'deudores_altos': [
                r'deudores\s+(?:con\s+)?(?:más|mayor(?:es)?|alto(?:s)?)\s+(?:deudas?|montos?)',
                r'quiénes\s+(?:son\s+)?(?:los\s+)?(?:mayores|principales)?\s*deudores',
                r'(?:los\s+)?deudores\s+(?:que\s+)?(?:más|mayor)\s+(?:deben|adeudan)',
                r'top\s+deudores',
                r'deudores\s+(?:más|mayores)',
                r'principales\s+deudores',
                r'mayores\s+deudas'
            ],
            'contar_compradores': [
                r'cuántos\s+compradores',
                r'número\s+(?:total\s+)?(?:de\s+)?compradores',
                r'total\s+(?:de\s+)?compradores',
                r'cantidad\s+(?:de\s+)?compradores',
                r'contar\s+compradores'
            ],
            'contar_deudores': [
                r'cuántos\s+deudores',
                r'número\s+(?:total\s+)?(?:de\s+)?deudores',
                r'total\s+(?:de\s+)?deudores',
                r'cantidad\s+(?:de\s+)?deudores',
                r'contar\s+deudores'
            ]
        }
    
    def initialize(self):
        """Método para mantener compatibilidad con la interfaz"""
        return self
    
    def detect_intent(self, user_message):
        """
        Detecta la intención del usuario a partir de su mensaje usando patrones predefinidos
        """
        # Sanitizar y normalizar la entrada
        message = sanitize_input(user_message).lower()
        
        if current_app:
            current_app.logger.info(f"Detectando intención para: '{message}'")
        
        # Buscar coincidencias con los patrones
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    # Si encuentra una coincidencia, extraer parámetros
                    parameters = self._extract_parameters(message, intent)
                    if current_app:
                        current_app.logger.info(f"Intención detectada: {intent}, parámetros: {parameters}")
                    return {
                        "intent": intent,
                        "parameters": parameters,
                        "confidence": 0.8  # Confianza estimada
                    }
        
        # Si no hay coincidencias claras, intentar detectar intenciones parciales
        best_intent = None
        best_score = 0
        best_params = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = self._calculate_partial_match(message, patterns)
            if score > best_score and score > 0.4:  # Umbral mínimo de confianza
                best_score = score
                best_intent = intent
                best_params = self._extract_parameters(message, intent)
        
        if best_intent:
            if current_app:
                current_app.logger.info(f"Intención parcial detectada: {best_intent}, parámetros: {best_params}, confianza: {best_score}")
            return {
                "intent": best_intent,
                "parameters": best_params,
                "confidence": best_score
            }
        
        # Si no hay ninguna coincidencia, devolver intención desconocida
        if current_app:
            current_app.logger.info("No se detectó ninguna intención clara")
        return {
            "intent": "desconocido",
            "parameters": {},
            "confidence": 0
        }
    
    def _calculate_partial_match(self, message, patterns):
        """Calcula una puntuación de coincidencia parcial basada en palabras clave"""
        message_words = set(message.lower().split())
        
        for pattern in patterns:
            # Convertir el patrón a palabras clave simples
            keywords = re.sub(r'[()[\]{}?+*\\|]', ' ', pattern)
            keywords = re.sub(r'\s+', ' ', keywords).strip()
            pattern_words = set(keywords.lower().split())
            
            # Calcular la intersección de palabras
            common_words = message_words.intersection(pattern_words)
            
            if len(common_words) > 0 and len(pattern_words) > 0:
                # Puntuación: proporción de palabras clave del patrón encontradas
                score = len(common_words) / len(pattern_words)
                if score > 0.5:  # Al menos la mitad de las palabras clave
                    return score
        
        return 0
    
    def _extract_parameters(self, message, intent):
        """Extrae parámetros relevantes según la intención"""
        parameters = {}
        
        # Extraer límite si se menciona
        if intent in ['mejores_compradores', 'deudores_altos']:
            # Buscar menciones de números para el límite
            limit_match = re.search(r'(?:top|primeros|mejores|principales)\s+(\d+)', message)
            if limit_match:
                try:
                    parameters['limite'] = int(limit_match.group(1))
                except ValueError:
                    parameters['limite'] = 3
            
            # Otra forma de especificar límite: "muéstrame 5 compradores"
            limit_match2 = re.search(r'(?:muéstrame|muestra|dame|ver|obtener)\s+(\d+)', message)
            if not 'limite' in parameters and limit_match2:
                try:
                    parameters['limite'] = int(limit_match2.group(1))
                except ValueError:
                    parameters['limite'] = 3
        
        return parameters