#!/bin/bash

# Установка дефолтных значений если не заданы
export BACKEND_HOST=${BACKEND_HOST:-localhost}
export BACKEND_PORT=${BACKEND_PORT:-8000}

# Обработка переменных в nginx.conf
envsubst '${BACKEND_HOST} ${BACKEND_PORT}' < /etc/nginx/sites-available/default.template > /etc/nginx/sites-available/default

# Запуск supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
