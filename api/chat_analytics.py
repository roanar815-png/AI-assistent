"""
API роутер для работы с аналитикой чата
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.schemas import ChatAnalyticsData
from integrations import google_sheets_service
from logger_config import get_logger, log_success, log_error

router = APIRouter(prefix="/api/chat-analytics", tags=["chat-analytics"])
logger = get_logger(__name__)


@router.post("/save")
async def save_chat_analytics(analytics: ChatAnalyticsData):
    """
    Сохранить данные аналитики чата
    
    Args:
        analytics: Данные аналитики чата
    
    Returns:
        Результат сохранения
    """
    try:
        analytics_dict = analytics.dict()
        success = google_sheets_service.save_chat_analytics(analytics_dict)
        
        if success:
            log_success(logger, "Аналитика чата успешно сохранена", 
                       session_id=analytics.session_id, user_id=analytics.user_id)
            return {
                "status": "success",
                "message": "Аналитика чата успешно сохранена",
                "session_id": analytics.session_id
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при сохранении аналитики чата"
            )
    except Exception as e:
        log_error(logger, "Ошибка при сохранении аналитики чата", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_chat_analytics(user_id: Optional[str] = None):
    """
    Получить данные аналитики чата
    
    Args:
        user_id: Фильтр по пользователю
    
    Returns:
        Список данных аналитики
    """
    try:
        analytics = google_sheets_service.get_chat_analytics(user_id)
        return {
            "status": "success",
            "data": analytics,
            "count": len(analytics)
        }
    except Exception as e:
        log_error(logger, "Ошибка получения аналитики чата", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/end-session")
async def end_chat_session(session_id: str, satisfaction_score: Optional[float] = None):
    """
    Завершить сессию чата и сохранить аналитику
    
    Args:
        session_id: ID сессии
        satisfaction_score: Оценка удовлетворенности (1-5)
    
    Returns:
        Результат завершения сессии
    """
    try:
        from services.analytics_service import analytics_service
        from integrations import google_sheets_service
        
        # Завершаем сессию и получаем аналитику
        analytics_data = analytics_service.end_session(session_id, satisfaction_score)
        
        if not analytics_data:
            raise HTTPException(
                status_code=404,
                detail="Сессия не найдена или уже завершена"
            )
        
        # Сохраняем аналитику в Google Sheets
        success = google_sheets_service.save_chat_analytics(analytics_data)
        
        if success:
            return {
                "status": "success",
                "message": "Сессия завершена и аналитика сохранена",
                "analytics": analytics_data
            }
        else:
            return {
                "status": "warning",
                "message": "Сессия завершена, но не удалось сохранить аналитику",
                "analytics": analytics_data
            }
    except Exception as e:
        log_error(logger, "Ошибка при завершении сессии", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_stats(session_id: str):
    """
    Получить статистику текущей сессии
    
    Args:
        session_id: ID сессии
    
    Returns:
        Статистика сессии
    """
    try:
        from services.analytics_service import analytics_service
        
        stats = analytics_service.get_session_stats(session_id)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail="Сессия не найдена"
            )
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        log_error(logger, "Ошибка получения статистики сессии", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_chat_analytics_statistics():
    """
    Получить статистику по аналитике чата
    
    Returns:
        Статистика аналитики чата
    """
    try:
        all_analytics = google_sheets_service.get_chat_analytics()
        
        if not all_analytics:
            return {
                "status": "success",
                "data": {
                    "total_sessions": 0,
                    "total_messages": 0,
                    "avg_response_time": 0,
                    "avg_satisfaction": 0,
                    "total_documents_created": 0,
                    "avg_session_duration": 0
                }
            }
        
        stats = {
            "total_sessions": len(all_analytics),
            "total_messages": sum(int(a.get("Количество сообщений", 0)) for a in all_analytics),
            "total_documents_created": sum(int(a.get("Создано документов", 0)) for a in all_analytics),
            "avg_response_time": 0,
            "avg_satisfaction": 0,
            "avg_session_duration": 0
        }
        
        # Вычисляем средние значения
        response_times = [float(a.get("Среднее время ответа (сек)", 0)) for a in all_analytics if a.get("Среднее время ответа (сек)")]
        if response_times:
            stats["avg_response_time"] = sum(response_times) / len(response_times)
        
        satisfaction_scores = [float(a.get("Оценка удовлетворенности", 0)) for a in all_analytics if a.get("Оценка удовлетворенности")]
        if satisfaction_scores:
            stats["avg_satisfaction"] = sum(satisfaction_scores) / len(satisfaction_scores)
        
        session_durations = [int(a.get("Длительность сессии (сек)", 0)) for a in all_analytics if a.get("Длительность сессии (сек)")]
        if session_durations:
            stats["avg_session_duration"] = sum(session_durations) / len(session_durations)
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        log_error(logger, "Ошибка получения статистики аналитики чата", error=e)
        raise HTTPException(status_code=500, detail=str(e))
