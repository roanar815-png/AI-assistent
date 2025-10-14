"""
Интеграция с Google Sheets для хранения данных
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
from datetime import datetime
import os
from config import settings
from logger_config import get_logger, log_success, log_error, log_warning

# Инициализация логгера
logger = get_logger(__name__)


class GoogleSheetsService:
    """Сервис для работы с Google Sheets"""
    
    def __init__(self):
        """Инициализация подключения к Google Sheets"""
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.creds = None
        self.client = None
        self.spreadsheet = None
        self.last_error: Optional[str] = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Установка соединения с Google Sheets"""
        try:
            logger.info("Инициализация Google Sheets Service")
            logger.debug(f"   Credentials file: {settings.google_credentials_file}")
            logger.debug(f"   Sheet ID configured: {'YES' if settings.google_sheet_id else 'NO'}")
            
            if not settings.google_sheet_id or not settings.google_sheet_id.strip():
                log_warning(logger, "Google Sheet ID не настроен! Функции сохранения данных отключены")
                logger.info("   💡 Для включения укажите GOOGLE_SHEET_ID в .env файле")
                self.last_error = "GOOGLE_SHEET_ID not configured"
                return
            
            self.creds = Credentials.from_service_account_file(
                settings.google_credentials_file,
                scopes=self.scope
            )
            self.client = gspread.authorize(self.creds)
            self.spreadsheet = self.client.open_by_key(settings.google_sheet_id)
            log_success(logger, "Google Sheets подключен", sheet_id=settings.google_sheet_id[:20]+"...")
            self.last_error = None
        except FileNotFoundError as e:
            log_error(logger, "Файл credentials не найден", error=e, file=settings.google_credentials_file)
            self.last_error = f"Credentials file not found: {settings.google_credentials_file}"
        except Exception as e:
            log_error(logger, "Ошибка подключения к Google Sheets", error=e)
            self.last_error = str(e)
    
    def _get_or_create_sheet(self, sheet_name: str):
        """Получить или создать лист в таблице"""
        if not self.spreadsheet:
            # Повышаем уровень видимости проблемы, чтобы было понятно почему не сохраняется
            log_warning(logger, "Google Sheets не инициализирован: пропуск операции", sheet=sheet_name)
            return None
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            return self.spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")

    def get_status(self) -> Dict:
        """Вернуть статус подключения и диагностику"""
        try:
            status = {
                "has_client": bool(self.client),
                "has_spreadsheet": bool(self.spreadsheet),
                "sheet_id": settings.google_sheet_id or "",
                "credentials_file": settings.google_credentials_file or "",
                "last_error": self.last_error or "",
            }
            return status
        except Exception as e:
            log_error(logger, "Ошибка получения статуса Google Sheets", error=e)
            return {"has_client": False, "has_spreadsheet": False, "last_error": str(e)}

    def reconnect(self) -> Dict:
        """Переинициализировать соединение и вернуть новый статус"""
        self.client = None
        self.spreadsheet = None
        self.creds = None
        self.last_error = None
        self._initialize_connection()
        return self.get_status()
    
    def save_user_data(self, user_data: Dict) -> bool:
        """Сохранить данные пользователя"""
        try:
            sheet = self._get_or_create_sheet("Users")
            if not sheet:
                logger.debug("Пропуск сохранения пользователя (Google Sheets не настроен)")
                return False
            
            # Добавляем заголовки, если лист пустой
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = ["ID", "ФИО", "Email", "Телефон", "Организация", 
                          "Должность", "Дата регистрации"]
                sheet.append_row(headers)
            
            row = [
                user_data.get("user_id", ""),
                user_data.get("full_name", ""),
                user_data.get("email", ""),
                user_data.get("phone", ""),
                user_data.get("organization", ""),
                user_data.get("position", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
            log_success(logger, "Пользователь сохранён в Google Sheets", user_id=user_data.get("user_id"))
            return True
        except Exception as e:
            log_error(logger, "Ошибка сохранения пользователя", error=e)
            return False
    
    def save_feedback(self, feedback: Dict) -> bool:
        """Сохранить обратную связь"""
        try:
            sheet = self._get_or_create_sheet("Feedback")
            if not sheet:
                logger.debug("Пропуск сохранения обратной связи (Google Sheets не настроен)")
                return False
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = ["User ID", "Сообщение", "Категория", "Дата"]
                sheet.append_row(headers)
            
            row = [
                feedback.get("user_id", ""),
                feedback.get("message", ""),
                feedback.get("category", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
            log_success(logger, "Обратная связь сохранена в Google Sheets", user_id=feedback.get("user_id"))
            return True
        except Exception as e:
            log_error(logger, "Ошибка сохранения обратной связи", error=e)
            return False
    
    def save_complaint(self, complaint: Dict) -> bool:
        """Сохранить жалобу"""
        try:
            sheet = self._get_or_create_sheet("Complaints")
            if not sheet:
                logger.debug("Пропуск сохранения жалобы (Google Sheets не настроен)")
                return False
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = ["ID", "User ID", "ФИО", "Email", "Телефон", 
                          "Организация", "Текст жалобы", "Категория", 
                          "Приоритет", "Статус", "Дата подачи", "Дата обработки"]
                sheet.append_row(headers)
            
            row = [
                complaint.get("complaint_id", ""),
                complaint.get("user_id", ""),
                complaint.get("full_name", ""),
                complaint.get("email", ""),
                complaint.get("phone", ""),
                complaint.get("organization", ""),
                complaint.get("complaint_text", ""),
                complaint.get("category", "Общая"),
                complaint.get("priority", "Средний"),
                "Новая",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ""
            ]
            sheet.append_row(row)
            log_success(logger, "Жалоба сохранена в Google Sheets", user_id=complaint.get("user_id"))
            return True
        except Exception as e:
            log_error(logger, "Ошибка сохранения жалобы", error=e)
            return False
    
    def save_chat_history(self, user_id: str, message: str, 
                         response: str) -> bool:
        """Сохранить историю чата"""
        try:
            sheet = self._get_or_create_sheet("ChatHistory")
            if not sheet:
                logger.debug("Пропуск сохранения истории чата (Google Sheets не настроен)")
                return False
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = ["User ID", "Сообщение пользователя", 
                          "Ответ ассистента", "Дата"]
                sheet.append_row(headers)
            
            row = [
                user_id,
                message[:100] + "..." if len(message) > 100 else message,  # Ограничим длину
                response[:200] + "..." if len(response) > 200 else response,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
            logger.debug(f"История чата сохранена для user_id={user_id}")
            return True
        except Exception as e:
            log_error(logger, "Ошибка сохранения истории чата", error=e, user_id=user_id)
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Получить всех пользователей"""
        try:
            sheet = self._get_or_create_sheet("Users")
            if not sheet:
                logger.debug("Пропуск получения пользователей (Google Sheets не настроен)")
                return []
            
            # Сначала пробуем получить данные с ожидаемыми заголовками
            try:
                data = sheet.get_all_records(expected_headers=[
                    "ID пользователя", "ФИО", "Имя", "Фамилия",
                    "Отчество", "Номер телефона", "Организация",
                    "Должность", "Email", "Дата регистрации"
                ])
                return data
            except Exception as header_error:
                # Если не получается с ожидаемыми заголовками, получаем все данные
                logger.warning(f"Не удалось получить данные с ожидаемыми заголовками: {header_error}")
                data = sheet.get_all_records()
                return data
        except Exception as e:
            log_error(logger, "Ошибка получения пользователей", error=e)
            return []
    
    def get_feedback(self, category: Optional[str] = None) -> List[Dict]:
        """Получить обратную связь"""
        try:
            sheet = self._get_or_create_sheet("Feedback")
            if not sheet:
                logger.debug("Пропуск получения обратной связи (Google Sheets не настроен)")
                return []
            data = sheet.get_all_records(expected_headers=[
                "ID мероприятия", "Название", "Дата", "Время", 
                "Описание", "Место проведения", "Участники", 
                "Организатор", "Статус", "Дата создания"
            ])
            
            if category:
                data = [fb for fb in data if fb.get("Категория") == category]
            
            return data
        except Exception as e:
            log_error(logger, "Ошибка получения обратной связи", error=e)
            return []
    
    def get_events(self) -> List[Dict]:
        """Получить список мероприятий"""
        try:
            sheet = self._get_or_create_sheet("Events")
            if not sheet:
                logger.debug("Пропуск получения мероприятий (Google Sheets не настроен)")
                return []
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = ["Название", "Дата", "Описание", "Участники"]
                sheet.append_row(headers)
                return []
            
            data = sheet.get_all_records(expected_headers=[
                "ID мероприятия", "Название", "Дата", "Время", 
                "Описание", "Место проведения", "Участники", 
                "Организатор", "Статус", "Дата создания"
            ])
            return data
        except Exception as e:
            log_error(logger, "Ошибка получения мероприятий", error=e)
            return []
    
    def save_legislation_update(self, title: str, url: str, 
                                date: str) -> bool:
        """Сохранить информацию об изменении законодательства"""
        try:
            sheet = self._get_or_create_sheet("Legislation")
            if not sheet:
                logger.debug("Пропуск сохранения изменения законодательства (Google Sheets не настроен)")
                return False
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = ["Название", "URL", "Дата публикации", "Дата добавления"]
                sheet.append_row(headers)
            
            row = [
                title,
                url,
                date,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
            log_success(logger, "Изменение законодательства сохранено в Google Sheets", title=title)
            return True
        except Exception as e:
            log_error(logger, "Ошибка сохранения изменения законодательства", error=e)
            return False
    
    def save_document(self, document_data: Dict) -> bool:
        """
        Сохранить информацию о созданном документе
        
        Args:
            document_data: Данные о документе
                - user_id: ID пользователя
                - full_name: ФИО пользователя
                - email: Email пользователя
                - template_name: Название шаблона
                - document_type: Тип документа
                - filepath: Путь к файлу
                - download_url: URL для скачивания
                - completeness_score: Полнота данных (%)
                - confidence_score: Уверенность (%)
                - data_quality: Качество данных
        
        Returns:
            True если успешно, False если ошибка
        """
        try:
            sheet = self._get_or_create_sheet("Documents")
            if not sheet:
                logger.debug("Пропуск сохранения документа (Google Sheets не настроен)")
                return False
            
            # Добавляем заголовки, если лист пустой
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = [
                    "User ID", 
                    "ФИО", 
                    "Email", 
                    "Тип документа",
                    "Название шаблона", 
                    "Имя файла",
                    "Ссылка на скачивание",
                    "Полнота данных (%)",
                    "Уверенность (%)",
                    "Качество",
                    "Дата создания"
                ]
                sheet.append_row(headers)
            
            # Формируем полную ссылку на скачивание
            from config import settings
            base_url = settings.base_url
            download_url = document_data.get("download_url", "")
            if download_url and not download_url.startswith("http"):
                download_url = f"{base_url}{download_url}"
            
            # Корректно извлекаем имя файла для путей Windows и POSIX
            filepath = document_data.get("filepath") or ""
            filename = os.path.basename(filepath) if filepath else ""
            
            row = [
                document_data.get("user_id", ""),
                document_data.get("full_name", ""),
                document_data.get("email", ""),
                document_data.get("document_type", ""),
                document_data.get("template_name", ""),
                filename,
                download_url,
                document_data.get("completeness_score", ""),
                document_data.get("confidence_score", ""),
                document_data.get("data_quality", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            
            sheet.append_row(row)
            # Дополнительный лог, если ключевые поля пустые — помогает отладить "нулевые" записи
            if not any([row[0], row[1], row[2], row[3], row[4], row[5], row[6]]):
                log_warning(logger, "Документ сохранен, но большинство полей пустые", 
                            filepath=filepath, download_url=download_url)
            else:
                log_success(logger, "Документ сохранен в Google Sheets", 
                           user_id=document_data.get("user_id"), filename=filename)
            return True
            
        except Exception as e:
            log_error(logger, "Ошибка сохранения документа в Google Sheets", error=e)
            return False

    def save_event(self, event_data: Dict) -> bool:
        """Сохранить данные о мероприятии"""
        try:
            sheet = self._get_or_create_sheet("Events")
            if not sheet:
                logger.debug("Пропуск сохранения мероприятия (Google Sheets не настроен)")
                return False
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = [
                    "ID мероприятия", "Название", "Дата", "Время", 
                    "Описание", "Место проведения", "Участники", 
                    "Организатор", "Статус", "Дата создания"
                ]
                sheet.append_row(headers)
            
            participants_str = ", ".join(event_data.get("participants", []))
            
            row = [
                event_data.get("event_id", ""),
                event_data.get("title", ""),
                event_data.get("date", ""),
                event_data.get("time", ""),
                event_data.get("description", ""),
                event_data.get("location", ""),
                participants_str,
                event_data.get("organizer", ""),
                event_data.get("status", "Запланировано"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
            log_success(logger, "Мероприятие сохранено в Google Sheets", 
                       event_id=event_data.get("event_id"))
            return True
        except Exception as e:
            log_error(logger, "Ошибка сохранения мероприятия", error=e)
            return False

    def save_legislation(self, legislation_data: Dict) -> bool:
        """Сохранить данные о законодательстве"""
        try:
            sheet = self._get_or_create_sheet("Legislation")
            if not sheet:
                logger.debug("Пропуск сохранения законодательства (Google Sheets не настроен)")
                return False
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = [
                    "Название", "URL", "Дата публикации", "Описание", 
                    "Категория", "Важность", "Дата добавления"
                ]
                sheet.append_row(headers)
            
            row = [
                legislation_data.get("title", ""),
                legislation_data.get("url", ""),
                legislation_data.get("publication_date", ""),
                legislation_data.get("description", ""),
                legislation_data.get("category", ""),
                legislation_data.get("importance", "Средняя"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
            log_success(logger, "Законодательство сохранено в Google Sheets", 
                       title=legislation_data.get("title"))
            return True
        except Exception as e:
            log_error(logger, "Ошибка сохранения законодательства", error=e)
            return False

    def save_chat_analytics(self, analytics_data: Dict) -> bool:
        """Сохранить данные аналитики чата"""
        try:
            sheet = self._get_or_create_sheet("ChatAnalytics")
            if not sheet:
                logger.debug("Пропуск сохранения аналитики чата (Google Sheets не настроен)")
                return False
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = [
                    "ID сессии", "User ID", "Количество сообщений", 
                    "Среднее время ответа (сек)", "Оценка удовлетворенности", 
                    "Обсуждаемые темы", "Создано документов", 
                    "Длительность сессии (сек)", "Дата создания"
                ]
                sheet.append_row(headers)
            
            topics_str = ", ".join(analytics_data.get("topics_discussed", []))
            
            row = [
                analytics_data.get("session_id", ""),
                analytics_data.get("user_id", ""),
                analytics_data.get("message_count", 0),
                analytics_data.get("response_time_avg", 0.0),
                analytics_data.get("satisfaction_score", ""),
                topics_str,
                analytics_data.get("documents_created", 0),
                analytics_data.get("session_duration", 0),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
            log_success(logger, "Аналитика чата сохранена в Google Sheets", 
                       session_id=analytics_data.get("session_id"))
            return True
        except Exception as e:
            log_error(logger, "Ошибка сохранения аналитики чата", error=e)
            return False

    def get_complaints(self, status: Optional[str] = None) -> List[Dict]:
        """Получить список жалоб"""
        try:
            sheet = self._get_or_create_sheet("Complaints")
            if not sheet:
                logger.debug("Пропуск получения жалоб (Google Sheets не настроен)")
                return []
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                return []
            
            data = sheet.get_all_records(expected_headers=[
                "ID мероприятия", "Название", "Дата", "Время", 
                "Описание", "Место проведения", "Участники", 
                "Организатор", "Статус", "Дата создания"
            ])
            
            if status:
                data = [c for c in data if c.get("Статус") == status]
            
            return data
        except Exception as e:
            log_error(logger, "Ошибка получения жалоб", error=e)
            return []

    def get_events(self, status: Optional[str] = None) -> List[Dict]:
        """Получить список мероприятий"""
        try:
            sheet = self._get_or_create_sheet("Events")
            if not sheet:
                logger.debug("Пропуск получения мероприятий (Google Sheets не настроен)")
                return []
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                return []
            
            data = sheet.get_all_records()
            
            if status:
                data = [e for e in data if e.get("Статус") == status]
            
            return data
        except Exception as e:
            log_error(logger, "Ошибка получения мероприятий", error=e)
            return []

    def get_legislation(self, category: Optional[str] = None) -> List[Dict]:
        """Получить список законодательства"""
        try:
            sheet = self._get_or_create_sheet("Legislation")
            if not sheet:
                logger.debug("Пропуск получения законодательства (Google Sheets не настроен)")
                return []
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                return []
            
            data = sheet.get_all_records(expected_headers=[
                "ID мероприятия", "Название", "Дата", "Время", 
                "Описание", "Место проведения", "Участники", 
                "Организатор", "Статус", "Дата создания"
            ])
            
            if category:
                data = [l for l in data if l.get("Категория") == category]
            
            return data
        except Exception as e:
            log_error(logger, "Ошибка получения законодательства", error=e)
            return []

    def get_chat_analytics(self, user_id: Optional[str] = None) -> List[Dict]:
        """Получить аналитику чата"""
        try:
            sheet = self._get_or_create_sheet("ChatAnalytics")
            if not sheet:
                logger.debug("Пропуск получения аналитики чата (Google Sheets не настроен)")
                return []
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                return []
            
            data = sheet.get_all_records(expected_headers=[
                "ID мероприятия", "Название", "Дата", "Время", 
                "Описание", "Место проведения", "Участники", 
                "Организатор", "Статус", "Дата создания"
            ])
            
            if user_id:
                data = [a for a in data if a.get("User ID") == user_id]
            
            return data
        except Exception as e:
            log_error(logger, "Ошибка получения аналитики чата", error=e)
            return []


# Singleton instance
google_sheets_service = GoogleSheetsService()

