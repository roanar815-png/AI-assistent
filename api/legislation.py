"""
API роутер для работы с законодательством
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.schemas import LegislationData
from integrations import google_sheets_service
from logger_config import get_logger, log_success, log_error

router = APIRouter(prefix="/api/legislation", tags=["legislation"])
logger = get_logger(__name__)


@router.post("/add")
async def add_legislation(legislation: LegislationData):
    """
    Добавить информацию о законодательстве
    
    Args:
        legislation: Данные о законодательстве
    
    Returns:
        Результат сохранения
    """
    try:
        legislation_dict = legislation.dict()
        success = google_sheets_service.save_legislation(legislation_dict)
        
        if success:
            log_success(logger, "Законодательство успешно добавлено", 
                       title=legislation.title)
            return {
                "status": "success",
                "message": "Информация о законодательстве успешно добавлена",
                "title": legislation.title
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при сохранении информации о законодательстве"
            )
    except Exception as e:
        log_error(logger, "Ошибка при добавлении законодательства", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_legislation(category: Optional[str] = None):
    """
    Получить список законодательства
    
    Args:
        category: Фильтр по категории
    
    Returns:
        Список законодательства
    """
    try:
        legislation = google_sheets_service.get_legislation(category)
        return {
            "status": "success",
            "data": legislation,
            "count": len(legislation)
        }
    except Exception as e:
        log_error(logger, "Ошибка получения списка законодательства", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_legislation_statistics():
    """
    Получить статистику по законодательству
    
    Returns:
        Статистика законодательства
    """
    try:
        all_legislation = google_sheets_service.get_legislation()
        
        stats = {
            "total": len(all_legislation),
            "by_category": {},
            "by_importance": {}
        }
        
        for item in all_legislation:
            # Статистика по категориям
            category = item.get("Категория", "Неизвестно")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Статистика по важности
            importance = item.get("Важность", "Неизвестно")
            stats["by_importance"][importance] = stats["by_importance"].get(importance, 0) + 1
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        log_error(logger, "Ошибка получения статистики законодательства", error=e)
        raise HTTPException(status_code=500, detail=str(e))
