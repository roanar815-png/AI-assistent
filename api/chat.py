"""
API роутер для чата с ассистентом
"""
from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import (
    ChatMessage, ChatResponse, 
    InteractiveAutofillRequest, AnalyzeDocumentRequest, 
    AskQuestionsRequest, AnswerQuestionRequest, FinalizeAutofillRequest,
    CreateDocumentRequest
)
from services import assistant_service
from integrations import openai_service, google_sheets_service
from logger_config import get_logger, log_success, log_error, log_warning

# Инициализация логгера
logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(message: ChatMessage):
    """
    Отправить сообщение ассистенту (асинхронная версия)
    
    Args:
        message: Объект сообщения с user_id и текстом
    
    Returns:
        Ответ ассистента
    """
    logger.info("💬 POST /api/chat/message (ASYNC)")
    logger.info(f"   User ID: {message.user_id}")
    logger.info(f"   Message: {message.message[:100]}{'...' if len(message.message) > 100 else ''}")
    
    try:
        logger.debug("Вызов assistant_service.process_message_async...")
        print(f"[API DEBUG] Обрабатываем сообщение: {message.message}")
        response = await assistant_service.process_message_async(
            user_id=message.user_id,
            message=message.message
        )
        print(f"[API DEBUG] Получен ответ с действием: {response.action}")
        
        log_success(logger, "Сообщение обработано асинхронно", 
                   user_id=message.user_id,
                   response_length=len(response.response) if response.response else 0)
        
        logger.debug(f"   Response preview: {response.response[:100] if response.response else 'EMPTY'}...")
        return response
        
    except Exception as e:
        log_error(logger, f"Ошибка асинхронной обработки сообщения", 
                 error=e, user_id=message.user_id)
        raise HTTPException(status_code=500, detail=str(e))


## История диалога отключена по требованию: удалены эндпоинты /history/{user_id}


