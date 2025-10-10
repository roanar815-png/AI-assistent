"""
Бизнес-логика сервисов
"""
from .assistant_service import assistant_service
from .report_service import report_service
from .document_service import document_service
from .monitoring_service import monitoring_service

__all__ = [
    "assistant_service",
    "report_service",
    "document_service",
    "monitoring_service"
]

