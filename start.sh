#!/bin/bash

# Обработка переменных в nginx.conf
envsubst '${BACKEND_HOST} ${BACKEND_PORT}' < /etc/nginx/sites-available/default.template > /etc/nginx/sites-available/default

# Запуск supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
