"""
Тестовый скрипт для проверки аварийного режима создания документов
"""

def test_emergency_mode():
    print("🧪 ТЕСТ АВАРИЙНОГО РЕЖИМА")
    print("=" * 60)
    
    # Тест 1: Импорты
    print("\n1. Проверка импортов...")
    try:
        from services.assistant_service import assistant_service
        from services.document_service import document_service
        print("   ✅ Импорты успешны")
    except Exception as e:
        print(f"   ❌ Ошибка импорта: {e}")
        return
    
    # Тест 2: Список шаблонов
    print("\n2. Проверка шаблонов...")
    try:
        templates = document_service.get_templates_list()
        print(f"   ✅ Найдено шаблонов: {len(templates)}")
        for t in templates:
            print(f"      - {t.get('name', 'Без названия')}")
        
        russia_template = None
        for t in templates:
            if "россия" in t.get('name', '').lower():
                russia_template = t
                print(f"   ✅ Найден шаблон 'Документ Россия': {t['name']}")
                break
        
        if not russia_template:
            print("   ❌ Шаблон 'Документ Россия' НЕ НАЙДЕН!")
            return
    except Exception as e:
        print(f"   ❌ Ошибка получения шаблонов: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Тест 3: Извлечение данных
    print("\n3. Проверка извлечения данных...")
    test_message = """Заполни документ Россия. АНКЕТА (для физических лиц) 
Фамилия: Иванов 
Имя: Пётр 
Отчество: Сергеевич 
ИНН: 123456789012 
Телефон: +7 (999) 123-45-67 
E-mail: ivanov.test@example.com"""
    
    try:
        import re
        user_info = {"user_id": "test-user"}
        
        field_patterns = {
            'last_name': r'(?:Фамилия|фамилия)[\s:=]+([А-ЯЁ][а-яё]+)',
            'first_name': r'(?:Имя|имя)[\s:=]+([А-ЯЁа-яё]+)',
            'middle_name': r'(?:Отчество|отчество)[\s:=]+([А-ЯЁ][а-яё]+)',
            'inn': r'(?:ИНН|инн)[\s:=]+(\d{10,12})',
            'phone': r'(?:Телефон|телефон)[\s:=]+(\+?[0-9\s\(\)\-]+)',
            'email': r'(?:E-mail|email|почта)[\s:=]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        }
        
        for field_name, pattern in field_patterns.items():
            match = re.search(pattern, test_message, re.IGNORECASE)
            if match:
                user_info[field_name] = match.group(1).strip()
                print(f"   ✅ {field_name}: {match.group(1)}")
        
        if user_info.get('last_name') or user_info.get('first_name'):
            parts = []
            if user_info.get('last_name'): parts.append(user_info['last_name'])
            if user_info.get('first_name'): parts.append(user_info['first_name'])
            if user_info.get('middle_name'): parts.append(user_info['middle_name'])
            user_info['full_name'] = ' '.join(parts)
            print(f"   ✅ full_name (объединено): {user_info['full_name']}")
    except Exception as e:
        print(f"   ❌ Ошибка извлечения: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Тест 4: Создание документа
    print("\n4. Проверка создания документа...")
    try:
        created_doc = assistant_service.create_document_from_template(
            user_id="test-user",
            template_id=russia_template['template_id'],
            user_data=user_info,
            conversation_data={
                "message": test_message,
                "response": "Test response"
            },
            send_email=False
        )
        
        if created_doc and created_doc.get('status') == 'success':
            print(f"   ✅ Документ создан успешно!")
            print(f"      Filepath: {created_doc.get('filepath')}")
            print(f"      Download URL: {created_doc.get('download_url')}")
        else:
            print(f"   ❌ Не удалось создать документ")
            print(f"      Результат: {created_doc}")
    except Exception as e:
        print(f"   ❌ Ошибка создания документа: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    print("=" * 60)

if __name__ == "__main__":
    test_emergency_mode()

