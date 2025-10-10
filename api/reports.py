"""
API роутер для формирования отчетов
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from models.schemas import ReportRequest
from services import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate")
async def generate_report(request: ReportRequest):
    """
    Сгенерировать отчет
    
    Args:
        request: Параметры отчета
    
    Returns:
        Путь к файлу отчета
    """
    try:
        if request.report_type == "users":
            filepath = report_service.generate_users_report(request.format)
        elif request.report_type == "applications":
            filepath = report_service.generate_applications_report(request.format)
        elif request.report_type == "feedback":
            filepath = report_service.generate_feedback_report(request.format)
        elif request.report_type == "stats":
            stats = report_service.generate_statistics_report()
            return {"type": "stats", "data": stats}
        else:
            raise HTTPException(
                status_code=400,
                detail="Неизвестный тип отчета"
            )
        
        if filepath:
            return {
                "status": "success",
                "filepath": filepath,
                "download_url": f"/api/reports/download?file={filepath}"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при создании отчета"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download")
async def download_report(file: str):
    """
    Скачать отчет
    
    Args:
        file: Путь к файлу
    
    Returns:
        Файл для скачивания
    """
    try:
        return FileResponse(
            path=file,
            filename=file.split('/')[-1],
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="Файл не найден")


@router.get("/statistics")
async def get_statistics():
    """
    Получить статистику
    
    Returns:
        Статистика системы
    """
    try:
        stats = report_service.generate_statistics_report()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

