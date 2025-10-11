#!/usr/bin/env python3
"""
Скрипт для ручного запуска рассылок
Использование: python manual_newsletter.py [тип_рассылки]
Типы рассылок: legislation, newsletter, reminders, all
"""
import asyncio
import sys
import os
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrations.gmail_service import gmail_service
from integrations.google_sheets import google_sheets_service
from services.monitoring_service import monitoring_service
from config import settings
from logger_config import get_logger, log_success, log_error, log_warning

# Инициализация логгера
logger = get_logger(__name__)

async def run_legislation_check():
    """Запуск проверки законодательства и рассылки уведомлений"""
    print("\n" + "="*60)
    print("ЗАПУСК: Проверка законодательства")
    print("="*60)
    
    try:
        logger.info("Начинаем проверку обновлений законодательства...")
        updates = await monitoring_service.check_legislation_updates()
        log_success(logger, f"Проверка завершена. Найдено обновлений: {len(updates)}")
        
        # Отправляем уведомления всем пользователям, если есть обновления
        if updates:
            logger.info(f"Подготовка рассылки об обновлениях ({len(updates)} шт.)")
            subject = "Обновления законодательства МСП"
            body = """Здравствуйте!

Найдены новые обновления в законодательстве для малого и среднего бизнеса:

"""
            for update in updates[:5]:
                body += f"• {update['title']}\n  {update['url']}\n\n"
            
            body += """Рекомендуем ознакомиться с новыми изменениями.

С уважением,
Команда "Опора России"
"""
            
            # Получаем список всех пользователей с email
            logger.info("Получаем список пользователей из Google Sheets...")
            users = google_sheets_service.get_all_users()
            recipients = [user.get('Email') for user in users if user.get('Email')]
            
            # Добавляем админа в список получателей
            if settings.gmail_user and settings.gmail_user not in recipients:
                recipients.append(settings.gmail_user)
                logger.debug(f"Добавлен администратор: {settings.gmail_user}")
            
            if recipients:
                logger.info(f"Начинаем отправку рассылки {len(recipients)} получателям...")
                
                sent_count = gmail_service.send_bulk_email_with_delay(
                    recipients=recipients,
                    subject=subject,
                    body=body,
                    html=False,
                    delay_seconds=2  # 2 секунды задержки между отправками
                )
                
                log_success(logger, "Рассылка об обновлениях законодательства завершена", 
                           sent=sent_count, total=len(recipients), 
                           success_rate=f"{(sent_count/len(recipients)*100):.1f}%")
            else:
                log_warning(logger, "Нет получателей для рассылки об обновлениях")
        else:
            logger.info("Обновлений законодательства не найдено, рассылка не требуется")
            
    except Exception as e:
        log_error(logger, "Ошибка при проверке законодательства", error=e)

