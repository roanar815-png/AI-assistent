"""
Pydantic модели для валидации данных
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserData(BaseModel):
    """Данные пользователя"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class ChatMessage(BaseModel):
    """Сообщение в чате"""
    user_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatResponse(BaseModel):
    """Ответ ассистента"""
    response: str
    action: Optional[str] = None
    data: Optional[dict] = None
    document_suggestion: Optional[dict] = None


class FeedbackData(BaseModel):
    """Обратная связь от пользователя"""
    user_id: str
    message: str
    category: str  # question, complaint, suggestion
    timestamp: datetime = Field(default_factory=datetime.now)


class EventData(BaseModel):
    """Данные о мероприятии"""
    title: str
    date: str
    description: str
    participants: List[str] = []


class ReportRequest(BaseModel):
    """Запрос на формирование отчета"""
    report_type: str  # users, faq, complaints, stats
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    format: str = "csv"  # csv, pdf


class DocumentTemplate(BaseModel):
    """Данные для заполнения шаблона документа"""
    template_type: str  # complaint, protocol, contract
    user_data: dict
    additional_data: Optional[dict] = None


class InteractiveAutofillRequest(BaseModel):
    """Запрос на начало интерактивного автозаполнения"""
    user_id: str
    message: Optional[str] = None


class AnalyzeDocumentRequest(BaseModel):
    """Запрос на анализ документа"""
    user_id: str
    document_name: str


class AskQuestionsRequest(BaseModel):
    """Запрос на получение вопросов"""
    user_id: str
    document_name: str
    current_data: Optional[dict] = None


class AnswerQuestionRequest(BaseModel):
    """Запрос на ответ на вопрос"""
    user_id: str
    question_id: str
    answer: str


class FinalizeAutofillRequest(BaseModel):
    """Запрос на завершение автозаполнения"""
    user_id: str
    document_name: str


class CreateDocumentRequest(BaseModel):
    """Запрос на создание документа"""
    user_id: str
    template_id: str
    user_data: dict
    conversation_data: Optional[dict] = None
    send_email: bool = False


class ComplaintData(BaseModel):
    """Данные жалобы"""
    complaint_id: str
    user_id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    organization: Optional[str] = None
    complaint_text: str
    category: str = "Общая"
    priority: str = "Средний"
    status: str = "Новая"
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None


class LegislationData(BaseModel):
    """Данные о законодательстве"""
    title: str
    url: str
    publication_date: str
    description: Optional[str] = None
    category: Optional[str] = None
    importance: str = "Средняя"
    added_at: datetime = Field(default_factory=datetime.now)


class EventData(BaseModel):
    """Данные о мероприятии"""
    event_id: str
    title: str
    date: str
    time: Optional[str] = None
    description: str
    location: Optional[str] = None
    participants: List[str] = []
    organizer: Optional[str] = None
    status: str = "Запланировано"
    created_at: datetime = Field(default_factory=datetime.now)


class ChatAnalyticsData(BaseModel):
    """Данные аналитики чата"""
    session_id: str
    user_id: str
    message_count: int
    response_time_avg: float
    satisfaction_score: Optional[float] = None
    topics_discussed: List[str] = []
    documents_created: int = 0
    session_duration: int  # в секундах
    created_at: datetime = Field(default_factory=datetime.now)

