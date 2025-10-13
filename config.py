"""
Конфигурация приложения
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Environment mode: 'local' or 'production'
    environment: str = "production"  # По умолчанию продакшн режим
    
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
    
    # Base URL for download links
    base_url: str = "https://sandbox1.facex.pro"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Разрешаем дополнительные поля

settings = Settings()

# Автоматическое переключение настроек в зависимости от режима
if settings.environment == "local":
    # ЛОКАЛЬНЫЙ РЕЖИМ: http://localhost/main-interface.html
    # Прокси ВСЕГДА включен для работы с OpenAI API
    settings.proxy_enabled = True
    settings.base_url = "http://localhost"
    settings.debug = True
    print(f"ЛОКАЛЬНЫЙ РЕЖИМ: {settings.base_url}/main-interface.html (с прокси для API)")
else:  # production
    # ПРОДАКШН РЕЖИМ: https://sandbox1.facex.pro
    settings.proxy_enabled = True
    settings.base_url = "https://sandbox1.facex.pro"
    settings.debug = False
    print(f"ПРОДАКШН РЕЖИМ: {settings.base_url}")

