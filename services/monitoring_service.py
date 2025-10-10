"""
Сервис мониторинга законодательства МСП
"""
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from config import settings
from integrations import google_sheets_service


class MonitoringService:
    """Сервис для мониторинга изменений в законодательстве"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.urls = settings.legislation_urls.split(',')
    
    async def check_legislation_updates(self) -> List[Dict]:
        """
        Проверить обновления законодательства
        
        Returns:
            Список найденных обновлений
        """
        updates = []
        
        for url in self.urls:
            url = url.strip()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            html = await response.text()
                            parsed_updates = self._parse_legislation_page(html, url)
                            updates.extend(parsed_updates)
            except Exception as e:
                print(f"Ошибка при проверке {url}: {e}")
        
        # Сохранить в Google Sheets
        for update in updates:
            google_sheets_service.save_legislation_update(
                title=update['title'],
                url=update['url'],
                date=update['date']
            )
        
        return updates
    
    def _parse_legislation_page(self, html: str, source_url: str) -> List[Dict]:
        """
        Парсинг страницы с законодательством
        
        Args:
            html: HTML код страницы
            source_url: URL источника
        
        Returns:
            Список найденных документов
        """
        updates = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Простой пример парсинга (нужно адаптировать под конкретные сайты)
        # Ищем заголовки и ссылки
        for item in soup.find_all(['h2', 'h3', 'a'], limit=10):
            if item.name == 'a' and item.get('href'):
                title = item.get_text(strip=True)
                if len(title) > 20:  # Фильтр по длине заголовка
                    updates.append({
                        'title': title,
                        'url': item.get('href') if item.get('href').startswith('http') 
                               else f"{source_url}{item.get('href')}",
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'source': source_url
                    })
        
        return updates[:5]  # Ограничиваем количество
    
    def get_legislation_summary(self, days: int = 7) -> str:
        """
        Получить сводку по законодательству за последние дни
        
        Args:
            days: Количество дней для анализа
        
        Returns:
            Текстовая сводка
        """
        # Можно получить данные из Google Sheets и сформировать сводку
        summary = f"""
📋 Сводка по изменениям законодательства МСП за последние {days} дней:

За указанный период проводится мониторинг официальных источников.
Обновления автоматически сохраняются в базе данных.

Для получения подробной информации используйте команду /legislation
"""
        return summary


monitoring_service = MonitoringService()

