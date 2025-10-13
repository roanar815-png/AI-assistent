"""
API роутер для работы с мероприятиями
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.schemas import EventData
from integrations import google_sheets_service
from logger_config import get_logger, log_success, log_error

router = APIRouter(prefix="/api/events", tags=["events"])
logger = get_logger(__name__)


@router.post("/create")
async def create_event(event: EventData):
    """
    Создать мероприятие
    
    Args:
        event: Данные о мероприятии
    
    Returns:
        Результат создания
    """
    try:
        event_dict = event.dict()
        success = google_sheets_service.save_event(event_dict)
        
        if success:
            log_success(logger, "Мероприятие успешно создано", 
                       event_id=event.event_id, title=event.title)
            return {
                "status": "success",
                "message": "Мероприятие успешно создано",
                "event_id": event.event_id
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при создании мероприятия"
            )
    except Exception as e:
        log_error(logger, "Ошибка при создании мероприятия", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_events(status: Optional[str] = None):
    """
    Получить список мероприятий
    
    Args:
        status: Фильтр по статусу (Запланировано, В процессе, Завершено, Отменено)
    
    Returns:
        Список мероприятий
    """
    try:
        events = google_sheets_service.get_events(status)
        return {
            "status": "success",
            "data": events,
            "count": len(events)
        }
    except Exception as e:
        log_error(logger, "Ошибка получения списка мероприятий", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_events_statistics():
    """
    Получить статистику по мероприятиям
    
    Returns:
        Статистика мероприятий
    """
    try:
        all_events = google_sheets_service.get_events()
        
        stats = {
            "total": len(all_events),
            "by_status": {},
            "by_organizer": {}
        }
        
        for event in all_events:
            # Статистика по статусам
            status = event.get("Статус", "Неизвестно")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Статистика по организаторам
            organizer = event.get("Организатор", "Неизвестно")
            stats["by_organizer"][organizer] = stats["by_organizer"].get(organizer, 0) + 1
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        log_error(logger, "Ошибка получения статистики мероприятий", error=e)
        raise HTTPException(status_code=500, detail=str(e))
