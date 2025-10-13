"""
Сервис для дополнительных оптимизаций производительности
"""
import asyncio
import time
import gc
from typing import Dict, List, Optional
from functools import lru_cache
from logger_config import get_logger, log_success, log_error, log_warning

logger = get_logger(__name__)


class PerformanceOptimizer:
    """Класс для дополнительных оптимизаций производительности"""
    
    def __init__(self):
        self.request_queue = asyncio.Queue(maxsize=100)
        self.batch_size = 5
        self.batch_timeout = 0.5  # 500ms
        self.processing_tasks = set()
        self.is_running = False
    
    async def start_batch_processor(self):
        """Запуск процессора пакетных запросов"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🚀 Запуск процессора пакетных запросов")
        
        # Создаем задачу для обработки пакетов
        task = asyncio.create_task(self._process_batches())
        self.processing_tasks.add(task)
        task.add_done_callback(self.processing_tasks.discard)
    
    async def stop_batch_processor(self):
        """Остановка процессора пакетных запросов"""
        self.is_running = False
        logger.info("🛑 Остановка процессора пакетных запросов")
        
        # Ждем завершения всех задач
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
    
    async def _process_batches(self):
        """Обработка пакетов запросов"""
        batch = []
        last_batch_time = time.time()
        
        while self.is_running:
            try:
                # Пытаемся получить запрос с таймаутом
                try:
                    request = await asyncio.wait_for(
                        self.request_queue.get(), 
                        timeout=self.batch_timeout
                    )
                    batch.append(request)
                except asyncio.TimeoutError:
                    # Таймаут - обрабатываем накопленный пакет
                    pass
                
                current_time = time.time()
                
                # Обрабатываем пакет если:
                # 1. Пакет заполнен
                # 2. Прошло достаточно времени
                # 3. Есть запросы в пакете
                if (len(batch) >= self.batch_size or 
                    (current_time - last_batch_time >= self.batch_timeout and batch)):
                    
                    if batch:
                        await self._process_batch(batch)
                        batch = []
                        last_batch_time = current_time
                
            except Exception as e:
                log_error(logger, "Ошибка в процессоре пакетов", error=e)
                await asyncio.sleep(0.1)
    
    async def _process_batch(self, batch: List[Dict]):
        """Обработка одного пакета запросов"""
        logger.info(f"📦 Обработка пакета из {len(batch)} запросов")
        
        try:
            # Здесь можно добавить логику пакетной обработки
            # Например, группировка похожих запросов
            for request in batch:
                # Обрабатываем каждый запрос
                await self._handle_request(request)
            
            log_success(logger, f"Пакет из {len(batch)} запросов обработан")
            
        except Exception as e:
            log_error(logger, "Ошибка обработки пакета", error=e)
    
    async def _handle_request(self, request: Dict):
        """Обработка отдельного запроса"""
        # Здесь можно добавить специфичную логику
        pass
    
    async def queue_request(self, request: Dict):
        """Добавление запроса в очередь"""
        try:
            await self.request_queue.put(request)
        except asyncio.QueueFull:
            log_warning(logger, "Очередь запросов переполнена")
    
    @lru_cache(maxsize=1000)
    def cached_response(self, message_hash: str) -> Optional[str]:
        """Кэшированный ответ с LRU кэшем"""
        # Этот метод будет переопределен в зависимости от логики
        return None
    
    def clear_cache(self):
        """Очистка кэша"""
        self.cached_response.cache_clear()
        logger.info("🧹 Кэш очищен")
    
    def optimize_memory(self):
        """Оптимизация использования памяти"""
        # Принудительная сборка мусора
        collected = gc.collect()
        logger.debug(f"🧹 Сборка мусора: освобождено {collected} объектов")
        
        # Дополнительные оптимизации памяти
        if hasattr(gc, 'set_threshold'):
            # Настройка порогов сборки мусора
            gc.set_threshold(700, 10, 10)
    
    def get_system_metrics(self) -> Dict:
        """Получение системных метрик"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "open_files": len(process.open_files()),
            "threads": process.num_threads(),
            "queue_size": self.request_queue.qsize(),
            "active_tasks": len(self.processing_tasks)
        }


# Глобальный экземпляр оптимизатора
performance_optimizer = PerformanceOptimizer()
