#!/usr/bin/env python3
"""
Тест с реальным email адресом
"""
import requests
import json

def test_with_real_email():
    """Тестируем с реальным email"""
    print("=" * 50)
    print("ТЕСТ С РЕАЛЬНЫМ EMAIL")
    print("=" * 50)
    
    # ВАЖНО: Замените на ваш реальный email!
    real_email = input("Введите ваш реальный email для тестирования: ").strip()
    
    if not real_email:
        print("[ERROR] Email не введен")
        return
    
    try:
        url = "http://localhost:8000/api/chat/create-document"
        
        params = {
            "user_id": "real-test-user",
            "template_id": "9b7e12a8-1d43-4c30-b4ec-33ded0ca1f22",
            "send_email": True
        }
        
        data = {
            "user_data": {
                "email": real_email,  # РЕАЛЬНЫЙ EMAIL!
                "full_name": "Тест Тестович",
                "organization": "Тестовая организация"
            },
            "conversation_data": {
                "message": "Создание документа",
                "response": "Документ создается"
            }
        }
        
        print(f"[INFO] Отправляем документ на {real_email}")
        print(f"[REQUEST] POST {url}")
        
        response = requests.post(url, params=params, json=data, timeout=30)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Документ создан!")
            print(f"  Status: {result.get('status', '')}")
            print(f"  Message: {result.get('message', '')}")
            
            if '[EMAIL]' in result.get('message', ''):
                print(f"[SUCCESS] Email отправлен на {real_email}")
                print(f"[INFO] Проверьте вашу почту (включая папку 'Спам')")
            else:
                print(f"[ERROR] Email не отправлен")
        else:
            print(f"[ERROR] HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")

if __name__ == "__main__":
    test_with_real_email()
