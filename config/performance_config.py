"""
Конфигурация для оптимизации производительности
"""
from typing import Dict, Any
from pydantic import BaseModel


class PerformanceConfig(BaseModel):
    """Конфигурация производительности"""
    
    # Кэширование
    cache_ttl: int = 3600  # TTL кэша в секундах (1 час)
    cache_max_size: int = 1000  # Максимальный размер кэша
    cache_cleanup_interval: int = 300  # Интервал очистки кэша (5 минут)
    
    # Асинхронная обработка
    max_concurrent_requests: int = 50  # Максимум одновременных запросов
    request_timeout: int = 60  # Таймаут запроса в секундах
    batch_size: int = 5  # Размер пакета для пакетной обработки
    batch_timeout: float = 0.5  # Таймаут пакета в секундах
    
    # Управление памятью
    max_history_length: int = 20  # Максимальная длина истории диалога
    memory_cleanup_interval: int = 300  # Интервал очистки памяти (5 минут)
    inactive_session_timeout: int = 3600  # Таймаут неактивной сессии (1 час)
    
    # Пулы соединений
    max_keepalive_connections: int = 20  # Максимум keep-alive соединений
    max_connections: int = 50  # Максимум соединений
    keepalive_expiry: float = 30.0  # Время жизни соединений
    
    # Мониторинг
    metrics_collection_interval: int = 60  # Интервал сбора метрик (1 минута)
    performance_logging: bool = True  # Включить логирование производительности
    
    # Оптимизации API
    temperature: float = 0.7  # Температура для API запросов
    max_tokens: int = 2000  # Максимум токенов в ответе
    api_retry_attempts: int = 2  # Количество попыток повтора API
    
    # Сжатие контекста
    context_compression_enabled: bool = True  # Включить сжатие контекста
    max_context_messages: int = 6  # Максимум сообщений в контексте
    
    # Предварительные вычисления
    precompute_embeddings: bool = False  # Предварительное вычисление эмбеддингов
    embedding_cache_size: int = 100  # Размер кэша эмбеддингов


# Глобальная конфигурация
performance_config = PerformanceConfig()


def get_optimized_settings() -> Dict[str, Any]:
    """Получить оптимизированные настройки"""
    return {
        "cache": {
            "ttl": performance_config.cache_ttl,
            "max_size": performance_config.cache_max_size,
            "cleanup_interval": performance_config.cache_cleanup_interval
        },
        "async": {
            "max_concurrent": performance_config.max_concurrent_requests,
            "timeout": performance_config.request_timeout,
            "batch_size": performance_config.batch_size,
            "batch_timeout": performance_config.batch_timeout
        },
        "memory": {
            "max_history": performance_config.max_history_length,
            "cleanup_interval": performance_config.memory_cleanup_interval,
            "inactive_timeout": performance_config.inactive_session_timeout
        },
        "connections": {
            "max_keepalive": performance_config.max_keepalive_connections,
            "max_connections": performance_config.max_connections,
            "keepalive_expiry": performance_config.keepalive_expiry
        },
        "api": {
            "temperature": performance_config.temperature,
            "max_tokens": performance_config.max_tokens,
            "retry_attempts": performance_config.api_retry_attempts
        }
    }
