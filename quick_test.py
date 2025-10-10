"""
🧪 Быстрый тест Умного Помощника для Документов
Запустите сначала сервер: python main.py
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER_ID = "test-smart-assistant-001"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_server():
    """Проверка, запущен ли сервер"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def send_message(message):
    """Отправка сообщения и анализ ответа"""
    print(f"\n💬 Вы: {message}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat/message",
        json={"user_id": USER_ID, "message": message}
    )
    
    result = response.json()
    print(f"🤖 Ассистент: {result.get('response', '')[:200]}...")
    
    # Проверяем document_suggestion
    doc_sugg = result.get("document_suggestion")
    if doc_sugg:
        print("\n📄 АНАЛИЗ ДОКУМЕНТА:")
        
        # Рекомендация шаблона
        rec = doc_sugg.get("template_recommendation", {})
        if rec:
            print(f"  📋 Рекомендуемый шаблон: {rec.get('suggested_template_name', 'не определен')}")
            print(f"  🎯 Уверенность: {rec.get('confidence', 0)}%")
            print(f"  📂 Категория: {rec.get('document_category', 'неизвестно')}")
        
        # Анализ полноты
        comp = doc_sugg.get("completeness_analysis", {})
        if comp:
            print(f"\n  📊 МЕТРИКИ КАЧЕСТВА:")
            print(f"    ├─ Completeness Score: {comp.get('completeness_score', 0)}%")
            print(f"    ├─ Confidence Score: {comp.get('confidence_score', 0)}%")
            print(f"    ├─ Data Quality: {comp.get('data_quality', 'unknown')}")
            print(f"    └─ Можно создать: {'✅ ДА' if comp.get('can_generate') else '❌ НЕТ'}")
            
            missing = comp.get('missing_fields', [])
            if missing:
                print(f"\n  ⚠️  Недостающие поля ({len(missing)}):")
                for field in missing[:5]:
                    print(f"      • {field}")
            
            recommendations = comp.get('recommendations', [])
            if recommendations:
                print(f"\n  💡 Рекомендации:")
                for rec in recommendations[:3]:
                    print(f"      • {rec}")
            
            questions = comp.get('suggested_questions', [])
            if questions:
                print(f"\n  ❓ Предложенные вопросы:")
                for q in questions[:3]:
                    print(f"      • {q}")
    
    return result

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🧪 БЫСТРЫЙ ТЕСТ УМНОГО ПОМОЩНИКА ДЛЯ ДОКУМЕНТОВ                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Проверка сервера
    print("🔍 Проверка сервера...")
    if not check_server():
        print("""
❌ ОШИБКА: Сервер не запущен!

Запустите сервер в отдельном терминале:
    python main.py

Или:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

После запуска сервера запустите этот скрипт снова.
        """)
        return
    
    print("✅ Сервер работает!\n")
    
    # ТЕСТ 1: Минимальные данные
    print_section("ТЕСТ 1: Обнаружение намерения создать документ")
    send_message("Хочу создать анкету на вступление в организацию")
    time.sleep(1)
    
    # ТЕСТ 2: Частичные данные
    print_section("ТЕСТ 2: Сбор данных из диалога")
    send_message("Меня зовут Иван Петров, email: ivan@example.com, телефон +79991234567")
    time.sleep(1)
    
    # ТЕСТ 3: Полные данные
    print_section("ТЕСТ 3: Создание документа с полными данными")
    send_message("""
    Создайте анкету для вступления в организацию.
    ФИО: Петров Петр Петрович
    Email: petrov@mail.ru
    Телефон: +79991234567
    Организация: ООО Успех
    ИНН: 1234567890
    Должность: Директор
    """)
    time.sleep(1)
    
    # ТЕСТ 4: Получение списка шаблонов
    print_section("ТЕСТ 4: Проверка доступных шаблонов")
    try:
        response = requests.get(f"{BASE_URL}/api/documents/templates")
        templates = response.json()
        
        if templates:
            print(f"\n✅ Найдено шаблонов: {len(templates)}")
            for i, tmpl in enumerate(templates, 1):
                print(f"  {i}. {tmpl.get('name')} (ID: {tmpl.get('template_id')[:8]}...)")
            
            # ТЕСТ 5: Предпросмотр с первым шаблоном
            if len(templates) > 0:
                template_id = templates[0]["template_id"]
                
                print_section("ТЕСТ 5: Предпросмотр документа")
                print(f"\n📄 Шаблон: {templates[0]['name']}")
                
                preview_response = requests.post(
                    f"{BASE_URL}/api/chat/preview-document",
                    params={"template_id": template_id},
                    json={
                        "full_name": "Иванов Иван Иванович",
                        "email": "ivan@mail.ru",
                        "phone": "+79991234567",
                        "organization": "ООО Тест",
                        "inn": "1234567890",
                        "position": "Директор"
                    }
                )
                
                preview = preview_response.json()
                if preview.get("status") == "success":
                    print(f"\n✅ Предпросмотр создан!")
                    print(f"\n{preview.get('preview', '')[:300]}...")
                    
                    comp = preview.get('completeness', {})
                    print(f"\n📊 МЕТРИКИ ПРЕДПРОСМОТРА:")
                    print(f"  ├─ Completeness: {comp.get('completeness_score', 0)}%")
                    print(f"  ├─ Confidence: {comp.get('confidence_score', 0)}%")
                    print(f"  └─ Можно создать: {'✅ ДА' if preview.get('can_generate') else '❌ НЕТ'}")
                else:
                    print(f"❌ Ошибка: {preview.get('message')}")
        else:
            print("\n⚠️  Шаблоны не найдены.")
            print("\nЗагрузите шаблон:")
            print("  1. Откройте: http://localhost:8000/static/template-manager.html")
            print("  2. Или используйте API: POST /api/documents/upload")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Итоги
    print_section("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("""
📚 Полная документация:
  • SMART_DOCUMENT_ASSISTANT_GUIDE.md - Руководство
  • TESTING_SMART_ASSISTANT.md - Подробные тесты
  • SMART_ASSISTANT_UPDATE_SUMMARY.md - Обзор обновлений

🌐 Веб-интерфейсы:
  • Чат: http://localhost:8000/static/chat-widget.html
  • Главный интерфейс: http://localhost:8000/static/main-interface.html
  • API Docs: http://localhost:8000/docs

🎯 Следующие шаги:
  1. Попробуйте веб-интерфейс чата
  2. Загрузите свои шаблоны документов
  3. Протестируйте с реальными данными
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()









