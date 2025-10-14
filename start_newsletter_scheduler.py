#!/usr/bin/env python3
"""
Скрипт для запуска приложения с планировщиком рассылок
"""
import uvicorn
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ЗАПУСК ПРИЛОЖЕНИЯ С ПЛАНИРОВЩИКОМ РАССЫЛОК")
    print("=" * 60)
    print(f"🌐 Адрес: http://{settings.host}:{settings.port}")
    print(f"📚 Документация: http://{settings.host}:{settings.port}/docs")
    print("⏰ Планировщик рассылок:")
    print("  - 09:00 - Проверка законодательства")
    print("  - 10:00 - Напоминания о мероприятиях")
    print("  - 11:00 - Массовая рассылка новостей")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
