"""
Главный файл приложения FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import os

from config import settings
from api import chat, applications, reports, documents, feedback, analysis
from services import monitoring_service
from integrations import gmail_service, google_sheets_service
from logger_config import get_logger, log_success, log_error, log_warning

# Инициализация логгера
logger = get_logger(__name__)


# Планировщик задач
scheduler = AsyncIOScheduler()


async def scheduled_legislation_check():
    """
    Запланированная проверка законодательства (раз в день)
    """
    logger.info("=" * 80)
    logger.info("🔍 ЗАПУСК ПЛАНОВОГО МОНИТОРИНГА ЗАКОНОДАТЕЛЬСТВА")
    logger.info("=" * 80)
    
    try:
        logger.info("Начинаем проверку обновлений законодательства...")
        updates = await monitoring_service.check_legislation_updates()
        log_success(logger, f"Проверка завершена. Найдено обновлений: {len(updates)}")
        
        # Отправляем уведомления всем пользователям, если есть обновления
        if updates:
            logger.info(f"📧 Подготовка рассылки об обновлениях ({len(updates)} шт.)")
            subject = "📋 Обновления законодательства МСП"
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
                logger.info(f"📬 Начинаем рассылку {len(recipients)} получателям...")
                sent_count = gmail_service.send_bulk_email(
                    recipients=recipients,
                    subject=subject,
                    body=body,
                    html=False
                )
                log_success(logger, f"Рассылка завершена", 
                           sent=sent_count, total=len(recipients))
            else:
                log_warning(logger, "Нет получателей для рассылки обновлений законодательства")
        else:
            logger.info("ℹ️ Новых обновлений законодательства не найдено")
                
    except Exception as e:
        log_error(logger, "Ошибка при проверке законодательства", error=e)


async def scheduled_event_reminders():
    """
    Запланированная отправка напоминаний о мероприятиях
    """
    logger.info("=" * 80)
    logger.info("📅 ПРОВЕРКА НАПОМИНАНИЙ О МЕРОПРИЯТИЯХ")
    logger.info("=" * 80)
    
    try:
        logger.info("Получаем список мероприятий из Google Sheets...")
        events = google_sheets_service.get_events()
        logger.info(f"Найдено мероприятий: {len(events) if events else 0}")
        # Логика отправки напоминаний
        # (можно проверить дату и отправить за день до мероприятия)
        log_success(logger, "Проверка напоминаний завершена")
    except Exception as e:
        log_error(logger, "Ошибка при отправке напоминаний", error=e)


async def scheduled_bulk_newsletter():
    """
    Запланированная массовая рассылка новостей (раз в день)
    """
    logger.info("=" * 80)
    logger.info("📰 ЗАПУСК МАССОВОЙ РАССЫЛКИ НОВОСТЕЙ")
    logger.info("=" * 80)
    
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
        subject = "📢 Еженедельная рассылка от Опора России"
        body = """Здравствуйте!

Добро пожаловать в еженедельную рассылку новостей от "Опора России"!

🎯 В этом выпуске:
• Новые возможности нашего AI-ассистента
• Актуальные изменения в законодательстве МСП
• Предстоящие мероприятия и семинары
• Полезные советы для предпринимателей

💡 Напоминание:
Наш AI-ассистент готов помочь вам с:
- Созданием документов и заявок
- Консультациями по законодательству
- Анализом бизнес-процессов
- Ответами на вопросы по МСП

🌐 Доступ к ассистенту:
http://localhost:8000/static/main-interface.html

Если у вас есть вопросы или предложения, просто напишите нам!

С уважением,
Команда "Опора России"