@router.post("/create-document")
async def create_document_from_chat(request: CreateDocumentRequest):
    """
    Создать документ из шаблона на основе данных чата
    
    Args:
        request: Запрос с данными для создания документа
    
    Returns:
        Результат создания документа
    """
    logger.info(f"📝 POST /api/chat/create-document")
    logger.info(f"   User ID: {request.user_id}")
    logger.info(f"   Template ID: {request.template_id}")
    logger.info(f"   Send Email: {request.send_email}")
    logger.debug(f"   User Data keys: {list(request.user_data.keys())}")
    
    try:
        logger.info(f"[DEBUG] api/chat.py: Вызываем create_document_from_template для user_id={request.user_id}")
        result = assistant_service.create_document_from_template(
            request.user_id, request.template_id, request.user_data, 
            request.conversation_data, request.send_email
        )
        logger.info(f"[DEBUG] api/chat.py: create_document_from_template вернула результат: {result.get('status', 'unknown')}")
        
        # Сохраняем информацию о документе в Google Sheets
        if result and result.get("status") == "success":
            try:
                # Получаем название шаблона
                template_name = "Неизвестный шаблон"
                try:
                    templates = assistant_service.get_available_templates()
                    template_name = next((t['name'] for t in templates if t['template_id'] == request.template_id), "Неизвестный шаблон")
                except:
                    pass
                
                google_sheets_service.save_document({
                    "user_id": request.user_id,
                    "full_name": request.user_data.get("full_name", ""),
                    "email": request.user_data.get("email", ""),
                    "document_type": "документ",
                    "template_name": template_name,
                    "filepath": result.get("filepath", ""),
                    "download_url": result.get("download_url", ""),
                    "completeness_score": 100,  # Предполагаем полные данные для прямого создания
                    "confidence_score": 100,
                    "data_quality": "Высокое"
                })
                logger.info("✅ Документ сохранен в Google Sheets")
            except Exception as e:
                logger.error(f"❌ Ошибка сохранения документа в Google Sheets: {e}")
        
        log_success(logger, "Документ создан", 
                   user_id=request.user_id, template_id=request.template_id, 
                   email_sent=request.send_email)
        return result
    except Exception as e:
        log_error(logger, "Ошибка создания документа", error=e, 
                 user_id=request.user_id, template_id=request.template_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview-document")
async def preview_document(template_id: str, user_data: dict):
    """
    Генерирует предпросмотр документа перед созданием
    
    Args:
        template_id: ID шаблона
        user_data: Данные пользователя
    
    Returns:
        Предпросмотр документа с анализом полноты данных
    """
    try:
        result = assistant_service.preview_document(template_id, user_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interactive-autofill")
async def start_interactive_autofill(user_id: str, message: str = None):
    """
    Начать интерактивный процесс автозаполнения документа
    
    Args:
        user_id: ID пользователя
        message: Сообщение пользователя (опционально)
    
    Returns:
        Начало интерактивного процесса
    """
    try:
        result = assistant_service.start_interactive_autofill(user_id, message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interactive-autofill/analyze-document")
async def analyze_document_for_autofill(user_id: str, document_name: str):
    """
    Анализирует указанный документ и определяет нужные поля
    
    Args:
        user_id: ID пользователя
        document_name: Название документа для анализа
    
    Returns:
        Анализ документа и список нужных полей
    """
    try:
        result = assistant_service.analyze_document_for_autofill(user_id, document_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interactive-autofill/ask-questions")
async def ask_questions_for_autofill(user_id: str, document_name: str, current_data: dict = None):
    """
    Задает вопросы для заполнения недостающих данных
    
    Args:
        user_id: ID пользователя
        document_name: Название документа
        current_data: Текущие данные пользователя
    
    Returns:
        Список вопросов для заполнения
    """
    try:
        result = assistant_service.ask_questions_for_autofill(user_id, document_name, current_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interactive-autofill/answer-question")
async def answer_question_for_autofill(user_id: str, question_id: str, answer: str):
    """
    Обрабатывает ответ пользователя на вопрос
    
    Args:
        user_id: ID пользователя
        question_id: ID вопроса
        answer: Ответ пользователя
    
    Returns:
        Результат обработки ответа
    """
    try:
        result = assistant_service.answer_question_for_autofill(user_id, question_id, answer)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interactive-autofill/finalize")
async def finalize_autofill(user_id: str, document_name: str):
    """
    Завершает процесс автозаполнения и создает документ
    
    Args:
        user_id: ID пользователя
        document_name: Название документа
    
    Returns:
        Созданный документ
    """
    try:
        result = assistant_service.finalize_autofill(user_id, document_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_metrics():
    """
    Получить метрики производительности системы
    
    Returns:
        Метрики производительности
    """
    logger.info("СТАТИСТИКА: GET /api/chat/performance")
    try:
        metrics = assistant_service.get_performance_metrics()
        log_success(logger, "Метрики производительности получены", 
                   total_requests=metrics.get("total_requests", 0),
                   cache_hit_rate=metrics.get("cache_hit_rate", "0%"))
        return metrics
    except Exception as e:
        log_error(logger, "Ошибка получения метрик производительности", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def process_batch_messages(messages: List[ChatMessage]):
    """
    Параллельная обработка нескольких сообщений
    
    Args:
        messages: Список сообщений для обработки
    
    Returns:
        Список ответов
    """
    logger.info(f"🚀 POST /api/chat/batch - {len(messages)} сообщений")
    try:
        # Подготавливаем запросы для параллельной обработки
        requests = []
        for msg in messages:
            history = assistant_service.get_conversation_history(msg.user_id)
            requests.append({
                "message": msg.message,
                "history": history
            })
        
        # Параллельная обработка
        responses = await openai_service.process_multiple_requests(requests)
        
        # Формируем ответы
        results = []
        for i, response_text in enumerate(responses):
            results.append(ChatResponse(
                response=response_text,
                action="chat",
                document_suggestion=None
            ))
        
        log_success(logger, "Пакетная обработка завершена", 
                   messages_count=len(messages),
                   success_count=len([r for r in results if r.response]))
        
        return {"results": results}
        
    except Exception as e:
        log_error(logger, "Ошибка пакетной обработки", error=e)
        raise HTTPException(status_code=500, detail=str(e))