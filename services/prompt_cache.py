"""
Кэш для оптимизированных промптов
"""
from typing import Dict
import hashlib

class PromptCache:
    """Кэш для часто используемых промптов"""
    
    def __init__(self):
        self.cache = {}
        self.system_prompts = self._get_optimized_prompts()
    
    def _get_optimized_prompts(self) -> Dict[str, str]:
        """Оптимизированные системные промпты"""
        return {
            "chat": """Ты — AI ассистент "Опора России" для малого и среднего бизнеса. 
Отвечай кратко и по делу. Помогай с документами, законодательством и бизнес-вопросами.""",
            
            "extract_user_data": """Извлеки данные пользователя из диалога. 
Верни JSON с полями: full_name, email, phone, organization, position.""",
            
            "detect_intent": """Определи намерение: application (заявка), document (документ), complaint (жалоба), other.
Верни JSON: {"intent": "тип", "data": {...}}""",
            
            "document_analysis": """Проанализируй, нужен ли документ. 
Верни JSON: {"suggested": true/false, "template_id": "id", "needs_data": true/false}"""
        }
    
    def get_system_prompt(self, prompt_type: str) -> str:
        """Получить системный промпт по типу"""
        return self.system_prompts.get(prompt_type, self.system_prompts["chat"])
    
    def get_cache_key(self, prompt: str, context: str = "") -> str:
        """Генерировать ключ кэша"""
        content = f"{prompt}:{context}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

# Глобальный экземпляр
prompt_cache = PromptCache()
