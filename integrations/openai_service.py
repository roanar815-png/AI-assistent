"""
Интеграция с OpenAI API для обработки естественного языка
"""
from openai import OpenAI
from typing import List, Dict
from datetime import datetime
from config import settings
from logger_config import get_logger, log_success, log_error, log_warning
import httpx
import asyncio
from functools import lru_cache
import hashlib
import time

# Инициализация логгера
logger = get_logger(__name__)


class OpenAIService:
    """Сервис для работы с OpenAI API"""
    
    def __init__(self):
        """Инициализация OpenAI/DeepSeek клиента"""
        print(f"\n[INITIALIZATION] OpenAI Service:")
        
        # Защита от ошибок при инициализации
        self.client = None
        self.async_client = None
        self.model = None
        self.response_cache = {}  # Кэш для быстрых ответов
        self.cache_ttl = 3600  # TTL кэша в секундах (1 час)
        self.connection_pool = None
        
        try:
            print(f"   [DEBUG] Начинаем инициализацию OpenAI...")
            api_key = getattr(settings, 'openai_api_key', None)
            print(f"   API Key: {'ЕСТЬ' if api_key and api_key.strip() else 'НЕТ'}")
            
            if not api_key or not api_key.strip():
                print(f"   [WARNING] OpenAI API ключ не настроен!")
                print(f"   Сервер запустится, но бот НЕ БУДЕТ отвечать.")
                return
            
            print(f"   API Key start: {api_key[:20]}... (first 20 chars)")
            
            # Создаем HTTP клиент с тайм-аутами и прокси
            proxy_config = None
            
            # Проверяем настройки прокси
            proxy_login = getattr(settings, 'proxy_login', None)
            proxy_password = getattr(settings, 'proxy_password', None)
            proxy_ip = getattr(settings, 'proxy_ip', None)
            proxy_port = getattr(settings, 'proxy_port', None)
            
            print(f"   [DEBUG] Прокси настройки:")
            print(f"   [DEBUG]   proxy_login: {proxy_login}")
            print(f"   [DEBUG]   proxy_password: {'ЕСТЬ' if proxy_password else 'НЕТ'}")
            print(f"   [DEBUG]   proxy_ip: {proxy_ip}")
            print(f"   [DEBUG]   proxy_port: {proxy_port}")
            
            # Создаем пул соединений для оптимизации
            connection_limits = httpx.Limits(
                max_keepalive_connections=20,  # Увеличено для пула
                max_connections=50,            # Увеличено для пула
                keepalive_expiry=30.0          # Время жизни соединений
            )
            
            timeout_config = httpx.Timeout(
                timeout=30.0,   # Еще больше уменьшен общий тайм-аут
                connect=3.0,    # Очень быстрое подключение
                read=30.0,      # Уменьшен тайм-аут чтения ответа
                write=3.0       # Очень быстрая запись
            )
            
            # Создаем HTTP клиент с прокси, если настроен
            if proxy_login and proxy_password and proxy_ip and proxy_port:
                proxy_url = f"http://{proxy_login}:{proxy_password}@{proxy_ip}:{proxy_port}"
                print(f"   [INFO] Используем прокси: {proxy_ip}:{proxy_port}")
                
                try:
                    # Синхронный клиент
                    http_client = httpx.Client(
                        timeout=timeout_config,
                        limits=connection_limits,
                        http2=False,  # Отключаем HTTP2 для избежания ошибок
                        proxy=proxy_url
                    )
                    
                    # Асинхронный клиент для параллельных запросов
                    self.async_client = httpx.AsyncClient(
                        timeout=timeout_config,
                        limits=connection_limits,
                        http2=False,
                        proxy=proxy_url
                    )
                    
                except Exception as e:
                    print(f"   [ERROR] Ошибка инициализации httpx.Client с прокси: {e}")
                    raise
            else:
                # Синхронный клиент
                http_client = httpx.Client(
                    timeout=timeout_config,
                    limits=connection_limits,
                    http2=False
                )
                
                # Асинхронный клиент
                self.async_client = httpx.AsyncClient(
                    timeout=timeout_config,
                    limits=connection_limits,
                    http2=False
                )
            
            print(f"   [INFO] Используем OpenAI API")
            try:
                # Создаем клиент OpenAI с настроенным HTTP клиентом
                client_kwargs = {
                    "api_key": api_key,
                    "http_client": http_client,
                    "timeout": 90.0,  # Общий тайм-аут 90 секунд
                    "max_retries": 2
                }
                
                self.client = OpenAI(**client_kwargs)
                self.model = "gpt-4o-mini"  # Быстрая модель OpenAI
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
        print(f"   self.async_client = {self.async_client is not None}", flush=True)
        print(f"   self.model = {self.model}", flush=True)
        if not self.client:
            print(f"   [WARNING] КЛИЕНТ НЕ СОЗДАН! Бот не будет отвечать!", flush=True)
        
        # Получаем текущую дату для актуальных рекомендаций
        current_date = datetime.now()
        current_year = current_date.year
        current_date_str = current_date.strftime("%d.%m.%Y")
        
        # Оптимизированный системный промпт - сокращен в 10 раз для ускорения
        self.system_prompt = f"""Ты — профессиональный AI ассистент "Опора России" для малого и среднего предпринимательства (МСП). Дата: {current_date_str} ({current_year}).

ОСНОВНЫЕ НАПРАВЛЕНИЯ РАБОТЫ:

ДОКУМЕНТООБОРОТ И ЗАЯВКИ:
• Помощь в заполнении заявлений, анкет и документов
• Консультации по правильному оформлению документов
• Автозаполнение шаблонов на основе предоставленных данных
• Проверка полноты и корректности документов

ПРАВОВЫЕ КОНСУЛЬТАЦИИ:
• Разъяснение законодательства для МСП
• Информация о льготах, субсидиях и поддержке
• Консультации по регистрации и ведению бизнеса
• Помощь в понимании налогового законодательства

АНАЛИЗ БИЗНЕС-ПРОЦЕССОВ:
• Анализ бизнес-процессов и их оптимизация
• Консультации по развитию бизнеса
• Помощь в планировании и стратегии
• Анализ рынка и конкурентов

ПОДДЕРЖКА МСП:
• Информация о программах поддержки малого бизнеса
• Консультации по получению финансирования
• Помощь в поиске партнеров и клиентов
• Информация о выставках и мероприятиях

КОНТАКТЫ И РЕГИОНАЛЬНАЯ ПОДДЕРЖКА:
• Предоставление контактов региональных отделений
• Информация о местных программах поддержки
• Помощь в поиске ближайших офисов "Опора России"

ТЕХНИЧЕСКАЯ ПОДДЕРЖКА:
• Помощь в работе с цифровыми сервисами
• Консультации по автоматизации бизнес-процессов
• Информация о цифровых инструментах для МСП

АНАЛИТИКА И ПРОГНОЗЫ:
• Анализ трендов в сфере МСП
• Прогнозирование развития рынка
• Статистика и аналитические данные
• Рекомендации по развитию бизнеса

СТИЛЬ ОБЩЕНИЯ:
• Дружелюбный и профессиональный тон
• Подробные и структурированные ответы
• Использование конкретных примеров и рекомендаций
• Адаптация сложной информации под уровень пользователя
• Активное предложение дополнительной помощи

ВАЖНЫЕ ПРИНЦИПЫ:
• Для простых приветствий отвечай дружелюбно, НЕ предлагай создание документов
• При запросах на документы - предлагай выбор шаблона, НЕ создавай автоматически
• Давай развернутые ответы с практическими советами
• Всегда предлагай дополнительные варианты помощи
• Используй структурированную подачу информации
• Приводи примеры и конкретные шаги действий

ПРИМЕРЫ ХОРОШИХ ОТВЕТОВ:
- При вопросе о регистрации ИП: подробно объясни этапы, документы, сроки, стоимость
- При запросе о льготах: перечисли все доступные льготы с условиями получения
- При вопросе о финансировании: опиши все программы поддержки с требованиями
- При запросе о документах: предложи подходящие шаблоны с объяснением их назначения

Помни: твоя цель - максимально помочь предпринимателю в развитии его бизнеса!"""
    
    def _get_cache_key(self, message: str, conversation_history: List[Dict] = None) -> str:
        """Генерирует ключ кэша для сообщения"""
        # Создаем хэш из сообщения и последних 3 сообщений истории
        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-3:]  # Только последние 3 сообщения
            history_text = " ".join([msg.get("content", "") for msg in recent_history])
        
        cache_input = f"{message.lower().strip()}:{history_text}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: dict) -> bool:
        """Проверяет валидность кэша"""
        if not cache_entry:
            return False
        return time.time() - cache_entry.get("timestamp", 0) < self.cache_ttl
    
    def _get_cached_response(self, cache_key: str) -> str:
        """Получает кэшированный ответ"""
        cache_entry = self.response_cache.get(cache_key)
        if cache_entry and self._is_cache_valid(cache_entry):
            logger.info(f"🚀 Кэш HIT для ключа: {cache_key[:8]}...")
            return cache_entry["response"]
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Сохраняет ответ в кэш"""
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        logger.debug(f"💾 Кэш SAVE для ключа: {cache_key[:8]}...")
    
    def _cleanup_cache(self):
        """Очищает устаревшие записи кэша"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.response_cache.items()
            if current_time - entry.get("timestamp", 0) > self.cache_ttl
        ]
        for key in expired_keys:
            del self.response_cache[key]
        if expired_keys:
            logger.debug(f"🧹 Очищено {len(expired_keys)} устаревших записей кэша")
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        Отправить сообщение в чат и получить ответ (синхронная версия)
        
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
        
        # Проверяем кэш
        cache_key = self._get_cache_key(message, conversation_history)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Очищаем устаревший кэш
        self._cleanup_cache()
        
        try:
            history_len = len(conversation_history) if conversation_history else 0
            logger.info(f"   Message length: {len(message)} chars")
            logger.info(f"   History: {history_len} messages")
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if conversation_history:
                # Ограничиваем историю для ускорения - только последние 3 сообщения
                recent_history = conversation_history[-3:]  # Только последние 3 сообщения
                messages.extend(recent_history)
            
            messages.append({"role": "user", "content": message})
            
            logger.info(f"   📤 Отправка {len(messages)} сообщений к API...")
            logger.debug(f"   Параметры: temperature=0.7, max_tokens=2000")
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,  # Оптимизированная креативность
                max_tokens=4000,  # Значительно увеличено для полных ответов
                timeout=60.0      # Увеличен тайм-аут для длинных ответов
            )
            
            elapsed_time = time.time() - start_time
            
            result = response.choices[0].message.content
            log_success(logger, f"API ответил за {elapsed_time:.2f}s", 
                       response_length=len(result) if result else 0,
                       model=self.model)
            logger.debug(f"   Preview: {result[:100] if result else 'EMPTY'}...")
            
            # Кэшируем ответ для простых вопросов
            if len(message) < 100 and len(result) < 500:
                self._cache_response(cache_key, result)
            
            return result
            
        except httpx.TimeoutException as e:
            log_error(logger, "⏱️ Тайм-аут при обращении к API", error=e, model=self.model)
            return "Извините, API не ответил вовремя. Попробуйте позже или упростите запрос."
        except Exception as e:
            log_error(logger, "Ошибка при обращении к OpenAI API", 
                     error=e, model=self.model)
            return f"Извините, произошла ошибка. Попробуйте позже."
    
    async def chat_async(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        Асинхронная версия отправки сообщения в чат
        
        Args:
            message: Сообщение пользователя
            conversation_history: История диалога
        
        Returns:
            Ответ ассистента
        """
        logger.info("🤖 Асинхронный вызов OpenAI/DeepSeek API для чата")
        logger.debug(f"   Model: {self.model}")
        logger.debug(f"   Async Client configured: {'YES' if self.async_client else 'NO'}")
        
        # Проверка что асинхронный клиент настроен
        if not self.async_client:
            log_error(logger, "OpenAI асинхронный клиент не настроен! API недоступен")
            return "Извините, OpenAI/DeepSeek API не настроен. Проверьте конфигурацию сервера."
        
        # Проверяем кэш
        cache_key = self._get_cache_key(message, conversation_history)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Очищаем устаревший кэш
        self._cleanup_cache()
        
        try:
            history_len = len(conversation_history) if conversation_history else 0
            logger.info(f"   Message length: {len(message)} chars")
            logger.info(f"   History: {history_len} messages")
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if conversation_history:
                # Ограничиваем историю для ускорения - только последние 3 сообщения
                recent_history = conversation_history[-3:]  # Только последние 3 сообщения
                messages.extend(recent_history)
            
            messages.append({"role": "user", "content": message})
            
            logger.info(f"   📤 Асинхронная отправка {len(messages)} сообщений к API...")
            logger.debug(f"   Параметры: temperature=0.7, max_tokens=2000")
            
            start_time = time.time()
            
            # Используем асинхронный клиент
            response = await self.async_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.5,
                    "max_tokens": 600
                }
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                result = result_data["choices"][0]["message"]["content"]
                
                log_success(logger, f"Асинхронный API ответил за {elapsed_time:.2f}s", 
                           response_length=len(result) if result else 0,
                           model=self.model)
                logger.debug(f"   Preview: {result[:100] if result else 'EMPTY'}...")
                
                # Кэшируем ответ для простых вопросов
                if len(message) < 100 and len(result) < 500:
                    self._cache_response(cache_key, result)
                
                return result
            else:
                log_error(logger, f"Ошибка API: {response.status_code}", 
                         response_text=response.text)
                return "Извините, произошла ошибка при обращении к API."
            
        except httpx.TimeoutException as e:
            log_error(logger, "⏱️ Тайм-аут при асинхронном обращении к API", error=e, model=self.model)
            return "Извините, API не ответил вовремя. Попробуйте позже или упростите запрос."
        except Exception as e:
            log_error(logger, "Ошибка при асинхронном обращении к OpenAI API", 
                     error=e, model=self.model)
            return f"Извините, произошла ошибка. Попробуйте позже."
    
    async def process_multiple_requests(self, requests: List[Dict]) -> List[str]:
        """
        Параллельная обработка нескольких запросов
        
        Args:
            requests: Список запросов [{"message": str, "history": List[Dict]}, ...]
        
        Returns:
            Список ответов
        """
        logger.info(f"🚀 Параллельная обработка {len(requests)} запросов")
        
        if not self.async_client:
            log_error(logger, "Асинхронный клиент не настроен!")
            return ["Ошибка: асинхронный клиент не настроен"] * len(requests)
        
        # Создаем задачи для параллельного выполнения
        tasks = []
        for request in requests:
            message = request.get("message", "")
            history = request.get("history", [])
            task = self.chat_async(message, history)
            tasks.append(task)
        
        try:
            # Выполняем все задачи параллельно
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed_time = time.time() - start_time
            
            # Обрабатываем результаты
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    log_error(logger, f"Ошибка в запросе {i+1}", error=result)
                    processed_results.append(f"Ошибка при обработке запроса: {str(result)}")
                else:
                    processed_results.append(result)
            
            log_success(logger, f"Параллельная обработка завершена за {elapsed_time:.2f}s", 
                       requests_count=len(requests),
                       avg_time_per_request=f"{elapsed_time/len(requests):.2f}s")
            
            return processed_results
            
        except Exception as e:
            log_error(logger, "Ошибка при параллельной обработке", error=e)
            return [f"Ошибка параллельной обработки: {str(e)}"] * len(requests)
    
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
Предоставь ДЕТАЛЬНЫЙ и СТРУКТУРИРОВАННЫЙ анализ и прогноз для малого и среднего предпринимательства в России на текущий период.

СТРУКТУРА ОТВЕТА:
1. ОСНОВНЫЕ ТРЕНДЫ В МСП
   - Опиши 3-5 ключевых трендов с конкретными примерами
   - Укажи статистику и цифры где возможно
   - Объясни причины возникновения этих трендов

2. ПЕРСПЕКТИВНЫЕ ОТРАСЛИ
   - Перечисли 5-7 наиболее перспективных направлений
   - Объясни почему именно эти отрасли развиваются
   - Приведи данные о росте и потенциале этих отраслей

3. ГОСУДАРСТВЕННАЯ ПОДДЕРЖКА
   - Перечисли все доступные программы поддержки
   - Укажи условия получения и размеры поддержки
   - Опиши механизмы работы программ поддержки

4. ВЫЗОВЫ И РИСКИ
   - Опиши основные проблемы МСП
   - Объясни причины возникновения этих проблем
   - Приведи статистику по основным вызовам

5. АНАЛИТИЧЕСКАЯ ИНФОРМАЦИЯ
   - Ключевые показатели развития МСП
   - Сравнительный анализ с предыдущими периодами
   - Региональные особенности развития

Используй структурированную подачу информации, приводи конкретные примеры и цифры! Фокусируйся на предоставлении подробной информации, а не на советах.
"""
            if query:
                prompt += f"\n\nКонкретный запрос: {query}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты - эксперт по малому и среднему бизнесу в России. Давай подробные и структурированные ответы с аналитической информацией, статистикой и фактами. Фокусируйся на предоставлении информации, а не на советах."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Низкая креативность для аналитических ответов
                max_tokens=4000   # Значительно увеличено для полных анализов
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка анализа трендов МСП: {e}")
            return "Ошибка при формировании анализа."
    
    def market_forecast(self, query: str = None) -> str:
        """
        Прогнозирование рынка для МСП
        
        Args:
            query: Конкретный запрос (опционально)
        
        Returns:
            Прогноз рынка
        """
        try:
            prompt = """
Предоставь ДЕТАЛЬНЫЙ и СТРУКТУРИРОВАННЫЙ прогноз рынка для малого и среднего предпринимательства в России.

СТРУКТУРА ОТВЕТА:
1. ТЕКУЩЕЕ СОСТОЯНИЕ РЫНКА
   - Основные показатели рынка МСП
   - Ключевые игроки и их доля
   - Региональное распределение

2. ФАКТОРЫ ВЛИЯНИЯ НА РЫНОК
   - Экономические факторы
   - Политические и регуляторные изменения
   - Технологические тренды
   - Социальные и демографические факторы

3. ПРОГНОЗ РАЗВИТИЯ
   - Краткосрочный прогноз (6-12 месяцев)
   - Среднесрочный прогноз (1-3 года)
   - Долгосрочный прогноз (3-5 лет)

4. СЕГМЕНТАЦИЯ РЫНКА
   - Анализ по отраслям
   - Анализ по размерам предприятий
   - Анализ по регионам

5. КЛЮЧЕВЫЕ МЕТРИКИ И ПОКАЗАТЕЛИ
   - Ожидаемые темпы роста
   - Объемы рынка
   - Количество предприятий
   - Занятость в секторе

Используй структурированную подачу информации, приводи конкретные данные и статистику! Фокусируйся на предоставлении подробной аналитической информации.
"""
            if query:
                prompt += f"\n\nКонкретный запрос: {query}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты - эксперт по рыночному анализу и прогнозированию в сфере МСП России. Давай подробные и структурированные прогнозы с аналитической информацией, статистикой и фактами. Фокусируйся на предоставлении информации, а не на советах."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Низкая креативность для аналитических ответов
                max_tokens=4000   # Значительно увеличено для полных прогнозов
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка прогнозирования рынка: {e}")
            return "Ошибка при формировании прогноза рынка."
    
    def business_insights(self, query: str = None) -> str:
        """
        Бизнес-инсайты для МСП
        
        Args:
            query: Конкретный запрос (опционально)
        
        Returns:
            Бизнес-инсайты
        """
        try:
            prompt = """
Предоставь ДЕТАЛЬНЫЙ и СТРУКТУРИРОВАННЫЙ анализ бизнес-инсайтов для малого и среднего предпринимательства в России.

СТРУКТУРА ОТВЕТА:
1. КЛЮЧЕВЫЕ ИНСАЙТЫ ОТРАСЛИ
   - Важные открытия и тенденции
   - Изменения в поведении потребителей
   - Новые возможности на рынке

2. ТЕХНОЛОГИЧЕСКИЕ ИННОВАЦИИ
   - Внедрение новых технологий в МСП
   - Цифровизация бизнес-процессов
   - Влияние технологий на конкурентоспособность

3. ИЗМЕНЕНИЯ В ПОТРЕБИТЕЛЬСКОМ ПОВЕДЕНИИ
   - Новые предпочтения клиентов
   - Изменения в способах покупки
   - Влияние социальных факторов

4. КОНКУРЕНТНАЯ СРЕДА
   - Анализ конкурентной ситуации
   - Новые игроки на рынке
   - Изменения в стратегиях конкурентов

5. РЕГУЛЯТИВНЫЕ ИЗМЕНЕНИЯ
   - Новые законы и постановления
   - Изменения в налогообложении
   - Влияние регуляторных изменений на бизнес

6. ЭКОНОМИЧЕСКИЕ ИНДИКАТОРЫ
   - Ключевые экономические показатели
   - Влияние макроэкономических факторов
   - Прогнозы экономического развития

Используй структурированную подачу информации, приводи конкретные примеры и данные! Фокусируйся на предоставлении подробной аналитической информации.
"""
            if query:
                prompt += f"\n\nКонкретный запрос: {query}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты - эксперт по бизнес-аналитике и инсайтам в сфере МСП России. Давай подробные и структурированные анализы с информацией, статистикой и фактами. Фокусируйся на предоставлении информации, а не на советах."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Низкая креативность для аналитических ответов
                max_tokens=4000   # Значительно увеличено для полных инсайтов
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка формирования бизнес-инсайтов: {e}")
            return "Ошибка при формировании бизнес-инсайтов."
    
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
                temperature=0.3,  # Низкая креативность для быстрых ответов
                max_tokens=500    # Уменьшено для ускорения
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
                temperature=0.3,  # Низкая креативность для быстрых ответов
                max_tokens=1000   # Уменьшено для ускорения
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка генерации предпросмотра: {e}")
            return "Не удалось создать предпросмотр документа."
    
    def chat_with_extraction(self, message: str, conversation_history: List[Dict] = None) -> tuple:
        """
        ОБЪЕДИНЕННЫЙ МЕТОД: чат + извлечение данных + определение намерения
        Это заменяет множественные API вызовы одним оптимизированным запросом
        
        Args:
            message: Сообщение пользователя
            conversation_history: История диалога
        
        Returns:
            tuple: (response_text, user_data, intent_data)
        """
        logger.info("🤖 Объединенный запрос: чат + извлечение данных + намерение")
        
        # Проверка что клиент настроен
        if not self.client:
            log_error(logger, "OpenAI клиент не настроен! API недоступен")
            return "Извините, OpenAI/DeepSeek API не настроен. Проверьте конфигурацию сервера.", {}, {}
        
        try:
            # Создаем объединенный промпт для всех задач
            conversation_text = ""
            if conversation_history:
                recent_history = conversation_history[-3:]  # Только последние 3 сообщения
                conversation_text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in recent_history])
            
            combined_prompt = f"""
Обработай сообщение пользователя и выполни следующие задачи:

1. ОТВЕТЬ на вопрос пользователя ПОДРОБНО и ПОЛЕЗНО
2. ИЗВЛЕКИ данные пользователя ТОЛЬКО если они явно указаны
3. ОПРЕДЕЛИ намерение пользователя

ПРИНЦИПЫ ОТВЕТА:
- Давай РАЗВЕРНУТЫЕ ответы с практическими советами
- Используй структурированную подачу информации (списки, разделы)
- Приводи конкретные примеры и пошаговые инструкции
- Предлагай дополнительные варианты помощи
- Используй структурированную подачу информации
- Адаптируй сложную информацию под уровень пользователя

ВАЖНЫЕ ОГРАНИЧЕНИЯ: 
- Если пользователь просто представился (например, "Меня зовут Лев"), отвечай дружелюбно как обычный чат
- НЕ предлагай создание документов без явного запроса
- НЕ извлекай данные из простых приветствий и представлений
- Для простых приветствий используй intent = "chat"

ТИПЫ ЗАПРОСОВ И ПОДХОДЫ:
- Вопросы о регистрации бизнеса: подробно объясни этапы, документы, сроки, стоимость
- Запросы о льготах и поддержке: перечисли все доступные программы с условиями
- Вопросы о финансировании: опиши все программы поддержки с требованиями
- Запросы о документах: предложи подходящие шаблоны с объяснением назначения
- Правовые вопросы: дай развернутое объяснение с примерами
- Бизнес-консультации: предложи конкретные шаги и рекомендации

Сообщение: {message}

Контекст беседы:
{conversation_text}

Верни ответ в формате JSON:
{{
  "response": "твой ПОДРОБНЫЙ и ПОЛЕЗНЫЙ ответ пользователю с практическими советами. ОБЯЗАТЕЛЬНО давай ПОЛНЫЙ ответ без сокращений и обрезания текста!",
  "user_data": {{
    "full_name": "имя ТОЛЬКО если явно указано",
    "email": "email ТОЛЬКО если явно указан", 
    "phone": "телефон ТОЛЬКО если явно указан",
    "organization": "организация ТОЛЬКО если явно указана",
    "position": "должность ТОЛЬКО если явно указана"
  }},
  "intent": {{
    "type": "application|document|feedback|chat",
    "confidence": 0-100,
    "details": "дополнительные детали намерения"
  }}
}}

Помни: твоя цель - максимально помочь предпринимателю! Давай развернутые, структурированные ответы с практической пользой! ВАЖНО: всегда давай ПОЛНЫЕ ответы без сокращений и обрезания текста!
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты — профессиональный AI ассистент 'Опора России' для МСП. Давай ПОДРОБНЫЕ и ПОЛЕЗНЫЕ ответы с практическими советами. Помогай с документами, законодательством, бизнес-вопросами, регистрацией, льготами и поддержкой. Используй структурированную подачу информации и конкретные примеры. НЕ предлагай создание документов без явного запроса пользователя. Всегда давай ПОЛНЫЕ ответы без сокращений!"},
                    {"role": "user", "content": combined_prompt}
                ],
                temperature=0.5,  # Оптимизированная креативность
                max_tokens=4000,  # Значительно увеличено для полных ответов
                timeout=60.0      # Увеличен таймаут для длинных ответов
            )
            
            result = response.choices[0].message.content
            
            # Парсим JSON ответ
            try:
                import json
                parsed_result = json.loads(result)
                response_text = parsed_result.get("response", result)
                user_data = parsed_result.get("user_data", {})
                intent_data = parsed_result.get("intent", {})
            except:
                # Если не удалось распарсить JSON, возвращаем как есть
                response_text = result
                user_data = {}
                intent_data = {}
            
            log_success(logger, f"Объединенный запрос выполнен", 
                       response_length=len(response_text),
                       user_data_fields=len(user_data),
                       intent_type=intent_data.get("type", "unknown"))
            
            return response_text, user_data, intent_data
            
        except Exception as e:
            log_error(logger, "Ошибка объединенного запроса", error=e)
            return f"Извините, произошла ошибка при обработке запроса: {str(e)}", {}, {}


# Singleton instance
openai_service = OpenAIService()

