/**
 * AI Ассистент - Чат-виджет
 */

class ChatWidget {
    constructor() {
        this.apiUrl = 'http://localhost/api';  // API через Nginx на порту 80
        this.userId = this.generateUserId();
        this.isOpen = false;
        
        // Защита от ошибок расширений браузера
        this.setupErrorHandling();
        
        this.initElements();
        this.attachEventListeners();
    }
    
    setupErrorHandling() {
        // Подавление ошибок расширений браузера
        const originalError = console.error;
        console.error = (...args) => {
            const message = args.join(' ');
            if (message.includes('message port closed') || 
                message.includes('message channel closed') ||
                message.includes('runtime.lastError')) {
                console.warn('Browser extension error suppressed:', message);
                return;
            }
            originalError.apply(console, args);
        };
        
        // Обработка необработанных промисов от расширений
        window.addEventListener('unhandledrejection', (event) => {
            if (event.reason && event.reason.message && (
                event.reason.message.includes('message channel closed') ||
                event.reason.message.includes('message port closed') ||
                event.reason.message.includes('runtime.lastError')
            )) {
                console.warn('Browser extension promise rejection suppressed:', event.reason.message);
                event.preventDefault();
            }
        });
    }
    
    initElements() {
        this.chatButton = document.getElementById('chat-button');
        this.chatWidget = document.getElementById('chat-widget');
        this.closeButton = document.getElementById('close-chat');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.quickActions = document.querySelectorAll('.quick-action-btn');
    }
    
