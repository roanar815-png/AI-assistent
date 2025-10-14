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


@router.get("/market-forecast")
async def get_market_forecast(query: str = None):
    """
    Получить прогноз рынка для МСП
    
    Args:
        query: Конкретный запрос (опционально)
    
    Returns:
        Прогноз рынка
    """
    try:
        forecast = openai_service.market_forecast(query)
        return {
            "forecast": forecast,
            "query": query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business-insights")
async def get_business_insights(query: str = None):
    """
    Получить бизнес-инсайты для МСП
    
    Args:
        query: Конкретный запрос (опционально)
    
    Returns:
        Бизнес-инсайты
    """
    try:
        insights = openai_service.business_insights(query)
        return {
            "insights": insights,
            "query": query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