async def run_bulk_newsletter():
    """Запуск массовой рассылки новостей"""
    print("\n" + "="*60)
    print("ЗАПУСК: Массовая рассылка новостей")
    print("="*60)
    
    try:
        # Получаем список всех пользователей с email
        logger.info("Загружаем список пользователей для рассылки...")
        users = google_sheets_service.get_all_users()
        recipients = [user.get('Email') for user in users if user.get('Email')]
        logger.info(f"Пользователей с email: {len(recipients)}")
        
        # Добавляем админа в список получателей
        if settings.gmail_user and settings.gmail_user not in recipients:
            recipients.append(settings.gmail_user)
            logger.debug(f"Добавлен администратор: {settings.gmail_user}")
        
        if not recipients:
            log_warning(logger, "Нет получателей для массовой рассылки")
            return
        
        # Тема и содержание рассылки
        subject = "Еженедельная рассылка от Опора России"
        body = f"""Здравствуйте!

Добро пожаловать в еженедельную рассылку новостей от "Опора России"!

Время отправки: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

В этом выпуске:
• Новые возможности нашего AI-ассистента
• Актуальные изменения в законодательстве МСП
• Предстоящие мероприятия и семинары
• Полезные советы для предпринимателей

Напоминание:
Наш AI-ассистент готов помочь вам с:
- Созданием документов и заявок
- Консультациями по законодательству
- Анализом бизнес-процессов
- Ответами на вопросы по МСП

Доступ к ассистенту:
http://localhost:8000/static/main-interface.html

Если у вас есть вопросы или предложения, просто напишите нам!

С уважением,
Команда "Опора России"

---
Если вы не хотите получать эти рассылки, ответьте на это письмо с темой "Отписаться".
"""
        
        logger.info(f"Начинаем отправку рассылки {len(recipients)} получателям...")
        logger.debug("Задержка между отправками: 2 секунды")
        
        sent_count = gmail_service.send_bulk_email_with_delay(
            recipients=recipients,
            subject=subject,
            body=body,
            html=False,
            delay_seconds=2  # 2 секунды задержки между отправками
        )
        
        log_success(logger, "Массовая рассылка завершена", 
                   sent=sent_count, total=len(recipients), 
                   success_rate=f"{(sent_count/len(recipients)*100):.1f}%")
        
    except Exception as e:
        log_error(logger, "Ошибка при массовой рассылке", error=e)

async def run_event_reminders():
    """Запуск напоминаний о мероприятиях"""
    print("\n" + "="*60)
    print("ЗАПУСК: Напоминания о мероприятиях")
    print("="*60)
    
    try:
        # Получаем список пользователей
        users = google_sheets_service.get_all_users()
        recipients = [user.get('Email') for user in users if user.get('Email')]
        
        if not recipients:
            log_warning(logger, "Нет получателей для напоминаний")
            return
        
        # Пример напоминания (можно расширить логику)
        logger.info(f"Отправка напоминаний {len(recipients)} получателям...")
        
        sent_count = 0
        for recipient in recipients:
            result = gmail_service.send_event_reminder(
                to_email=recipient,
                event_title="Еженедельный семинар по МСП",
                event_date="2025-10-15 14:00",
                event_description="Приглашаем вас на еженедельный семинар по поддержке малого и среднего бизнеса."
            )
            if result:
                sent_count += 1
        
        log_success(logger, "Напоминания о мероприятиях отправлены", 
                   sent=sent_count, total=len(recipients), 
                   success_rate=f"{(sent_count/len(recipients)*100):.1f}%")
        
    except Exception as e:
        log_error(logger, "Ошибка при отправке напоминаний", error=e)

async def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("Использование: python manual_newsletter.py [тип_рассылки]")
        print("Типы рассылок:")
        print("  legislation - проверка законодательства и уведомления")
        print("  newsletter  - массовая рассылка новостей")
        print("  reminders   - напоминания о мероприятиях")
        print("  all         - все рассылки")
        return
    
    newsletter_type = sys.argv[1].lower()
    
    print("ЗАПУСК РУЧНОЙ РАССЫЛКИ")
    print("="*60)
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Тип рассылки: {newsletter_type}")
    print(f"Gmail user: {settings.gmail_user}")
    
    # Проверяем инициализацию сервисов
    print(f"\nGmail Service: {'Инициализирован' if gmail_service.service else 'Не инициализирован'}")
    print(f"Google Sheets: {'Подключен' if google_sheets_service.client else 'Не подключен'}")
    
    if newsletter_type == "legislation":
        await run_legislation_check()
    elif newsletter_type == "newsletter":
        await run_bulk_newsletter()
    elif newsletter_type == "reminders":
        await run_event_reminders()
    elif newsletter_type == "all":
        await run_legislation_check()
        await run_bulk_newsletter()
        await run_event_reminders()
    else:
        print(f"Неизвестный тип рассылки: {newsletter_type}")
        return
    
    print("\n" + "="*60)
    print("РАССЫЛКА ЗАВЕРШЕНА")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
