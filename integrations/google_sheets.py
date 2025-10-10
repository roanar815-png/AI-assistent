"""
Интеграция с Google Sheets для хранения данных
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Optional
from datetime import datetime
from config import settings
from logger_config import get_logger, log_success, log_error, log_warning

# Инициализация логгера
logger = get_logger(__name__)


class GoogleSheetsService:
    """Сервис для работы с Google Sheets"""
    
    def __init__(self):
        """Инициализация подключения к Google Sheets"""
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.creds = None
        self.client = None
        self.spreadsheet = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Установка соединения с Google Sheets"""
        try:
            logger.info("🔧 Инициализация Google Sheets Service")
            logger.debug(f"   Credentials file: {settings.google_credentials_file}")
            logger.debug(f"   Sheet ID configured: {'YES' if settings.google_sheet_id else 'NO'}")
            
            if not settings.google_sheet_id or not settings.google_sheet_id.strip():
                log_warning(logger, "Google Sheet ID не настроен! Функции сохранения данных отключены")
                logger.info("   💡 Для включения укажите GOOGLE_SHEET_ID в .env файле")
                return
            
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(
                settings.google_credentials_file,
                self.scope
            )
            self.client = gspread.authorize(self.creds)
            self.spreadsheet = self.client.open_by_key(settings.google_sheet_id)
            log_success(logger, "Google Sheets подключен", sheet_id=settings.google_sheet_id[:20]+"...")
        except FileNotFoundError as e:
            log_error(logger, "Файл credentials не найден", error=e, file=settings.google_credentials_file)
        except Exception as e:
            log_error(logger, "Ошибка подключения к Google Sheets", error=e)
    
    def _get_or_create_sheet(self, sheet_name: str):
        """Получить или создать лист в таблице"""
        if not self.spreadsheet:
            logger.debug(f"Google Sheets не настроен, пропуск операции: {sheet_name}")
            return None
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            return self.spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
    
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
    
    def save_application(self, application: Dict) -> bool:
        """Сохранить заявку на вступление"""
        try:
            sheet = self._get_or_create_sheet("Applications")
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = ["ID", "ФИО", "Организация", "ИНН", "Email", 
                          "Телефон", "Тип бизнеса", "Комментарий", "Дата подачи", "Статус"]
                sheet.append_row(headers)
            
            row = [
                application.get("user_id", ""),
                application.get("full_name", ""),
                application.get("organization", ""),
                application.get("inn", ""),
                application.get("email", ""),
                application.get("phone", ""),
                application.get("business_type", ""),
                application.get("comment", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Новая"
            ]
            sheet.append_row(row)
            return True
        except Exception as e:
            print(f"Ошибка сохранения заявки: {e}")
            return False
    
    def save_feedback(self, feedback: Dict) -> bool:
        """Сохранить обратную связь"""
        try:
            sheet = self._get_or_create_sheet("Feedback")
            
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
            return True
        except Exception as e:
            print(f"Ошибка сохранения обратной связи: {e}")
            return False
    
    def save_complaint(self, complaint: Dict) -> bool:
        """Сохранить жалобу"""
        try:
            sheet = self._get_or_create_sheet("Complaints")
            
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
            return True
        except Exception as e:
            print(f"Ошибка сохранения жалобы: {e}")
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
            data = sheet.get_all_records()
            return data
        except Exception as e:
            print(f"Ошибка получения пользователей: {e}")
            return []
    
    def get_applications(self, status: Optional[str] = None) -> List[Dict]:
        """Получить заявки"""
        try:
            sheet = self._get_or_create_sheet("Applications")
            data = sheet.get_all_records()
            
            if status:
                data = [app for app in data if app.get("Статус") == status]
            
            return data
        except Exception as e:
            print(f"Ошибка получения заявок: {e}")
            return []
    
    def get_feedback(self, category: Optional[str] = None) -> List[Dict]:
        """Получить обратную связь"""
        try:
            sheet = self._get_or_create_sheet("Feedback")
            data = sheet.get_all_records()
            
            if category:
                data = [fb for fb in data if fb.get("Категория") == category]
            
            return data
        except Exception as e:
            print(f"Ошибка получения обратной связи: {e}")
            return []
    
    def get_events(self) -> List[Dict]:
        """Получить список мероприятий"""
        try:
            sheet = self._get_or_create_sheet("Events")
            
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = ["Название", "Дата", "Описание", "Участники"]
                sheet.append_row(headers)
                return []
            
            data = sheet.get_all_records()
            return data
        except Exception as e:
            print(f"Ошибка получения мероприятий: {e}")
            return []
    
    def save_legislation_update(self, title: str, url: str, 
                                date: str) -> bool:
        """Сохранить информацию об изменении законодательства"""
        try:
            sheet = self._get_or_create_sheet("Legislation")
            
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
            return True
        except Exception as e:
            print(f"Ошибка сохранения изменения законодательства: {e}")
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
            base_url = "http://localhost:8000"  # TODO: брать из конфигурации
            download_url = document_data.get("download_url", "")
            if download_url and not download_url.startswith("http"):
                download_url = f"{base_url}{download_url}"
            
            filename = document_data.get("filepath", "").split("/")[-1] if document_data.get("filepath") else ""
            
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
            print(f"[OK] Документ сохранен в Google Sheets: {filename}", flush=True)
            return True
            
        except Exception as e:
            print(f"[ERROR] Ошибка сохранения документа в Google Sheets: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False


# Singleton instance
google_sheets_service = GoogleSheetsService()

