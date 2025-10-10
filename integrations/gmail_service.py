"""
Интеграция с Gmail API для отправки рассылок
"""
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
from typing import List
from config import settings


class GmailService:
    """Сервис для работы с Gmail API"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self):
        """Инициализация Gmail сервиса"""
        self.service = None
    
    def _initialize_service(self):
        """Инициализация подключения к Gmail API"""
        creds = None
        
        # Токен сохраняется для повторного использования
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # Если нет валидных учетных данных
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        settings.google_credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0, open_browser=True)
                except Exception as e:
                    print(f"Ошибка авторизации Gmail: {e}")
                    return
            
            # Сохранение токена
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"Ошибка создания Gmail сервиса: {e}")
    
    def send_document(self, to_email: str, subject: str, body: str, 
                     attachment_path: str) -> bool:
        """
        Отправить email с вложением
        
        Args:
            to_email: Email получателя
            subject: Тема письма
            body: Текст письма
            attachment_path: Путь к файлу для вложения
        
        Returns:
            True если отправлено успешно
        """
        try:
            if not self.service:
                print("Gmail сервис не инициализирован")
                return False
            
            # Создаем сообщение с вложением
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            
            # Добавляем текст письма
            message.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Добавляем вложение
            if os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as attachment:
                    from email.mime.base import MIMEBase
                    from email import encoders
                    
                    part = MIMEBase('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(attachment_path)}')
                    message.attach(part)
            
            # Кодируем сообщение
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Отправляем
            send_message = self.service.users().messages().send(
                userId='me', 
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email отправлен: {send_message['id']}")
            return True
            
        except Exception as e:
            print(f"Ошибка отправки email с вложением: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   html: bool = False) -> bool:
        """
        Отправить email
        
        Args:
            to_email: Email получателя
            subject: Тема письма
            body: Текст письма
            html: Использовать HTML формат
        
        Returns:
            True если успешно отправлено
        """
        try:
            # Инициализируем сервис если нужно
            if not self.service:
                self._initialize_service()
            
            if not self.service:
                print("Gmail сервис не инициализирован")
                return False
            
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            
            if html:
                message.attach(MIMEText(body, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            return True
            
        except Exception as e:
            print(f"Ошибка отправки email: {e}")
            return False
    
    def send_bulk_email(self, recipients: List[str], subject: str, 
                       body: str, html: bool = False) -> int:
        """
        Массовая рассылка email
        
        Args:
            recipients: Список email получателей
            subject: Тема письма
            body: Текст письма
            html: Использовать HTML формат
        
        Returns:
            Количество успешно отправленных писем
        """
        sent_count = 0
        
        for recipient in recipients:
            if self.send_email(recipient, subject, body, html):
                sent_count += 1
        
        return sent_count
    
    def send_bulk_email_with_delay(self, recipients: List[str], subject: str, 
                                  body: str, html: bool = False, 
                                  delay_seconds: int = 1) -> int:
        """
        Массовая рассылка email с задержкой между отправками
        
        Args:
            recipients: Список email получателей
            subject: Тема письма
            body: Текст письма
            html: Использовать HTML формат
            delay_seconds: Задержка между отправками в секундах
        
        Returns:
            Количество успешно отправленных писем
        """
        import time
        sent_count = 0
        
        for i, recipient in enumerate(recipients):
            if self.send_email(recipient, subject, body, html):
                sent_count += 1
                print(f"Отправлено {i+1}/{len(recipients)}: {recipient}")
            
            # Задержка между отправками (кроме последнего письма)
            if i < len(recipients) - 1:
                time.sleep(delay_seconds)
        
        return sent_count
    
    def send_event_reminder(self, to_email: str, event_title: str, 
                           event_date: str, event_description: str) -> bool:
        """
        Отправить напоминание о мероприятии
        
        Args:
            to_email: Email получателя
            event_title: Название мероприятия
            event_date: Дата мероприятия
            event_description: Описание
        
        Returns:
            True если успешно отправлено
        """
        subject = f"Напоминание: {event_title}"
        
        body = f"""
Здравствуйте!

Напоминаем вам о предстоящем мероприятии:

Название: {event_title}
Дата: {event_date}

Описание:
{event_description}

С уважением,
Команда "Опора России"
"""
        
        return self.send_email(to_email, subject, body)


# Singleton instance
gmail_service = GmailService()

