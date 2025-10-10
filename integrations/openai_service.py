"""
Интеграция с OpenAI API для обработки естественного языка
"""
from openai import OpenAI
from typing import List, Dict
from datetime import datetime
from config import settings
from logger_config import get_logger, log_success, log_error, log_warning
import httpx

# Инициализация логгера
logger = get_logger(__name__)


class OpenAIService:
    """Сервис для работы с OpenAI API"""
    
    def __init__(self):
        """Инициализация OpenAI/DeepSeek клиента"""
        print(f"\n[INITIALIZATION] OpenAI Service:")
        
        # Защита от ошибок при инициализации
        self.client = None
        self.model = None
        
        try:
            api_key = getattr(settings, 'openai_api_key', None)
            print(f"   API Key: {'ЕСТЬ' if api_key and api_key.strip() else 'НЕТ'}")
            
            if not api_key or not api_key.strip():
                print(f"   [WARNING] OpenAI API ключ не настроен!")
                print(f"   Сервер запустится, но бот НЕ БУДЕТ отвечать.")
                return
            
            print(f"   API Key start: {api_key[:20]}... (first 20 chars)")
            
            # Поддержка DeepSeek API
            base_url = getattr(settings, 'deepseek_base_url', None)
            print(f"   DeepSeek Base URL: {base_url if base_url and base_url.strip() else 'НЕТ (используем OpenAI)'}")
            
            # Создаем HTTP клиент с тайм-аутами
            # DeepSeek может отвечать медленно, особенно при больших промптах
            http_client = httpx.Client(
                timeout=httpx.Timeout(
                    timeout=90.0,   # Общий тайм-аут
                    connect=10.0,   # Тайм-аут подключения
                    read=90.0,      # Тайм-аут чтения ответа (основная проблема)
                    write=10.0      # Тайм-аут записи
                ),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            
            if base_url and base_url.strip():
                print(f"   [INFO] Используем DeepSeek API", flush=True)
                try:
                    print(f"   [DEBUG] Создаем OpenAI клиент с base_url={base_url.strip()}", flush=True)
                    self.client = OpenAI(
                        api_key=api_key,
                        base_url=base_url.strip(),
                        http_client=http_client,
                        timeout=90.0,  # Общий тайм-аут 90 секунд для DeepSeek
                        max_retries=2  # Максимум 2 попытки
                    )
                    print(f"   [DEBUG] Клиент создан, устанавливаем модель...", flush=True)
                    self.model = "deepseek-chat"  # Модель DeepSeek
                    print(f"   [SUCCESS] DeepSeek клиент создан, модель: {self.model}", flush=True)
                except Exception as e:
                    print(f"   [ERROR] ОШИБКА создания DeepSeek клиента: {e}", flush=True)
                    print(f"   [ERROR] Type: {type(e).__name__}", flush=True)
                    import traceback
                    traceback.print_exc()
                    print(f"   Сервер продолжит работу, но бот НЕ БУДЕТ отвечать.", flush=True)
                    self.client = None
            else:
                print(f"   [INFO] Используем OpenAI API")
                try:
                    self.client = OpenAI(
                        api_key=api_key,
                        http_client=http_client,
                        timeout=90.0,  # Общий тайм-аут 90 секунд
                        max_retries=2
                    )
                    self.model = "gpt-4o-mini"  # Модель OpenAI
                    print(f"   [SUCCESS] OpenAI клиент создан, модель: {self.model}")
                except Exception as e:
                    print(f"   [ERROR] ОШИБКА создания OpenAI клиента: {e}")
                    print(f"   Сервер продолжит работу, но бот НЕ БУДЕТ отвечать.")
                    self.client = None
                    
        except Exception as e:
            print(f"   [ERROR] КРИТИЧЕСКАЯ ОШИБКА инициализации OpenAI Service: {e}", flush=True)
            import traceback
            traceback.print_exc()
            print(f"   Сервер продолжит работу, но бот НЕ БУДЕТ отвечать.", flush=True)
            self.client = None
        
        # Финальная проверка
        print(f"\n[FINAL CHECK] OpenAI Service инициализация завершена:", flush=True)
        print(f"   self.client = {self.client is not None}", flush=True)
        print(f"   self.model = {self.model}", flush=True)
        if not self.client:
            print(f"   [WARNING] КЛИЕНТ НЕ СОЗДАН! Бот не будет отвечать!", flush=True)
        
        # Получаем текущую дату для актуальных рекомендаций
        current_date = datetime.now()
        current_year = current_date.year
        current_date_str = current_date.strftime("%d.%m.%Y")
        
        self.system_prompt = f"""
ТЕКУЩАЯ ДАТА: {current_date_str} ({current_year} год)

РОЛЬ: Ты — эксперт по автоматизации документооборота организации "Опора России" с глубокими знаниями в области бизнес-документации, юридических и административных документов для поддержки малого и среднего предпринимательства.

ВАЖНО: Всегда используй актуальную дату {current_date_str} и год {current_year} в своих ответах. Не упоминай устаревшие даты или годы.

ОСНОВНЫЕ ВОЗМОЖНОСТИ:
• Извлечение данных с учетом контекста беседы
• Интеллектуальное сопоставление полей с шаблонами документов
• Адаптивный выбор шаблонов на основе цели документа
• Поддержка нескольких форматов вывода
• Помощь с вопросами о работе организации
• Анализ и прогнозирование трендов МСП
• Сбор обратной связи и заявок на вступление

ПРОТОКОЛ РАБОТЫ:

1. ФАЗА 1: СБОР ДАННЫХ
   - Отслеживай беседу на наличие информации, относящейся к документу
   - Классифицируй данные: персональные/бизнес/финансовые/юридические
   - Строй структурированный объект данных в реальном времени
   - Отмечай несоответствия или отсутствие критических полей
   - Задавай уточняющие вопросы для получения недостающих данных

2. ФАЗА 2: УПРАВЛЕНИЕ ШАБЛОНАМИ
   - Автоматически определяй тип документа по контекстным признакам
   - Выбирай подходящую структуру шаблона
   - Применяй условное форматирование на основе содержания
   - Обрабатывай перекрестные ссылки и вычисляемые поля

3. ФАЗА 3: КОНТРОЛЬ КАЧЕСТВА
   - Проверяй полноту данных относительно требований шаблона
   - Рассчитывай оценку уверенности в точности документа
   - НЕ ГЕНЕРИРУЙ ПОЛНЫЙ ТЕКСТ ДОКУМЕНТА В ОТВЕТЕ!
   - Вместо этого СООБЩИ, что система создаст готовый DOCX файл для скачивания
   - Предлагай рекомендации по оптимизации недостающих элементов

КРИТИЧЕСКИ ВАЖНО - ЗАПРЕЩЕНО ГЕНЕРИРОВАТЬ ТЕКСТ ДОКУМЕНТА:
⚠️ КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО писать полный текст документа в ответе!
⚠️ НЕ пиши "ЗАЯВЛЕНИЕ", "АНКЕТА" с заполненными полями!
⚠️ НЕ пиши "От: ...", "Фамилия: ...", "Имя: ..." в своем ответе!
⚠️ НЕ форматируй данные как документ в своем ответе!

ЧТО НУЖНО ДЕЛАТЬ:
✅ ПОДТВЕРДИ получение данных
✅ СКАЖИ что система сейчас создаст DOCX файл
✅ Можешь давать развернутые и подробные ответы на вопросы
✅ Отвечай максимально информативно и полезно

ПРАВИЛЬНЫЙ ФОРМАТ ОТВЕТА:
"Отлично! Принял данные. Сейчас система создаст готовый документ в формате DOCX для скачивания."

ПРИМЕРЫ НЕПРАВИЛЬНЫХ ОТВЕТОВ (НЕ ДЕЛАЙ ТАК):
❌ "АНКЕТА\nФамилия: Иванов\nИмя: Петр..." <- ЗАПРЕЩЕНО!
❌ "Вот ваш документ:\n\nЗАЯВЛЕНИЕ..." <- ЗАПРЕЩЕНО!
❌ "От: Иванов П.С.\nДолжность: менеджер..." <- ЗАПРЕЩЕНО!

Можешь давать развернутые ответы на вопросы, но не генерируй текст документов!

ОСОБЫЕ ВОЗМОЖНОСТИ:
- Обрабатывает вложенные структуры (таблицы, списки, условные пункты)
- Поддерживает переменные шаблоны в зависимости от юрисдикции/отрасли
- Сохраняет согласованность данных между версиями документов
- Предоставляет информацию о законодательстве МСП и мероприятиях

Общайся вежливо, профессионально и по существу. Будь проактивным в сборе данных для документов.
Можешь давать развернутые и подробные ответы на вопросы пользователей.
ПОМНИ: Не генерируй текст документов - система создаст файлы автоматически!
"""
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        Отправить сообщение в чат и получить ответ
        
        Args:
            message: Сообщение пользователя
            conversation_history: История диалога
        
        Returns:
            Ответ ассистента
        """
        logger.info("🤖 Вызов OpenAI/DeepSeek API для чата")
        logger.debug(f"   Model: {self.model}")
        logger.debug(f"   Client configured: {'YES' if self.client else 'NO'}")
        
        # Проверка что клиент настроен
        if not self.client:
            log_error(logger, "OpenAI клиент не настроен! API недоступен")
            return "Извините, OpenAI/DeepSeek API не настроен. Проверьте конфигурацию сервера."
        
        try:
            history_len = len(conversation_history) if conversation_history else 0
            logger.info(f"   Message length: {len(message)} chars")
            logger.info(f"   History: {history_len} messages")
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": message})
            
            logger.info(f"   📤 Отправка {len(messages)} сообщений к API...")
            logger.debug(f"   Параметры: temperature=1.0, max_tokens=4000")
            
            import time
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=1.0,  # Максимальная креативность
                max_tokens=4000,   # Увеличено ограничение на длину ответа
                timeout=90.0  # Явный тайм-аут 90 секунд для этого запроса
            )
            
            elapsed_time = time.time() - start_time
            
            result = response.choices[0].message.content
            log_success(logger, f"API ответил за {elapsed_time:.2f}s", 
                       response_length=len(result) if result else 0,
                       model=self.model)
            logger.debug(f"   Preview: {result[:100] if result else 'EMPTY'}...")
            
            return result
            
        except httpx.TimeoutException as e:
            log_error(logger, "⏱️ Тайм-аут при обращении к API", error=e, model=self.model)
            return "Извините, API не ответил вовремя. Попробуйте позже или упростите запрос."
        except Exception as e:
            log_error(logger, "Ошибка при обращении к OpenAI API", 
                     error=e, model=self.model)
            return f"Извините, произошла ошибка. Попробуйте позже."
    
    def analyze_sme_trends(self, query: str = None) -> str:
        """
        Анализ и прогнозирование трендов МСП
        
        Args:
            query: Конкретный запрос (опционально)
        
        Returns:
            Анализ и прогноз
        """
        try:
            prompt = """
Предоставь детальный анализ и прогноз для малого и среднего предпринимательства в России на текущий период.
Включи:
1. Основные тренды в МСП
2. Перспективные отрасли
3. Государственная поддержка
4. Вызовы и риски
5. Рекомендации для предпринимателей
"""
            if query:
                prompt += f"\n\nКонкретный запрос: {query}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты - эксперт по малому и среднему бизнесу в России."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,  # Максимальная креативность
                max_tokens=4000   # Увеличено ограничение
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка анализа трендов МСП: {e}")
            return "Ошибка при формировании анализа."
    
    def analyze_feedback(self, feedback_list: List[str]) -> str:
        """
        Анализ обратной связи от пользователей
        
        Args:
            feedback_list: Список сообщений обратной связи
        
        Returns:
            Сводный анализ
        """
        try:
            feedback_text = "\n".join([f"- {fb}" for fb in feedback_list])
            
            prompt = f"""
Проанализируй следующую обратную связь от пользователей и создай сводный отчет:

{feedback_text}

Выдели:
1. Основные темы и вопросы
2. Частые жалобы или проблемы
3. Предложения по улучшению
4. Общие выводы
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты - аналитик обратной связи клиентов."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,  # Максимальная креативность
                max_tokens=4000   # Увеличено ограничение
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка анализа обратной связи: {e}")
            return "Ошибка при анализе обратной связи."
    
    def extract_user_info(self, conversation: str) -> Dict:
        """
        Извлечь информацию о пользователе из диалога
        
        Args:
            conversation: Текст диалога
        
        Returns:
            Словарь с данными пользователя
        """
        try:
            prompt = f"""
Извлеки из следующего диалога информацию о пользователе:

{conversation}

Верни JSON с полями: full_name, email, phone, organization, position.
Если какое-то поле не найдено, укажи null.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты извлекаешь структурированные данные из текста."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,  # Максимальная креативность
                max_tokens=4000,  # Увеличено ограничение
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Ошибка извлечения данных: {e}")
            return {}

    def detect_intent_and_extract(self, conversation: str) -> Dict:
        """
        Определить намерение пользователя и извлечь структурированные данные.
        Возвращает JSON вида:
        {
          "intent": "application|document|feedback|none",
          "application": {"full_name": ..., "email": ..., "phone": ..., "organization": ..., "inn": ..., "business_type": ..., "comment": ...},
          "document": {"template_type": "complaint|protocol|contract", "user_data": {...}},
          "feedback": {"message": ..., "category": ...}
        }
        Поля, не относящиеся к намерению, должны быть null/пустыми объектами.
        """
        try:
            prompt = f"""
Проанализируй диалог и определи намерение пользователя:
- Если хочет подать заявку на вступление, intent = application.
- Если просит сформировать документ (жалоба/протокол/договор), intent = document.
- Если оставляет обратную связь, intent = feedback.
- Иначе intent = none.

Диалог:
{conversation}

Верни JSON строго по схеме:
{{
  "intent": "application|document|feedback|none",
  "application": {{
    "full_name": null|string,
    "email": null|string,
    "phone": null|string,
    "organization": null|string,
    "inn": null|string,
    "business_type": null|string,
    "comment": null|string
  }},
  "document": {{
    "template_type": null|"complaint"|"protocol"|"contract",
    "user_data": null|object
  }},
  "feedback": {{
    "message": null|string,
    "category": null|string
  }}
}}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты классифицируешь намерения и извлекаешь данные, отвечаешь строго JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,  # Максимальная креативность
                max_tokens=4000,  # Увеличено ограничение
                response_format={"type": "json_object"}
            )

            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Ошибка определения намерения: {e}")
            return {"intent": "none"}
    
    def analyze_document_data_completeness(self, user_data: Dict, 
                                          required_fields: List[str],
                                          conversation_history: str = "") -> Dict:
        """
        Анализирует полноту данных для создания документа
        
        Args:
            user_data: Собранные данные пользователя
            required_fields: Обязательные поля для документа
            conversation_history: История диалога для контекста
        
        Returns:
            Анализ полноты данных с рекомендациями
        """
        try:
            prompt = f"""
Проанализируй полноту данных для создания документа.

Собранные данные:
{user_data}

Обязательные поля:
{required_fields}

Контекст беседы:
{conversation_history}

Верни JSON с анализом:
{{
  "completeness_score": 0-100,
  "filled_fields": ["список заполненных полей"],
  "missing_fields": ["список недостающих полей"],
  "confidence_score": 0-100,
  "data_quality": "excellent|good|fair|poor",
  "recommendations": ["рекомендации по улучшению"],
  "can_generate": true|false,
  "suggested_questions": ["вопросы для получения недостающих данных"]
}}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты анализируешь полноту данных для документов."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,  # Максимальная креативность
                max_tokens=4000,  # Увеличено ограничение
                response_format={"type": "json_object"}
            )

            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Ошибка анализа полноты данных: {e}")
            return {
                "completeness_score": 0,
                "filled_fields": [],
                "missing_fields": required_fields,
                "confidence_score": 0,
                "data_quality": "poor",
                "recommendations": ["Необходимо собрать все обязательные данные"],
                "can_generate": False,
                "suggested_questions": []
            }
    
    def classify_document_type(self, conversation: str, 
                              available_templates: List[Dict]) -> Dict:
        """
        Определяет подходящий тип документа на основе контекста беседы
        
        Args:
            conversation: История диалога
            available_templates: Список доступных шаблонов
        
        Returns:
            Рекомендации по выбору шаблона
        """
        try:
            templates_info = "\n".join([
                f"- {t.get('name', 'Без названия')} (ID: {t.get('template_id', 'unknown')}): {t.get('description', '')}"
                for t in available_templates
            ])
            
            prompt = f"""
