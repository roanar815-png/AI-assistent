# AI Ассистент для сайта "Опора России"

Умный чат-бот для поддержки малого и среднего предпринимательства с функциями диалога, анализа, обработки заявок и автоматизации бизнес-процессов.

## 🚀 Возможности

### 1. **Интеллектуальный диалог**
- Общение на естественном языке через OpenAI GPT
- Сбор и сохранение данных пользователей
- История диалогов в Google Sheets

### 2. **Анализ и прогнозирование МСП**
- AI-анализ трендов малого и среднего бизнеса
- Прогнозы и рекомендации
- Актуальная информация о перспективах

### 3. **Обработка заявок**
- Прием заявок на вступление в "Опору России"
- Автоматическое сохранение в Google Sheets
- Формирование отчетов по заявкам

### 4. **Мониторинг законодательства**
- Автоматическая проверка изменений (раз в день)
- Парсинг официальных источников
- Уведомления администраторам

### 5. **Рассылки и напоминания**
- Email-рассылки через Gmail API
- Напоминания о мероприятиях
- Персонализированные сообщения

### 6. **Отчеты и аналитика**
- Отчеты по пользователям
- Статистика заявок
- Анализ обратной связи
- Экспорт в CSV/PDF

### 7. **Автоматическое заполнение документов**
- Шаблоны жалоб, протоколов, договоров
- Генерация DOCX файлов
- Подстановка данных из Google Sheets

### 8. **Обратная связь**
- Сбор вопросов, жалоб, предложений
- AI-анализ обратной связи
- Формирование сводных отчетов

## 📋 Требования

- Python 3.9+
- Google Sheets API credentials
- OpenAI API key
- Gmail API credentials (опционально)

## 🛠 Установка

### 1. Клонируйте репозиторий

```bash
git clone <repository-url>
cd AIAI
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте Google Sheets API

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект
3. Включите Google Sheets API и Google Drive API
4. Создайте Service Account
5. Скачайте JSON файл с credentials
6. Переименуйте файл в `credentials.json` и поместите в корень проекта
7. Создайте Google Sheets таблицу и предоставьте доступ Service Account email

### 5. Настройте OpenAI API

1. Получите API ключ на [platform.openai.com](https://platform.openai.com/)
2. Добавьте его в файл `.env`

### 6. Создайте файл `.env`

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Google Sheets & Gmail
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Application Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Monitoring URLs
LEGISLATION_URLS=https://www.consultant.ru/law/hotdocs/,https://government.ru/news/

# Email Settings
GMAIL_USER=your_email@gmail.com
```

### 7. Настройте Gmail API (опционально)

Для отправки email-рассылок:

1. В Google Cloud Console включите Gmail API
2. Создайте OAuth 2.0 credentials
3. Скачайте `credentials.json`
4. При первом запуске пройдите авторизацию

## 🚀 Запуск

### Backend

```bash
python main.py
```

Или с uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (чат-виджет)

Откройте файл `static/chat-widget.html` в браузере или разместите виджет на вашем сайте:

```html
<!-- Подключение виджета на сайте -->
<link rel="stylesheet" href="http://localhost:8000/static/chat-widget.css">
<script src="http://localhost:8000/static/chat-widget.js"></script>
```

## 📚 API Documentation

После запуска сервера документация доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Основные эндпоинты

#### Чат
- `POST /api/chat/message` - Отправить сообщение
- `GET /api/chat/history/{user_id}` - Получить историю
- `DELETE /api/chat/history/{user_id}` - Очистить историю

#### Заявки
- `POST /api/applications/submit` - Подать заявку
- `GET /api/applications/list` - Список заявок
- `GET /api/applications/{user_id}` - Заявки пользователя

#### Отчеты
- `POST /api/reports/generate` - Создать отчет
- `GET /api/reports/download` - Скачать отчет
- `GET /api/reports/statistics` - Статистика

#### Документы
- `POST /api/documents/generate` - Создать документ
- `GET /api/documents/download` - Скачать документ

#### Обратная связь
- `POST /api/feedback/submit` - Отправить обратную связь
- `GET /api/feedback/list` - Список обратной связи
- `GET /api/feedback/analysis` - Анализ обратной связи

