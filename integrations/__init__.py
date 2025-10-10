"""
Интеграции с внешними сервисами
"""
from .google_sheets import google_sheets_service
from .openai_service import openai_service
from .gmail_service import gmail_service

__all__ = [
    "google_sheets_service",
    "openai_service",
    "gmail_service"
]

