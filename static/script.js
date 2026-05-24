document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const messagesContainer = document.getElementById('messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.querySelector('.input-area button:not(#voice-btn)');
    const voiceBtn = document.getElementById('voice-btn');

    // ==================== SEND MESSAGE ====================
    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message
        appendMessage('user', message);
        userInput.value = '';
        userInput.focus();

        // Show typing indicator
        const typingId = showTypingIndicator();

        try {
            const response = await fetch('/get_response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Remove typing and show bot response
            removeTypingIndicator(typingId);
            setTimeout(() => {
                appendMessage('bot', data.response);
            }, 600);

        } catch (error) {
            removeTypingIndicator(typingId);
            appendMessage('bot', 'Sorry, I encountered an error. Please try again.');
            console.error('Error:', error);
        }
    };

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // ==================== APPEND MESSAGE ====================
    const appendMessage = (sender, text) => {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);

        const avatarIcon = sender === 'bot' ? '<i class="fa-solid fa-robot"></i>' : '';
        
        // Process text (basic formatting)
        const formattedText = text.replace(/\n/g, '<br>');

        msgDiv.innerHTML = sender === 'bot' 
            ? `<div class="avatar">${avatarIcon}</div><div class="bubble">${formattedText}</div>`
            : `<div class="bubble">${formattedText}</div>`;

        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
    };

    // ==================== TYPING INDICATOR ====================
    const showTypingIndicator = () => {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.classList.add('message', 'bot', 'typing');
        div.id = id;
        div.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="bubble">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        `;
        messagesContainer.appendChild(div);
        scrollToBottom();
        return id;
    };

    const removeTypingIndicator = (id) => {
        const el = document.getElementById(id);
        if (el) el.remove();
    };

    const scrollToBottom = () => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    };

    // ==================== VOICE INPUT ====================
    window.startVoice = () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Voice input is not supported in this browser. Please use Chrome or Edge.');
            return;
        }

        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        // Visual feedback
        voiceBtn.style.transform = 'scale(1.2)';
        voiceBtn.style.boxShadow = '0 0 30px rgba(255, 95, 95, 0.8)';
        
        recognition.start();

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            voiceBtn.style.transform = 'scale(1)';
            voiceBtn.style.boxShadow = '';
            sendMessage();
        };

        recognition.onerror = (event) => {
            console.error('Voice error:', event.error);
            voiceBtn.style.transform = 'scale(1)';
            voiceBtn.style.boxShadow = '';
        };

        recognition.onend = () => {
            voiceBtn.style.transform = 'scale(1)';
            voiceBtn.style.boxShadow = '';
        };
    };

    // ==================== CLEAR CHAT ====================
    window.clearChat = () => {
        if (confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
            window.location.href = '/clear_chat';
        }
    };
});