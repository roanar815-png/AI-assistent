"""
API роутер для анализа и прогнозирования МСП
"""
from fastapi import APIRouter, HTTPException
from integrations import openai_service

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/sme-trends")
async def get_sme_trends(query: str = None):
    """
    Получить анализ и прогноз трендов МСП
    
    Args:
        query: Конкретный запрос (опционально)
    
    Returns:
        Анализ и прогноз
    """
    try:
        analysis = openai_service.analyze_sme_trends(query)
        return {
            "analysis": analysis,
            "query": query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

