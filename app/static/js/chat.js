document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    
    // Función para enviar mensajes
    function sendMessage() {
        const message = userInput.value.trim();
        
        if (message === '') return;
        
        // Agregar mensaje del usuario al chat
        addMessage(message, 'user');
        
        // Limpiar input
        userInput.value = '';
        
        // Mostrar indicador de escritura
        showTypingIndicator();
        
        // Enviar mensaje al servidor y procesar respuesta
        fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Ocultar indicador de escritura
            hideTypingIndicator();
            
            // Mostrar respuesta del chatbot
            if (data.status === 'success') {
                addMessage(data.message, 'bot');
            } else {
                addMessage('Ha ocurrido un error: ' + data.message, 'bot');
            }
        })
        .catch(error => {
            // Ocultar indicador de escritura
            hideTypingIndicator();
            
            // Mostrar mensaje de error
            addMessage('Error de conexión. Por favor, intenta de nuevo más tarde.', 'bot');
            console.error('Error:', error);
        });
    }
    
    // Función para agregar un mensaje al chat
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        // Formatear el mensaje con saltos de línea
        messageContent.innerHTML = message.replace(/\n/g, '<br>');
        
        messageElement.appendChild(messageContent);
        chatMessages.appendChild(messageElement);
        
        // Scroll al último mensaje
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Función para mostrar indicador de escritura
    function showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.id = 'typing-indicator';
        typingElement.classList.add('message', 'bot', 'typing-indicator');
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingElement.appendChild(dot);
        }
        
        chatMessages.appendChild(typingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Función para ocultar indicador de escritura
    function hideTypingIndicator() {
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    // Evento click para el botón de enviar
    sendButton.addEventListener('click', sendMessage);
    
    // Evento keydown para enviar con Enter
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Poner el foco en el input
    userInput.focus();
});