    attachEventListeners() {
        this.chatButton.addEventListener('click', () => this.toggleChat());
        this.closeButton.addEventListener('click', () => this.toggleChat());
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        this.quickActions.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.getAttribute('data-action');
                this.handleQuickAction(action);
            });
        });
    }
    
    toggleChat() {
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            this.chatWidget.classList.add('active');
            this.chatButton.classList.add('hidden');
            this.chatInput.focus();
        } else {
            this.chatWidget.classList.remove('active');
            this.chatButton.classList.remove('hidden');
        }
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        
        if (!message) return;
        
        // Отображаем сообщение пользователя
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        
        // Показываем индикатор печати
        this.showTypingIndicator();
        
        try {
            // Отправляем запрос к API
            const response = await fetch(`${this.apiUrl}/chat/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    message: message
                })
            });
            
            const data = await response.json();
            
            // Удаляем индикатор печати
            this.hideTypingIndicator();
            
            // Отображаем ответ бота
            this.addMessage(data.response, 'bot');
            
            // Показываем предложение документа если есть
            if (data.document_suggestion && data.document_suggestion.suggested) {
                this.showDocumentSuggestion(data.document_suggestion);
            }
            
        } catch (error) {
            console.error('Ошибка отправки сообщения:', error);
            this.hideTypingIndicator();
            this.addMessage('Извините, произошла ошибка. Попробуйте позже.', 'bot');
        }
    }
    
    addMessage(text, sender, attachments = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Конвертируем markdown в HTML и создаем кликабельные ссылки
        const formattedText = this.formatMessage(text);
        contentDiv.innerHTML = formattedText;
        
        messageDiv.appendChild(contentDiv);
        
        // Добавляем вложения если есть
        if (attachments && attachments.length > 0) {
            const attachmentsDiv = document.createElement('div');
            attachmentsDiv.className = 'message-attachments';
            
            attachments.forEach(attachment => {
                const link = document.createElement('a');
                link.href = attachment.url;
                link.download = attachment.filename;
                link.className = 'attachment-link';
                link.innerHTML = `📄 ${attachment.filename}`;
                attachmentsDiv.appendChild(link);
            });
            
            messageDiv.appendChild(attachmentsDiv);
        }
        
        this.chatMessages.appendChild(messageDiv);
        
        // Прокручиваем вниз
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        if (!text) return '';
        
        // Экранируем HTML теги
        let formatted = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        
        // Конвертируем markdown **жирный** в HTML
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Конвертируем URLs в кликабельные ссылки
        const urlPattern = /(https?:\/\/[^\s]+)/g;
        formatted = formatted.replace(urlPattern, (url) => {
            // Проверяем, содержит ли URL путь к документу
            if (url.includes('/api/documents/download')) {
                return `<a href="${url}" target="_blank" class="download-link" download style="display: inline-block; margin: 10px 0; padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">📥 Скачать документ</a>`;
            }
            return `<a href="${url}" target="_blank" class="message-link">${url}</a>`;
        });
        
        // Конвертируем переносы строк в <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message bot-message';
        indicator.id = 'typing-indicator';
        
        const content = document.createElement('div');
        content.className = 'typing-indicator';
        content.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        indicator.appendChild(content);
        this.chatMessages.appendChild(indicator);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    showDocumentSuggestion(suggestion) {
        // Если документ уже создан, показываем красивую карточку с ссылкой на скачивание
        if (suggestion.created_document && suggestion.created_document.status === 'success') {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message document-created';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.style.background = 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)';
            contentDiv.style.borderLeft = '4px solid #28a745';
            contentDiv.style.padding = '20px';
            contentDiv.style.borderRadius = '15px';
            contentDiv.style.boxShadow = '0 4px 12px rgba(40, 167, 69, 0.2)';
            
            contentDiv.innerHTML = `
                <div style="text-align: center;">
                    <h3 style="margin: 0 0 10px 0; color: #155724; font-size: 18px;">✅ Документ готов!</h3>
                    <p style="margin: 0 0 15px 0; color: #155724;">Ваш документ успешно создан и готов к скачиванию.</p>
                    <a href="http://localhost${suggestion.created_document.download_url}" 
                       style="display: inline-block; background: linear-gradient(135deg, #28a745 0%, #218838 100%); 
                              color: white; text-decoration: none; padding: 15px 25px; 
                              border-radius: 10px; text-align: center; margin-top: 15px;
                              font-weight: bold; transition: all 0.3s; box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);"
                       onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(40, 167, 69, 0.4)';"
                       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(40, 167, 69, 0.3)';">
                        📥 Скачать документ
                    </a>
                </div>
            `;
            
            messageDiv.appendChild(contentDiv);
            this.chatMessages.appendChild(messageDiv);
            this.scrollToBottom();
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message document-suggestion';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Используем formatMessage для правильного форматирования
        contentDiv.innerHTML = this.formatMessage(suggestion.message);
        
        messageDiv.appendChild(contentDiv);
        
        // Создаем список шаблонов только если документ не был создан автоматически
        if (suggestion.templates && suggestion.templates.length > 0 && !suggestion.created_document) {
            const templatesDiv = document.createElement('div');
            templatesDiv.className = 'templates-list';
            
            suggestion.templates.forEach(template => {
                const templateButton = document.createElement('button');
                templateButton.className = 'template-button';
                templateButton.textContent = template.name;
                templateButton.onclick = () => this.createDocument(template.template_id, suggestion.user_data, suggestion.conversation_data);
                templatesDiv.appendChild(templateButton);
            });
            
            messageDiv.appendChild(templatesDiv);
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    async createDocument(templateId, userData, conversationData) {
        try {
            this.showTypingIndicator();
            
            const response = await fetch(`${this.apiUrl}/chat/create-document`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    template_id: templateId,
                    user_data: userData,
                    conversation_data: conversationData,
                    send_email: true
                })
            });
            
            const data = await response.json();
            this.hideTypingIndicator();
            
            if (data.status === 'success') {
                this.addMessage(data.message, 'bot', [{
                    url: data.download_url,
                    filename: data.filepath.split('/').pop()
                }]);
            } else {
                this.addMessage(`Ошибка: ${data.message}`, 'bot');
            }
            
        } catch (error) {
            console.error('Ошибка создания документа:', error);
            this.hideTypingIndicator();
            this.addMessage('Ошибка создания документа. Попробуйте позже.', 'bot');
        }
    }
    
    async handleQuickAction(action) {
        let message = '';
        
        switch(action) {
            case 'sme-analysis':
                message = 'Покажи анализ и прогноз для малого и среднего предпринимательства';
                break;
            case 'application':
                message = 'Хочу подать заявку на вступление в Опору России';
                break;
            case 'events':
                message = 'Какие мероприятия запланированы?';
                break;
            case 'legislation':
                message = 'Расскажи о последних изменениях в законодательстве для МСП';
                break;
        }
        
        if (message) {
            this.chatInput.value = message;
            this.sendMessage();
        }
    }
    
    generateUserId() {
        // Проверяем, есть ли уже ID в localStorage
        let userId = localStorage.getItem('chat_user_id');
        
        if (!userId) {
            // Генерируем новый ID
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('chat_user_id', userId);
        }
        
        return userId;
    }
}

// Инициализация виджета при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.chatWidget = new ChatWidget();
});

