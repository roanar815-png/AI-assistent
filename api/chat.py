"""
API роутер для чата с ассистентом
"""
from fastapi import APIRouter, HTTPException
from models.schemas import (
    ChatMessage, ChatResponse, 
    InteractiveAutofillRequest, AnalyzeDocumentRequest, 
    AskQuestionsRequest, AnswerQuestionRequest, FinalizeAutofillRequest
)
from services import assistant_service
from logger_config import get_logger, log_success, log_error, log_warning

# Инициализация логгера
logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(message: ChatMessage):
    """
    Отправить сообщение ассистенту
    
    Args:
        message: Объект сообщения с user_id и текстом
    
    Returns:
        Ответ ассистента
    """
    logger.info("💬 POST /api/chat/message")
    logger.info(f"   User ID: {message.user_id}")
    logger.info(f"   Message: {message.message[:100]}{'...' if len(message.message) > 100 else ''}")
    
    try:
        logger.debug("Вызов assistant_service.process_message...")
        response = assistant_service.process_message(
            user_id=message.user_id,
            message=message.message
        )
        
        log_success(logger, "Сообщение обработано", 
                   user_id=message.user_id,
                   response_length=len(response.response) if response.response else 0)
        
        logger.debug(f"   Response preview: {response.response[:100] if response.response else 'EMPTY'}...")
        return response
        
    except Exception as e:
        log_error(logger, f"Ошибка обработки сообщения", 
                 error=e, user_id=message.user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_history(user_id: str):
    """
    Получить историю диалога пользователя
    
    Args:
        user_id: ID пользователя
    
    Returns:
        История диалога
    """
    logger.info(f"📖 GET /api/chat/history/{user_id}")
    try:
        history = assistant_service.get_conversation_history(user_id)
        log_success(logger, "История получена", user_id=user_id, 
                   messages_count=len(history) if history else 0)
        return {"history": history}
    except Exception as e:
        log_error(logger, "Ошибка получения истории", error=e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{user_id}")
async def clear_history(user_id: str):
    """
    Очистить историю диалога
    
    Args:
        user_id: ID пользователя
    
    Returns:
        Статус операции
    """
    logger.info(f"🗑️ DELETE /api/chat/history/{user_id}")
    try:
        assistant_service.clear_conversation(user_id)
        log_success(logger, "История очищена", user_id=user_id)
        return {"status": "success", "message": "История очищена"}
    except Exception as e:
        log_error(logger, "Ошибка очистки истории", error=e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-document")
async def create_document_from_chat(
    user_id: str,
    template_id: str,
    user_data: dict,
    conversation_data: dict = None,
    send_email: bool = False
):
    """
    Создать документ из шаблона на основе данных чата
    
    Args:
        user_id: ID пользователя
        template_id: ID шаблона
        user_data: Данные пользователя
        conversation_data: Данные из разговора
        send_email: Bool - отправить документ на email
    
    Returns:
        Результат создания документа
    """
    logger.info(f"📝 POST /api/chat/create-document")
    logger.info(f"   User ID: {user_id}")
    logger.info(f"   Template ID: {template_id}")
    logger.info(f"   Send Email: {send_email}")
    logger.debug(f"   User Data keys: {list(user_data.keys())}")
    
    try:
        result = assistant_service.create_document_from_template(
            user_id, template_id, user_data, conversation_data, send_email
        )
        log_success(logger, "Документ создан", 
                   user_id=user_id, template_id=template_id, 
                   email_sent=send_email)
        return result
    except Exception as e:
        log_error(logger, "Ошибка создания документа", error=e, 
                 user_id=user_id, template_id=template_id)
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