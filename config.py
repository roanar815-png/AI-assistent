"""
Конфигурация приложения
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Environment mode: 'local' or 'production'
    environment: str = os.getenv("ENVIRONMENT", "local")  # По умолчанию локальный режим
    
    # OpenAI / DeepSeek (секреты берутся из переменных окружения)
    openai_api_key: str = ""
    deepseek_base_url: Optional[str] = None  # None = используем OpenAI API с прокси
    
    # Proxy settings for OpenAI access
    # Прокси ВСЕГДА включен для работы с OpenAI API
    proxy_enabled: bool = True  # Включен для работы с OpenAI API
    proxy_ip: str = os.getenv("PROXY_IP", "")
    proxy_port: int = int(os.getenv("PROXY_PORT", "0") or 0)
    proxy_login: str = os.getenv("PROXY_LOGIN", "")
    proxy_password: str = os.getenv("PROXY_PASSWORD", "")
    
    # Google
    google_credentials_file: str = "my-sheets-ai-assistant-d59c589763f8.json"
    google_sheet_id: str = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"  # ID Google таблицы
    
    # Application
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Docker ports
    http_port: int = 80
    api_port: int = 8000
    
    # Monitoring
    legislation_urls: str = "https://www.consultant.ru/law/hotdocs/"
    
    # Email
    gmail_user: str = ""
    
    # Base URL for download links (используется для абсолютных ссылок в email и UI)
    # Берется из переменной окружения BASE_URL, по умолчанию localhost
    base_url: str = os.getenv("BASE_URL", "http://localhost")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Разрешаем дополнительные поля

settings = Settings()

# Логируем активные настройки окружения и базовый адрес
print(f"ENVIRONMENT={settings.environment}; BASE_URL={settings.base_url}; DEBUG={settings.debug}")

