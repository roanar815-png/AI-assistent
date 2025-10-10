"""
Скрипт для проверки корректности настроек
"""
from config import settings
from integrations import google_sheets_service, openai_service


def test_configuration():
    """Проверка конфигурации"""
    print("=" * 60)
    print("ПРОВЕРКА КОНФИГУРАЦИИ")
    print("=" * 60)
    
    print("\n✓ Конфигурация загружена")
    print(f"  - OpenAI API ключ: {'✓' if settings.openai_api_key else '✗ НЕ УКАЗАН'}")
    if settings.openai_api_key:
        print(f"    {settings.openai_api_key[:15]}...")
    
    print(f"  - Google Sheet ID: {'✓' if settings.google_sheet_id else '✗ НЕ УКАЗАН'}")
    if settings.google_sheet_id:
        print(f"    {settings.google_sheet_id}")
    
    print(f"  - Credentials файл: {settings.google_credentials_file}")
    print(f"  - Host: {settings.host}:{settings.port}")


def test_google_sheets():
    """Проверка Google Sheets"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА GOOGLE SHEETS")
    print("=" * 60)
    
    try:
        # Попытка получить пользователей
        users = google_sheets_service.get_all_users()
        print(f"\n✓ Google Sheets подключен успешно!")
        print(f"  - Найдено пользователей: {len(users)}")
        
        # Попытка записи тестовых данных
        test_data = {
            "user_id": "test_user",
            "full_name": "Тестовый Пользователь",
            "email": "test@example.com",
            "phone": "+7 999 123-45-67",
            "organization": "Тестовая Организация",
            "position": "Директор"
        }
        
        success = google_sheets_service.save_user_data(test_data)
        if success:
            print("✓ Запись данных работает")
        else:
            print("✗ Ошибка записи данных")
        
        return True
    except Exception as e:
        print(f"\n✗ Ошибка Google Sheets:")
        print(f"  {str(e)}")
        print("\nВозможные причины:")
        print("  1. Проверьте наличие файла credentials.json")
        print("  2. Убедитесь, что Service Account имеет доступ к таблице")
        print("  3. Проверьте правильность GOOGLE_SHEET_ID в .env")
        return False


def test_openai():
    """Проверка OpenAI"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА OPENAI API")
    print("=" * 60)
    
    try:
        response = openai_service.chat("Привет! Ответь кратко.")
        print(f"\n✓ OpenAI API работает!")
        print(f"  - Ответ: {response[:100]}...")
        return True
    except Exception as e:
        print(f"\n✗ Ошибка OpenAI API:")
        print(f"  {str(e)}")
        print("\nВозможные причины:")
        print("  1. Проверьте правильность API ключа")
        print("  2. Убедитесь, что на аккаунте есть баланс")
        print("  3. Проверьте подключение к интернету")
        return False


def main():
    """Главная функция проверки"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "ПРОВЕРКА НАСТРОЕК ПРИЛОЖЕНИЯ" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    
    test_configuration()
    
    sheets_ok = test_google_sheets()
    openai_ok = test_openai()
    
    print("\n" + "=" * 60)
    print("ИТОГИ ПРОВЕРКИ")
    print("=" * 60)
    
    if sheets_ok and openai_ok:
        print("\n✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("\nВы можете запустить приложение:")
        print("  python main.py")
    else:
        print("\n✗ ОБНАРУЖЕНЫ ОШИБКИ!")
        print("\nИсправьте ошибки перед запуском приложения.")
        if not sheets_ok:
            print("  - Настройте Google Sheets API")
        if not openai_ok:
            print("  - Настройте OpenAI API")
        print("\nСм. инструкции в SETUP_GUIDE.md")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()

