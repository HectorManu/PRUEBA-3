import re
import html

def sanitize_input(text):
    """
    Sanitiza la entrada del usuario para prevenir prompt injection y otros ataques
    """
    if text is None:
        return ""
        
    # Convertir a string si no lo es
    if not isinstance(text, str):
        text = str(text)
    
    # Limitar la longitud del texto
    text = text[:1000]  # Limitar a 1000 caracteres
    
    # Escapar caracteres HTML para prevenir XSS
    text = html.escape(text)
    
    # Remover caracteres de control y secuencias potencialmente maliciosas
    # Eliminar caracteres que podrían manipular el prompt
    text = re.sub(r'[\\`\*_\{\}\[\]\(\)#\+\-\.!]', ' ', text)
    
    # Eliminar palabras clave que podrían ser utilizadas para manipular el sistema
    prompt_injection_patterns = [
        r'\bignora\b', r'\bolvida\b', r'\bsistema\b', r'\binstrucciones\b',
        r'\bprompt\b', r'\bdesatender\b', r'\boverride\b', r'\bbypass\b',
        r'\badvertencia\b', r'\balerta\b', r'\bwarning\b', r'\balert\b',
        r'\bsql\b', r'\bselect\b', r'\binsert\b', r'\bupdate\b', r'\bdelete\b',
        r'\bdrop\b', r'\balter\b', r'\bcreate\b', r'\bexecute\b', r'\bexec\b'
    ]
    
    for pattern in prompt_injection_patterns:
        text = re.sub(pattern, '[redactado]', text, flags=re.IGNORECASE)
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def validate_json_input(json_data, required_fields=None):
    """
    Valida que el JSON de entrada tenga los campos requeridos
    """
    if not json_data:
        return False, "No se proporcionaron datos JSON"
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in json_data]
        if missing_fields:
            return False, f"Faltan campos requeridos: {', '.join(missing_fields)}"
    
    return True, ""