"""
API роутер для health-проверок
"""
from fastapi import APIRouter
from integrations import google_sheets_service
from logger_config import get_logger, log_error


router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/google-sheets")
async def google_sheets_health():
    """
    Проверка доступности Google Sheets
    """
    logger = get_logger(__name__)
    status = google_sheets_service.get_status()
    status["connected"] = bool(status.get("has_client") and status.get("has_spreadsheet"))
    if not status["connected"]:
        # Пытаемся инициировать создание (на случай ленивой инициализации уже выполненной в конструкторе)
        try:
            # Попробуем получить лист Users как минимальную операцию
            sheet = google_sheets_service._get_or_create_sheet("Users")  # noqa: SLF001
            status["can_get_sheet"] = bool(sheet)
        except Exception as e:
            status["can_get_sheet"] = False
            log_error(logger, "Проверка Google Sheets завершилась ошибкой", error=e)
    return status

@router.post("/google-sheets/reconnect")
async def google_sheets_reconnect():
    """
    Принудительное переподключение к Google Sheets
    """
    logger = get_logger(__name__)
    try:
        status = google_sheets_service.reconnect()
        status["connected"] = bool(status.get("has_client") and status.get("has_spreadsheet"))
        return status
    except Exception as e:
        log_error(logger, "Ошибка переподключения к Google Sheets", error=e)
        return {"connected": False, "error": str(e)}


