"""
API роутер для работы с жалобами
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.schemas import ComplaintData
from integrations import google_sheets_service
from logger_config import get_logger, log_success, log_error

router = APIRouter(prefix="/api/complaints", tags=["complaints"])
logger = get_logger(__name__)


@router.post("/submit")
async def submit_complaint(complaint: ComplaintData):
    """
    Подать жалобу
    
    Args:
        complaint: Данные жалобы
    
    Returns:
        Результат сохранения
    """
    try:
        complaint_dict = complaint.dict()
        success = google_sheets_service.save_complaint(complaint_dict)
        
        if success:
            log_success(logger, "Жалоба успешно подана", 
                       complaint_id=complaint.complaint_id, user_id=complaint.user_id)
            return {
                "status": "success",
                "message": "Жалоба успешно подана",
                "complaint_id": complaint.complaint_id
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при сохранении жалобы"
            )
    except Exception as e:
        log_error(logger, "Ошибка при подаче жалобы", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_complaints(status: Optional[str] = None):
    """
    Получить список жалоб
    
    Args:
        status: Фильтр по статусу (Новая, В обработке, Решена, Отклонена)
    
    Returns:
        Список жалоб
    """
    try:
        complaints = google_sheets_service.get_complaints(status)
        return {
            "status": "success",
            "data": complaints,
            "count": len(complaints)
        }
    except Exception as e:
        log_error(logger, "Ошибка получения списка жалоб", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_complaints_statistics():
    """
    Получить статистику по жалобам
    
    Returns:
        Статистика жалоб
    """
    try:
        all_complaints = google_sheets_service.get_complaints()
        
        stats = {
            "total": len(all_complaints),
            "by_status": {},
            "by_category": {},
            "by_priority": {}
        }
        
        for complaint in all_complaints:
            # Статистика по статусам
            status = complaint.get("Статус", "Неизвестно")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Статистика по категориям
            category = complaint.get("Категория", "Неизвестно")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Статистика по приоритетам
            priority = complaint.get("Приоритет", "Неизвестно")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        log_error(logger, "Ошибка получения статистики жалоб", error=e)
        raise HTTPException(status_code=500, detail=str(e))
