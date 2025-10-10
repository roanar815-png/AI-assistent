"""
API роутер для заявок на вступление
"""
from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import ApplicationRequest
from integrations import google_sheets_service

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("/submit")
async def submit_application(application: ApplicationRequest):
    """
    Подать заявку на вступление в Опору России
    
    Args:
        application: Данные заявки
    
    Returns:
        Статус операции
    """
    try:
        success = google_sheets_service.save_application(application.dict())
        
        if success:
            return {
                "status": "success",
                "message": "Заявка успешно подана",
                "application_id": application.user_id
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при сохранении заявки"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_applications(status: str = None):
    """
    Получить список заявок
    
    Args:
        status: Фильтр по статусу (опционально)
    
    Returns:
        Список заявок
    """
    try:
        applications = google_sheets_service.get_applications(status)
        return {"applications": applications, "count": len(applications)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_user_applications(user_id: str):
    """
    Получить заявки конкретного пользователя
    
    Args:
        user_id: ID пользователя
    
    Returns:
        Заявки пользователя
    """
    try:
        all_applications = google_sheets_service.get_applications()
        user_applications = [
            app for app in all_applications 
            if app.get("ID") == user_id
        ]
        return {"applications": user_applications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

