#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест улучшенных промптов для подробных ответов
"""

import requests
import json

def test_improved_prompts():
    """Тестируем улучшенные промпты на различных типах запросов"""
    
    print("Тестирование улучшенных промптов...")
    print("=" * 60)
    
    # URL API
    from config import settings
    api_url = f"{settings.base_url}/api/chat/message"
    
    # Тестовые запросы разных типов
    test_cases = [
        {
            "message": "Как зарегистрировать ИП?",
            "expected_keywords": ["этапы", "документы", "сроки", "стоимость", "паспорт", "заявление"],
            "description": "Вопрос о регистрации ИП - должен дать подробный ответ"
        },
        {
            "message": "Какие льготы есть для малого бизнеса?",
            "expected_keywords": ["льготы", "налог", "поддержка", "программы", "условия"],
            "description": "Вопрос о льготах - должен перечислить все доступные"
        },
        {
            "message": "Как получить финансирование для стартапа?",
            "expected_keywords": ["финансирование", "кредит", "грант", "инвестор", "программы"],
            "description": "Вопрос о финансировании - должен описать все программы"
        },
        {
            "message": "Что такое упрощенная система налогообложения?",
            "expected_keywords": ["УСН", "налог", "процент", "доход", "расход", "пример"],
            "description": "Правовой вопрос - должен дать развернутое объяснение"
        },
        {
            "message": "Как развить бизнес в сфере услуг?",
            "expected_keywords": ["клиенты", "маркетинг", "качество", "рекомендации", "шаги"],
            "description": "Бизнес-консультация - должен предложить конкретные шаги"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        message = test_case["message"]
        expected_keywords = test_case["expected_keywords"]
        description = test_case["description"]
        
        print(f"{i}. {description}")
        print(f"   Запрос: '{message}'")
        
        try:
            # Отправляем запрос
            response = requests.post(api_url, json={
                "user_id": f"test_user_prompts_{i}",
                "message": message
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                
                print(f"   Статус: OK")
                print(f"   Длина ответа: {len(response_text)} символов")
                print(f"   Ответ: {response_text[:200]}...")
                
                # Проверяем наличие ключевых слов
                found_keywords = []
                for keyword in expected_keywords:
                    if keyword.lower() in response_text.lower():
                        found_keywords.append(keyword)
                
                if len(found_keywords) >= len(expected_keywords) * 0.6:  # 60% ключевых слов
                    print(f"   УСПЕХ: Найдено {len(found_keywords)}/{len(expected_keywords)} ключевых слов: {found_keywords}")
                else:
                    print(f"   ПРЕДУПРЕЖДЕНИЕ: Найдено только {len(found_keywords)}/{len(expected_keywords)} ключевых слов: {found_keywords}")
                
                # Проверяем структурированность ответа
                if any(marker in response_text for marker in ["•", "-", "1.", "2.", "3.", "📋", "⚖️", "📊"]):
                    print("   УСПЕХ: Ответ структурирован (есть списки/эмодзи)")
                else:
                    print("   ПРЕДУПРЕЖДЕНИЕ: Ответ не структурирован")
                    
            else:
                print(f"   ОШИБКА: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ОШИБКА: Не удается подключиться к серверу")
        except Exception as e:
            print(f"   ОШИБКА: {e}")
        
        print()

if __name__ == "__main__":
    test_improved_prompts()
