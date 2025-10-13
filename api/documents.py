"""
API роутер для работы с документами
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from models.schemas import DocumentTemplate
from integrations import google_sheets_service
from logger_config import get_logger, log_error
from services import document_service
from typing import Optional

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/generate")
async def generate_document(template: DocumentTemplate):
    """
    Сгенерировать документ из шаблона
    
    Args:
        template: Данные для заполнения шаблона
    
    Returns:
        Путь к созданному документу
    """
    try:
        if template.template_type == "complaint":
            filepath = document_service.fill_complaint_template(template.user_data)
        elif template.template_type == "protocol":
            filepath = document_service.fill_protocol_template(template.user_data)
        elif template.template_type == "contract":
            filepath = document_service.fill_contract_template(template.user_data)
        else:
            raise HTTPException(
                status_code=400,
                detail="Неизвестный тип шаблона"
            )
        
        if filepath:
            result = {
                "status": "success",
                "filepath": filepath,
                "download_url": f"/api/documents/download?file={filepath}"
            }
            # Сохраняем информацию о документе в Google Sheets
            try:
                user_data = template.user_data or {}
                google_sheets_service.save_document({
                    "user_id": user_data.get("user_id", ""),
                    "full_name": user_data.get("full_name", ""),
                    "email": user_data.get("email", ""),
                    "document_type": template.template_type,
                    "template_name": template.template_type,
                    "filepath": filepath,
                    "download_url": result["download_url"],
                    "completeness_score": user_data.get("completeness_score", ""),
                    "confidence_score": user_data.get("confidence_score", ""),
                    "data_quality": user_data.get("data_quality", ""),
                })
            except Exception as e:
                # Логируем, но не падаем для пользователя
                logger = get_logger(__name__)
                log_error(logger, "Ошибка записи документа в Google Sheets (generate)", error=e)
            return result
        else:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при создании документа"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download")
async def download_document(file: str):
    """
    Скачать документ
    
    Args:
        file: Путь к файлу
    
    Returns:
        Файл для скачивания
    """
    try:
        return FileResponse(
            path=file,
            filename=file.split('/')[-1],
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="Файл не найден")


@router.post("/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    template_name: str = Form(...),
    description: str = Form("")
):
    """
    Загрузить шаблон документа
    
    Args:
        file: Файл шаблона (.docx или .txt)
        template_name: Название шаблона
        description: Описание шаблона
    
    Returns:
        Результат загрузки
    """
    try:
        # Проверяем тип файла
        if not file.filename.endswith(('.docx', '.txt')):
            raise HTTPException(
                status_code=400,
                detail="Поддерживаются только файлы .docx и .txt"
            )
        
        # Сохраняем временный файл
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Загружаем шаблон
        result = document_service.upload_template(
            temp_file_path, 
            template_name, 
            description
        )
        
        # Удаляем временный файл
        import os
        os.unlink(temp_file_path)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_templates():
    """
    Получить список всех шаблонов (новый endpoint)
    
    Returns:
        Список шаблонов
    """
    try:
        templates = document_service.get_templates_list()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/list")
async def get_templates_list():
    """
    Получить список всех шаблонов (старый endpoint для обратной совместимости)
    
    Returns:
        Список шаблонов
    """
    try:
        templates = document_service.get_templates_list()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/generate")
async def generate_from_template(
    template_id: str,
    user_data: dict,
    conversation_data: Optional[dict] = None
):
    """
    Сгенерировать документ из загруженного шаблона
    
    Args:
        template_id: ID шаблона
        user_data: Данные пользователя
        conversation_data: Данные из разговора
    
    Returns:
        Путь к созданному документу
    """
    try:
        filepath = document_service.fill_uploaded_template(
            template_id, 
            user_data, 
            conversation_data
        )
        
        result = {
            "status": "success",
            "filepath": filepath,
            "download_url": f"/api/documents/download?file={filepath}"
        }
        # Сохраняем информацию о документе в Google Sheets
        try:
            user_info = user_data or {}
            google_sheets_service.save_document({
                "user_id": user_info.get("user_id", ""),
                "full_name": user_info.get("full_name", ""),
                "email": user_info.get("email", ""),
                "document_type": "uploaded_template",
                "template_name": template_id,
                "filepath": filepath,
                "download_url": result["download_url"],
                "completeness_score": user_info.get("completeness_score", ""),
                "confidence_score": user_info.get("confidence_score", ""),
                "data_quality": user_info.get("data_quality", ""),
            })
        except Exception as e:
            logger = get_logger(__name__)
            log_error(logger, "Ошибка записи документа в Google Sheets (generate_from_template)", error=e)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """
    Удалить шаблон
    
    Args:
        template_id: ID шаблона
    
    Returns:
        Результат операции
    """
    try:
        result = document_service.delete_template(template_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