---
Если вы не хотите получать эти рассылки, ответьте на это письмо с темой "Отписаться".
"""
        
        logger.info(f"📬 Начинаем отправку рассылки {len(recipients)} получателям...")
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    # ==================== STARTUP ====================
    logger.info("=" * 80)
    logger.info("🚀 ЗАПУСК ПРИЛОЖЕНИЯ AI АССИСТЕНТ ОПОРА РОССИИ")
    logger.info("=" * 80)
    
    # Создание необходимых директорий
    logger.info("📁 Создание рабочих директорий...")
    directories = ["reports", "generated_documents", "templates/documents", "logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"  ✓ {directory}")
    log_success(logger, "Все директории созданы")
    
    # Запуск планировщика
    logger.info("⏰ Настройка планировщика задач...")
    
    scheduler.add_job(
        scheduled_legislation_check,
        CronTrigger(hour=9, minute=0),  # Каждый день в 9:00
        id="legislation_check"
    )
    logger.debug("  ✓ Мониторинг законодательства: ежедневно в 09:00")
    
    scheduler.add_job(
        scheduled_event_reminders,
        CronTrigger(hour=10, minute=0),  # Каждый день в 10:00
        id="event_reminders"
    )
    logger.debug("  ✓ Напоминания о мероприятиях: ежедневно в 10:00")
    
    scheduler.add_job(
        scheduled_bulk_newsletter,
        CronTrigger(hour=11, minute=0),  # Каждый день в 11:00
        id="bulk_newsletter"
    )
    logger.debug("  ✓ Массовая рассылка новостей: ежедневно в 11:00")
    
    scheduler.start()
    log_success(logger, "Планировщик задач запущен и готов к работе")
    
    logger.info("=" * 80)
    logger.info("✅ ПРИЛОЖЕНИЕ УСПЕШНО ЗАПУЩЕНО И ГОТОВО К РАБОТЕ")
    logger.info(f"🌐 API доступно по адресу: http://{settings.host}:{settings.port}")
    logger.info(f"📚 Документация: http://{settings.host}:{settings.port}/docs")
    logger.info("=" * 80)
    
    yield
    
    # ==================== SHUTDOWN ====================
    logger.info("=" * 80)
    logger.info("🛑 ОСТАНОВКА ПРИЛОЖЕНИЯ")
    logger.info("=" * 80)
    logger.info("Остановка планировщика задач...")
    scheduler.shutdown()
    log_success(logger, "Приложение корректно остановлено")
    logger.info("=" * 80)


# Создание приложения
app = FastAPI(
    title="AI Ассистент Опора России",
    description="Умный ассистент для поддержки МСП",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования всех запросов
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware для логирования всех HTTP запросов"""
    request_id = id(request)
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info("=" * 80)
    logger.info(f"📥 HTTP REQUEST [{request_id}]")
    logger.info(f"   Method: {request.method}")
    logger.info(f"   URL: {request.url.path}")
    if request.query_params:
        logger.info(f"   Query: {dict(request.query_params)}")
    logger.info(f"   Client: {request.client.host if request.client else 'Unknown'}")
    logger.info("=" * 80)
    
    # Обрабатываем запрос
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Логируем ответ
        status_emoji = "✅" if response.status_code < 400 else "❌"
        logger.info("=" * 80)
        logger.info(f"{status_emoji} HTTP RESPONSE [{request_id}]")
        logger.info(f"   Status: {response.status_code}")
        logger.info(f"   Time: {process_time:.3f}s")
        logger.info("=" * 80)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        log_error(logger, f"Ошибка при обработке запроса [{request_id}]", 
                 error=e, url=str(request.url), time=f"{process_time:.3f}s")
        raise

# Подключение роутеров
app.include_router(chat.router)
app.include_router(applications.router)
app.include_router(reports.router)
app.include_router(documents.router)
app.include_router(feedback.router)
app.include_router(analysis.router)

# Статические файлы (для чат-виджета)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """
    Корневой эндпоинт
    """
    logger.debug("Обработка запроса к корневому эндпоинту")
    response = {
        "message": "AI Ассистент Опора России",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
    logger.debug(f"Ответ корневого эндпоинта: {response}")
    return response


@app.get("/health")
async def health_check():
    """
    Проверка здоровья приложения
    """
    logger.debug("Проверка здоровья приложения (health check)")
    is_healthy = scheduler.running
    
    response = {
        "status": "healthy" if is_healthy else "unhealthy",
        "scheduler": is_healthy
    }
    
    if is_healthy:
        logger.debug("✅ Health check: приложение здорово")
    else:
        log_warning(logger, "⚠️ Health check: планировщик не работает!")
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

