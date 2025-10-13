"""
Скрипт для тестирования заполнения всех таблиц
"""
import asyncio
import uuid
from datetime import datetime
from models.schemas import (
    ComplaintData, LegislationData, EventData, ChatAnalyticsData
)
from integrations import google_sheets_service
from services.analytics_service import analytics_service

async def test_complaints_table():
    """Тестирование таблицы жалоб"""
    print("Тестирование таблицы жалоб...")
    
    complaint = ComplaintData(
        complaint_id=str(uuid.uuid4()),
        user_id="test_user_001",
        full_name="Иванов Иван Иванович",
        email="ivanov@example.com",
        phone="+7 (999) 123-45-67",
        organization="ООО Тест",
        complaint_text="Некачественное обслуживание в отделении банка",
        category="Банковские услуги",
        priority="Высокий"
    )
    
    success = google_sheets_service.save_complaint(complaint.model_dump())
    print(f"   Результат: {'Успешно' if success else 'Ошибка'}")
    
    # Получаем список жалоб
    complaints = google_sheets_service.get_complaints()
    print(f"   Всего жалоб в таблице: {len(complaints)}")
    
    return success

async def test_legislation_table():
    """Тестирование таблицы законодательства"""
    print("Тестирование таблицы законодательства...")
    
    legislation = LegislationData(
        title="Федеральный закон о поддержке малого и среднего предпринимательства",
        url="https://example.com/law/123",
        publication_date="2024-01-15",
        description="Закон регулирует вопросы поддержки МСП",
        category="Поддержка МСП",
        importance="Высокая"
    )
    
    success = google_sheets_service.save_legislation(legislation.model_dump())
    print(f"   Результат: {'Успешно' if success else 'Ошибка'}")
    
    # Получаем список законодательства
    legislation_list = google_sheets_service.get_legislation()
    print(f"   Всего записей в таблице: {len(legislation_list)}")
    
    return success

async def test_events_table():
    """Тестирование таблицы мероприятий"""
    print("Тестирование таблицы мероприятий...")
    
    event = EventData(
        event_id=str(uuid.uuid4()),
        title="Семинар по налогообложению МСП",
        date="2024-02-15",
        time="14:00",
        description="Обучение основам налогообложения для малого бизнеса",
        location="Конференц-зал Центра поддержки МСП",
        participants=["Иванов И.И.", "Петров П.П.", "Сидоров С.С."],
        organizer="Центр поддержки МСП",
        status="Запланировано"
    )
    
    success = google_sheets_service.save_event(event.model_dump())
    print(f"   Результат: {'Успешно' if success else 'Ошибка'}")
    
    # Получаем список мероприятий
    events = google_sheets_service.get_events()
    print(f"   Всего мероприятий в таблице: {len(events)}")
    
    return success

async def test_chat_analytics():
    """Тестирование таблицы аналитики чата"""
    print("Тестирование таблицы аналитики чата...")
    
    # Создаем тестовую сессию
    session_id = analytics_service.start_session("test_user_001")
    print(f"   Создана сессия: {session_id}")
    
    # Добавляем несколько сообщений
    analytics_service.add_message(
        session_id, 
        "Как зарегистрировать ООО?", 
        "Для регистрации ООО необходимо...", 
        2.5, 
        ["регистрация", "ооо"]
    )
    
    analytics_service.add_message(
        session_id, 
        "Какие документы нужны?", 
        "Вам понадобятся следующие документы...", 
        1.8, 
        ["документы"]
    )
    
    analytics_service.mark_document_created(session_id)
    
    # Завершаем сессию
    analytics_data = analytics_service.end_session(session_id, satisfaction_score=4.5)
    print(f"   Аналитика сессии: {analytics_data}")
    
    # Сохраняем в Google Sheets
    success = google_sheets_service.save_chat_analytics(analytics_data)
    print(f"   Результат: {'Успешно' if success else 'Ошибка'}")
    
    # Получаем список аналитики
    analytics_list = google_sheets_service.get_chat_analytics()
    print(f"   Всего сессий в таблице: {len(analytics_list)}")
    
    return success

async def test_statistics():
    """Тестирование статистики"""
    print("Тестирование статистики...")
    
    try:
        from services.report_service import report_service
        
        stats = report_service.generate_statistics_report()
        print(f"   Общая статистика:")
        print(f"     - Пользователей: {stats.get('total_users', 0)}")
        print(f"     - Жалоб: {stats.get('total_complaints', 0)}")
        print(f"     - Мероприятий: {stats.get('total_events', 0)}")
        print(f"     - Записей законодательства: {stats.get('total_legislation', 0)}")
        print(f"     - Сессий чата: {stats.get('total_chat_sessions', 0)}")
        
        return True
    except Exception as e:
        print(f"   Ошибка получения статистики: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("Запуск тестирования заполнения таблиц")
    print("=" * 60)
    
    # Проверяем статус Google Sheets
    status = google_sheets_service.get_status()
    print(f"Статус Google Sheets:")
    print(f"   - Подключен: {'Да' if status.get('has_client') else 'Нет'}")
    print(f"   - Таблица доступна: {'Да' if status.get('has_spreadsheet') else 'Нет'}")
    if status.get('last_error'):
        print(f"   - Ошибка: {status['last_error']}")
    print()
    
    if not status.get('has_client') or not status.get('has_spreadsheet'):
        print("Google Sheets не настроен. Пропускаем тестирование.")
        return
    
    # Тестируем все таблицы
    results = []
    
    results.append(await test_complaints_table())
    print()
    
    results.append(await test_legislation_table())
    print()
    
    results.append(await test_events_table())
    print()
    
    results.append(await test_chat_analytics())
    print()
    
    results.append(await test_statistics())
    print()
    
    # Итоги
    print("=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    success_count = sum(results)
    total_count = len(results)
    
    print(f"   Успешно: {success_count}/{total_count}")
    print(f"   Статус: {'Все тесты пройдены' if success_count == total_count else 'Есть ошибки'}")
    
    if success_count == total_count:
        print("\nВсе таблицы успешно заполняются!")
        print("   - Complaints (жалобы)")
        print("   - Legislation (законодательство)")
        print("   - Events (мероприятия)")
        print("   - ChatAnalytics (аналитика чата)")
    else:
        print(f"\n{total_count - success_count} тестов завершились с ошибками")

if __name__ == "__main__":
    asyncio.run(main())
