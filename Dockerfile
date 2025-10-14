# Использование официального образа Python
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов проекта
COPY . .

# Создание необходимых директорий
RUN mkdir -p reports generated_documents templates/documents /var/log/supervisor

# Копирование конфигурации Nginx
COPY nginx.conf /etc/nginx/sites-available/default

# Копирование конфигурации Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# Настройки режима (можно переопределить через docker-compose)
ENV ENVIRONMENT=${ENVIRONMENT:-production}
# ENV PROXY_ENABLED=True  # Управляется через config.py
ENV PROXY_IP=45.152.197.36
ENV PROXY_PORT=8000
ENV PROXY_LOGIN=wvJF4w
ENV PROXY_PASSWORD=0C7w1U
# BASE_URL должен приходить из окружения/оркестратора
ENV DEBUG=False
# Открытие портов
EXPOSE 80 8000

# Команда запуска
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
