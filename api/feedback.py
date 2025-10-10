"""
API роутер для обратной связи
"""
from fastapi import APIRouter, HTTPException
from models.schemas import FeedbackData
from integrations import google_sheets_service, openai_service

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("/submit")
async def submit_feedback(feedback: FeedbackData):
    """
    Отправить обратную связь
    
    Args:
        feedback: Данные обратной связи
    
    Returns:
        Статус операции
    """
    try:
        success = google_sheets_service.save_feedback(feedback.dict())
        
        if success:
            return {
                "status": "success",
                "message": "Спасибо за вашу обратную связь!"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при сохранении обратной связи"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_feedback(category: str = None):
    """
    Получить обратную связь
    
    Args:
        category: Фильтр по категории (опционально)
    
    Returns:
        Список обратной связи
    """
    try:
        feedback_list = google_sheets_service.get_feedback(category)
        return {"feedback": feedback_list, "count": len(feedback_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis")
async def analyze_feedback():
    """
    Получить анализ обратной связи
    
    Returns:
        Аналитический отчет
    """
    try:
        feedback_list = google_sheets_service.get_feedback()
        
        if not feedback_list:
            return {"analysis": "Нет данных для анализа"}
        
        messages = [fb.get("Сообщение", "") for fb in feedback_list]
        analysis = openai_service.analyze_feedback(messages)
        
        return {
            "analysis": analysis,
            "total_feedback": len(feedback_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

