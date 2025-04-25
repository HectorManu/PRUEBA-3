# Flask Chatbot API con detección de intenciones

Este proyecto implementa una API REST con Flask para un chatbot que responde preguntas sobre una base de datos ficticia de compradores y deudores. Utiliza OpenAI (si está configurado) o un sistema local basado en expresiones regulares para la detección de intenciones, y está diseñado con una arquitectura modular para facilitar su mantenimiento y escalabilidad.

## Características

- API REST con Flask
- Detección de intenciones híbrida: OpenAI (opcional) con fallback local
- Protección contra prompt injection y otras amenazas de seguridad
- Base de datos SQLite con datos de ejemplo
- Estructura modular y escalable
- Dockerizado para facilitar el despliegue
- Interfaz web sencilla para interactuar con el chatbot

## Estructura del proyecto

```
chatbot-flask-api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chatbot_service.py
│   │   ├── openai_service.py
│   │   └── fallback_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── security.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── chatbot_routes.py
│   ├── templates/
│   │   └── chat.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── chat.js
├── data/
│   └── database.db
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── run.py
```

## Requisitos previos

- Docker y Docker Compose
- Clave API de OpenAI (opcional)

## Configuración inicial

1. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd chatbot-flask-api
   ```

2. Crea un archivo `.env` basado en el ejemplo:
   ```bash
   cp .env.example .env
   ```

3. (Opcional) Edita el archivo `.env` y agrega tu clave de API de OpenAI:
   ```
   OPENAI_API_KEY=tu-clave-api-openai
   ```

4. (Opcional) Configura el modo de detección de intenciones:
   ```
   # Opciones: auto, openai, fallback
   NLP_SERVICE=auto
   ```
   - `auto`: Usa OpenAI si hay una API key, sino usa el sistema local
   - `openai`: Intenta usar OpenAI (requiere API key)
   - `fallback`: Usa siempre el sistema local basado en expresiones regulares

## Ejecución con Docker

1. Construye e inicia los contenedores:
   ```bash
   docker-compose up --build
   ```

2. La aplicación estará disponible en:
   - Interfaz web: `http://localhost:5000`
   - API REST: `http://localhost:5000/chatbot`

## Ejecución local (sin Docker)

1. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```bash
   python run.py
   ```

## Uso de la API

### Endpoint del chatbot

- **URL**: `/chatbot`
- **Método**: `POST`
- **Cuerpo de la solicitud**:
  ```json
  {
    "message": "¿Quiénes son los mejores compradores?"
  }
  ```
- **Ejemplo de respuesta**:
  ```json
  {
    "status": "success",
    "message": "Los 3 mejores compradores son:\n1. Ana Martínez - $9800.00\n2. María López - $7500.75\n3. Juan Pérez - $5000.50",
    "data": [
      {"id": 4, "nombre": "Ana Martínez", "total_compras": 9800.0},
      {"id": 2, "nombre": "María López", "total_compras": 7500.75},
      {"id": 1, "nombre": "Juan Pérez", "total_compras": 5000.5}
    ],
    "processing_time": "0.85s"
  }
  ```

### Verificación de salud

- **URL**: `/chatbot/health`
- **Método**: `GET`
- **Ejemplo de respuesta**:
  ```json
  {
    "status": "success",
    "message": "El servicio del chatbot está funcionando correctamente"
  }
  ```

## Ejemplos de preguntas soportadas

- "¿Quiénes son los mejores compradores?"
- "¿Cuáles son los deudores con montos más altos?"
- "¿Cuántos compradores hay en total?"
- "¿Cuántos deudores hay registrados?"
- "Muéstrame los 5 mejores compradores"
- "¿Cuáles son los principales deudores?"

## Interfaz Web

La aplicación incluye una interfaz web simple para interactuar con el chatbot. Para acceder a ella, simplemente visita `http://localhost:5000` en tu navegador después de iniciar el servidor.

La interfaz proporciona:
- Una ventana de chat para visualizar las conversaciones
- Un campo de entrada para escribir preguntas
- Ejemplos de preguntas que puedes hacer
- Indicador de escritura mientras se procesa la respuesta

## Sistema de Detección de Intenciones

### Modo híbrido

El sistema utiliza un enfoque híbrido para la detección de intenciones:

1. **OpenAI (si está configurado)**
   - Ofrece una comprensión más precisa y natural del lenguaje
   - Requiere una clave API de OpenAI
   - Se configura a través de la variable de entorno `OPENAI_API_KEY`

2. **Sistema local basado en expresiones regulares (fallback)**
   - Funciona sin conexión a internet
   - No requiere claves API ni servicios externos
   - Ofrece respuesta rápida y confiable
   - Se usa automáticamente cuando OpenAI no está disponible

3. **Modo de selección**
   - Controlado por la variable `NLP_SERVICE` en el archivo `.env`
   - Valores posibles: `auto`, `openai`, `fallback`

## Seguridad

La aplicación incluye medidas de seguridad para proteger contra:

- Prompt injection
- Inyección SQL
- XSS (Cross-Site Scripting)
- Manipulación de parámetros

## Extensión

Para agregar nuevas intenciones:

1. Actualiza el sistema de intenciones en ambos servicios:
   - `app/services/openai_service.py` (prompt system)
   - `app/services/fallback_service.py` (patrones regex)
2. Implementa el manejador de la intención en `app/services/chatbot_service.py`
3. Agrega nuevas consultas en `app/models/database.py` si es necesario

## Solución de problemas

### Error con la API de OpenAI
Si encuentras errores relacionados con la API de OpenAI:
1. Verifica que la clave API sea válida
2. Configura `NLP_SERVICE=fallback` en el archivo `.env` para usar solo el sistema local

### Error de base de datos
Si encuentras errores relacionados con la base de datos, puedes reiniciar la aplicación para recrear la base de datos con los datos de ejemplo:
```bash
docker-compose down
docker-compose up --build
```
