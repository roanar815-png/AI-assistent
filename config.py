"""
Конфигурация приложения
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # OpenAI / DeepSeek
    openai_api_key: str = "sk-a74ad479a22247f499901068a59377ff"
    deepseek_base_url: str = "https://api.deepseek.com"
    
    # Google
    google_credentials_file: str = "my-sheets-ai-assistant-d59c589763f8.json"
    google_sheet_id: str = ""  # НУЖНО УКАЗАТЬ ID ВАШЕЙ GOOGLE ТАБЛИЦЫ
    
    # Application
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Monitoring
    legislation_urls: str = "https://www.consultant.ru/law/hotdocs/"
    
    # Email
    gmail_user: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