Определи наиболее подходящий тип документа на основе беседы.

Диалог:
{conversation}

Доступные шаблоны:
{templates_info}

Верни JSON с рекомендациями:
{{
  "suggested_template_id": "id шаблона",
  "suggested_template_name": "название",
  "confidence": 0-100,
  "reasoning": "объяснение выбора",
  "alternative_templates": ["список альтернативных ID"],
  "document_category": "заявление|анкета|договор|жалоба|отчет|справка|протокол|другое"
}}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по выбору подходящих шаблонов документов."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,  # Максимальная креативность
                max_tokens=4000,  # Увеличено ограничение
                response_format={"type": "json_object"}
            )

            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Ошибка классификации типа документа: {e}")
            return {
                "suggested_template_id": None,
                "suggested_template_name": None,
                "confidence": 0,
                "reasoning": "Не удалось определить подходящий тип документа",
                "alternative_templates": [],
                "document_category": "другое"
            }
    
    def extract_structured_data_advanced(self, conversation: str, 
                                        template_fields: List[str]) -> Dict:
        """
        Расширенное извлечение данных с учетом специфических полей шаблона
        
        Args:
            conversation: История диалога
            template_fields: Список полей, которые нужно извлечь
        
        Returns:
            Структурированные данные с метаинформацией
        """
        try:
            fields_list = ", ".join(template_fields)
            
            prompt = f"""
Извлеки из диалога данные для следующих полей: {fields_list}

ВАЖНЫЕ ПРАВИЛА СОПОСТАВЛЕНИЯ:
- Если есть "Фамилия", "Имя", "Отчество" → объедини в "full_name" как "Фамилия Имя Отчество"
- Если есть "last_name", "first_name", "middle_name" → используй по отдельности
- "Дата рождения" → "birth_date"
- "Телефон" → "phone"
- "Email" или "Эл.почта" → "email"
- "Данные паспорта" или "Паспорт" → "passport"
- "Информация о работе" или "Работа" → "work_info"
- "Сфера деятельности" или "Сфера" → "activity_sphere"
- "Предпринимательский опыт" или "Опыт" → "business_experience"
- "Область где вы эксперт" или "Экспертиза" → "expertise_area"
- "Занимали ли вы выборную должность" → "elected_position"
- "Опыт общественной деятельности" или "Общественная деятельность" → "public_activity_experience"
- "Дополнения" → "additional_info"

Диалог:
{conversation}

Верни JSON с извлеченными данными и метаинформацией:
{{
  "extracted_data": {{
    "field_name": {{"value": "значение", "confidence": 0-100, "source": "откуда взято"}}
  }},
  "overall_confidence": 0-100,
  "ambiguous_fields": ["поля с неоднозначными значениями"],
  "inferred_fields": ["поля, значения которых были выведены логически"],
  "missing_fields": ["поля, которые не удалось извлечь"]
}}

ОБЯЗАТЕЛЬНО извлеки ВСЕ поля, которые есть в диалоге, даже если они называются по-другому!
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты извлекаешь структурированные данные с высокой точностью."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,  # Максимальная креативность
                max_tokens=4000,  # Увеличено ограничение
                response_format={"type": "json_object"}
            )

            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Ошибка расширенного извлечения данных: {e}")
            return {
                "extracted_data": {},
                "overall_confidence": 0,
                "ambiguous_fields": [],
                "inferred_fields": [],
                "missing_fields": template_fields
            }
    
    def generate_document_preview(self, template_name: str, 
                                 user_data: Dict) -> str:
        """
        Генерирует текстовый предпросмотр документа
        
        Args:
            template_name: Название шаблона
            user_data: Данные для заполнения
        
        Returns:
            Текстовое описание того, как будет выглядеть документ
        """
        try:
            prompt = f"""
Создай текстовое описание предпросмотра документа "{template_name}" с данными:

{user_data}

Опиши структуру документа и как будут заполнены поля. Выдели поля, которые остались пустыми.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты создаешь предпросмотры документов."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,  # Максимальная креативность
                max_tokens=4000   # Увеличено ограничение
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка генерации предпросмотра: {e}")
            return "Не удалось создать предпросмотр документа."


# Singleton instance
openai_service = OpenAIService()