#### Анализ
- `GET /api/analysis/sme-trends` - Анализ трендов МСП

## 🏗 Архитектура проекта

```
AIAI/
├── api/                    # API роутеры
│   ├── chat.py            # Чат с ассистентом
│   ├── applications.py    # Заявки
│   ├── reports.py         # Отчеты
│   ├── documents.py       # Документы
│   ├── feedback.py        # Обратная связь
│   └── analysis.py        # Анализ МСП
├── integrations/          # Интеграции с внешними API
│   ├── google_sheets.py   # Google Sheets
│   ├── openai_service.py  # OpenAI
│   └── gmail_service.py   # Gmail
├── models/                # Pydantic модели
│   └── schemas.py
├── services/              # Бизнес-логика
│   ├── assistant_service.py    # Логика ассистента
│   ├── report_service.py       # Отчеты
│   ├── document_service.py     # Документы
│   └── monitoring_service.py   # Мониторинг
├── static/                # Фронтенд
│   ├── chat-widget.html
│   ├── chat-widget.css
│   └── chat-widget.js
├── templates/             # Шаблоны документов
├── reports/               # Сгенерированные отчеты
├── generated_documents/   # Сгенерированные документы
├── config.py             # Конфигурация
├── main.py               # Главный файл приложения
└── requirements.txt      # Зависимости
```

## 📅 Планировщик задач

Приложение включает автоматические задачи:

- **09:00** - Проверка изменений в законодательстве МСП
- **10:00** - Отправка напоминаний о мероприятиях

## 🎨 Использование чат-виджета

### Базовая интеграция

```html
<!DOCTYPE html>
<html>
<head>
    <title>Мой сайт</title>
    <link rel="stylesheet" href="http://localhost:8000/static/chat-widget.css">
</head>
<body>
    <!-- Ваш контент -->
    
    <script src="http://localhost:8000/static/chat-widget.js"></script>
</body>
</html>
```

### Настройка API URL

В файле `static/chat-widget.js` измените URL:

```javascript
this.apiUrl = 'https://your-domain.com/api';
```

## 📊 Работа с Google Sheets

Структура таблиц создается автоматически:

- **Users** - Данные пользователей
- **Applications** - Заявки на вступление
- **Feedback** - Обратная связь
- **ChatHistory** - История диалогов
- **Events** - Мероприятия
- **Legislation** - Изменения законодательства

## 🔒 Безопасность

⚠️ **Важно для продакшена:**

1. Измените CORS настройки в `main.py`
2. Используйте HTTPS
3. Добавьте rate limiting
4. Храните `.env` в безопасном месте
5. Не коммитьте `credentials.json`
6. Настройте firewall правила

## 🐛 Решение проблем

### Google Sheets API ошибки

```bash
# Проверьте права доступа Service Account
# Email должен быть добавлен в Google Sheets с правами редактора
```

### OpenAI API ошибки

```bash
# Проверьте баланс на аккаунте
# Убедитесь, что API ключ активен
```

### CORS ошибки

```python
# В main.py измените allow_origins
allow_origins=["https://your-domain.com"]
```

## 📝 Примеры использования

### Отправка сообщения через API

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/message",
    json={
        "user_id": "user_123",
        "message": "Расскажи о трендах МСП"
    }
)

print(response.json())
```

### Создание отчета

```python
response = requests.post(
    "http://localhost:8000/api/reports/generate",
    json={
        "report_type": "users",
        "format": "csv"
    }
)

print(response.json())
```

## 🤝 Поддержка

Для вопросов и предложений создавайте issues в репозитории.

## 📄 Лицензия

MIT License

## 🎯 Roadmap

- [ ] Websocket поддержка для real-time чата
- [ ] Многоязычность (i18n)
- [ ] Голосовой ввод
- [ ] Интеграция с Telegram Bot
- [ ] Dashboard для администраторов
- [ ] Machine Learning для предиктивной аналитики
- [ ] Интеграция с 1С

---

**Разработано для "Опора России"** 🇷🇺

