"""
Сервис для сбора и анализа данных чата
"""
import uuid
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from logger_config import get_logger, log_success, log_error

logger = get_logger(__name__)


class ChatAnalyticsService:
    """Сервис для сбора аналитики чата"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.session_messages: Dict[str, List[Dict]] = defaultdict(list)
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.topics_discussed: Dict[str, List[str]] = defaultdict(list)
        self.documents_created: Dict[str, int] = defaultdict(int)
    
    def start_session(self, user_id: str) -> str:
        """
        Начать новую сессию чата
        
        Args:
            user_id: ID пользователя
        
        Returns:
            ID сессии
        """
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "start_time": datetime.now(),
            "last_activity": datetime.now()
        }
        self.session_messages[session_id] = []
        self.response_times[session_id] = []
        self.topics_discussed[session_id] = []
        self.documents_created[session_id] = 0
        
        logger.debug(f"Начата новая сессия чата: {session_id} для пользователя {user_id}")
        return session_id
    
    def add_message(self, session_id: str, message: str, response: str, 
                   response_time: float, topics: List[str] = None):
        """
        Добавить сообщение в сессию
        
        Args:
            session_id: ID сессии
            message: Сообщение пользователя
            response: Ответ ассистента
            response_time: Время ответа в секундах
            topics: Обсуждаемые темы
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Попытка добавить сообщение в несуществующую сессию: {session_id}")
            return
        
        # Обновляем время последней активности
        self.active_sessions[session_id]["last_activity"] = datetime.now()
        
        # Добавляем сообщение
        self.session_messages[session_id].append({
            "message": message,
            "response": response,
            "timestamp": datetime.now(),
            "response_time": response_time
        })
        
        # Добавляем время ответа
        self.response_times[session_id].append(response_time)
        
        # Добавляем темы
        if topics:
            self.topics_discussed[session_id].extend(topics)
            # Убираем дубликаты
            self.topics_discussed[session_id] = list(set(self.topics_discussed[session_id]))
        
        logger.debug(f"Добавлено сообщение в сессию {session_id}, время ответа: {response_time:.2f}с")
    
    def mark_document_created(self, session_id: str):
        """
        Отметить создание документа в сессии
        
        Args:
            session_id: ID сессии
        """
        if session_id in self.documents_created:
            self.documents_created[session_id] += 1
            logger.debug(f"Отмечено создание документа в сессии {session_id}")
    
    def end_session(self, session_id: str, satisfaction_score: Optional[float] = None) -> Dict:
        """
        Завершить сессию и вернуть аналитику
        
        Args:
            session_id: ID сессии
            satisfaction_score: Оценка удовлетворенности (1-5)
        
        Returns:
            Данные аналитики сессии
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Попытка завершить несуществующую сессию: {session_id}")
            return {}
        
        session_data = self.active_sessions[session_id]
        start_time = session_data["start_time"]
        end_time = datetime.now()
        session_duration = int((end_time - start_time).total_seconds())
        
        # Вычисляем среднее время ответа
        response_times = self.response_times[session_id]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Подготавливаем данные аналитики
        analytics_data = {
            "session_id": session_id,
            "user_id": session_data["user_id"],
            "message_count": len(self.session_messages[session_id]),
            "response_time_avg": round(avg_response_time, 2),
            "satisfaction_score": satisfaction_score,
            "topics_discussed": self.topics_discussed[session_id],
            "documents_created": self.documents_created[session_id],
            "session_duration": session_duration,
            "created_at": end_time
        }
        
        # Очищаем данные сессии
        del self.active_sessions[session_id]
        del self.session_messages[session_id]
        del self.response_times[session_id]
        del self.topics_discussed[session_id]
        del self.documents_created[session_id]
        
        logger.info(f"Сессия {session_id} завершена. Длительность: {session_duration}с, "
                   f"сообщений: {analytics_data['message_count']}, "
                   f"документов: {analytics_data['documents_created']}")
        
        return analytics_data
    
    def get_session_stats(self, session_id: str) -> Dict:
        """
        Получить статистику текущей сессии
        
        Args:
            session_id: ID сессии
        
        Returns:
            Статистика сессии
        """
        if session_id not in self.active_sessions:
            return {}
        
        session_data = self.active_sessions[session_id]
        start_time = session_data["start_time"]
        current_time = datetime.now()
        duration = int((current_time - start_time).total_seconds())
        
        response_times = self.response_times[session_id]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        return {
            "session_id": session_id,
            "user_id": session_data["user_id"],
            "duration": duration,
            "message_count": len(self.session_messages[session_id]),
            "avg_response_time": round(avg_response_time, 2),
            "topics_count": len(self.topics_discussed[session_id]),
            "documents_created": self.documents_created[session_id]
        }
    
    def cleanup_inactive_sessions(self, max_idle_minutes: int = 30):
        """
        Очистить неактивные сессии
        
        Args:
            max_idle_minutes: Максимальное время неактивности в минутах
        """
        current_time = datetime.now()
        inactive_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            last_activity = session_data["last_activity"]
            idle_time = current_time - last_activity
            
            if idle_time > timedelta(minutes=max_idle_minutes):
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            logger.info(f"Очистка неактивной сессии: {session_id}")
            self.end_session(session_id)
        
        if inactive_sessions:
            logger.info(f"Очищено {len(inactive_sessions)} неактивных сессий")
    
    def extract_topics_from_message(self, message: str) -> List[str]:
        """
        Извлечь темы из сообщения пользователя
        
        Args:
            message: Сообщение пользователя
        
        Returns:
            Список тем
        """
        topics = []
        message_lower = message.lower()
        
        # Ключевые слова для определения тем
        topic_keywords = {
            "документы": ["документ", "шаблон", "заполнить", "создать", "оформить"],
            "законодательство": ["закон", "норматив", "требование", "регулирование"],
            "налоги": ["налог", "сбор", "платеж", "декларация", "отчетность"],
            "регистрация": ["регистрация", "регистрировать", "ооо", "ип", "юрлицо"],
            "лицензии": ["лицензия", "разрешение", "сертификат", "аккредитация"],
            "жалобы": ["жалоба", "претензия", "нарушение", "недовольство"],
            "мероприятия": ["мероприятие", "событие", "встреча", "семинар", "конференция"],
            "консультации": ["консультация", "помощь", "вопрос", "совет", "рекомендация"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics


# Singleton instance
analytics_service = ChatAnalyticsService()
