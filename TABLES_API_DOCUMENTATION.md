# Документация по API для работы с таблицами

## Обзор

Система теперь поддерживает автоматическое заполнение четырех основных таблиц в Google Sheets:

1. **Complaints** - Жалобы пользователей
2. **Legislation** - Законодательство и нормативные акты
3. **Events** - Мероприятия и события
4. **ChatAnalytics** - Аналитика чата

## API Endpoints

### 1. Жалобы (Complaints)

#### POST `/api/complaints/submit`
Подать жалобу

**Тело запроса:**
```json
{
  "complaint_id": "uuid",
  "user_id": "user_123",
  "full_name": "Иванов Иван Иванович",
  "email": "ivanov@example.com",
  "phone": "+7 (999) 123-45-67",
  "organization": "ООО Тест",
  "complaint_text": "Текст жалобы",
  "category": "Банковские услуги",
  "priority": "Высокий"
}
```

#### GET `/api/complaints/list?status=Новая`
Получить список жалоб с фильтром по статусу

#### GET `/api/complaints/statistics`
Получить статистику по жалобам

### 2. Законодательство (Legislation)

#### POST `/api/legislation/add`
Добавить информацию о законодательстве

**Тело запроса:**
```json
{
  "title": "Название закона",
  "url": "https://example.com/law",
  "publication_date": "2024-01-15",
  "description": "Описание закона",
  "category": "Поддержка МСП",
  "importance": "Высокая"
}
```

#### GET `/api/legislation/list?category=Поддержка МСП`
Получить список законодательства с фильтром по категории

#### GET `/api/legislation/statistics`
Получить статистику по законодательству

### 3. Мероприятия (Events)

#### POST `/api/events/create`
Создать мероприятие

**Тело запроса:**
```json
{
  "event_id": "uuid",
  "title": "Название мероприятия",
  "date": "2024-02-15",
  "time": "14:00",
  "description": "Описание мероприятия",
  "location": "Место проведения",
  "participants": ["Участник 1", "Участник 2"],
  "organizer": "Организатор",
  "status": "Запланировано"
}
```

#### GET `/api/events/list?status=Запланировано`
Получить список мероприятий с фильтром по статусу

#### GET `/api/events/statistics`
Получить статистику по мероприятиям

### 4. Аналитика чата (Chat Analytics)

#### POST `/api/chat-analytics/save`
Сохранить данные аналитики чата

**Тело запроса:**
```json
{
  "session_id": "uuid",
  "user_id": "user_123",
  "message_count": 5,
  "response_time_avg": 2.3,
  "satisfaction_score": 4.5,
  "topics_discussed": ["документы", "регистрация"],
  "documents_created": 1,
  "session_duration": 300
}
```

#### GET `/api/chat-analytics/list?user_id=user_123`
Получить данные аналитики с фильтром по пользователю

#### POST `/api/chat-analytics/end-session?session_id=uuid&satisfaction_score=4.5`
Завершить сессию чата и сохранить аналитику

#### GET `/api/chat-analytics/session/{session_id}`
Получить статистику текущей сессии

#### GET `/api/chat-analytics/statistics`
Получить общую статистику по аналитике чата

## Автоматическое заполнение

### Аналитика чата
Система автоматически собирает аналитику во время работы чата:

- **Время ответа** - измеряется для каждого сообщения
- **Темы обсуждения** - автоматически извлекаются из сообщений
- **Создание документов** - отслеживается автоматически
- **Длительность сессии** - измеряется от начала до завершения

### Интеграция с чатом
При каждом сообщении в чате автоматически:
1. Создается или продолжается сессия аналитики
2. Измеряется время ответа
3. Извлекаются темы из сообщения
4. Отмечается создание документов
5. При завершении сессии сохраняется полная аналитика

## Структура таблиц в Google Sheets

### Complaints
| ID | User ID | ФИО | Email | Телефон | Организация | Текст жалобы | Категория | Приоритет | Статус | Дата подачи | Дата обработки |

### Legislation
| Название | URL | Дата публикации | Описание | Категория | Важность | Дата добавления |

### Events
| ID мероприятия | Название | Дата | Время | Описание | Место проведения | Участники | Организатор | Статус | Дата создания |

### ChatAnalytics
| ID сессии | User ID | Количество сообщений | Среднее время ответа (сек) | Оценка удовлетворенности | Обсуждаемые темы | Создано документов | Длительность сессии (сек) | Дата создания |

## Тестирование

Для тестирования всех функций используйте скрипт:

```bash
python test_tables_filling.py
```

Скрипт проверит:
- Подключение к Google Sheets
- Заполнение всех таблиц
- Получение данных
- Статистику

## Мониторинг

Все операции логируются с помощью системы логирования:
- Успешные операции помечаются как `SUCCESS`
- Ошибки помечаются как `ERROR`
- Предупреждения помечаются как `WARNING`

## Настройка

Убедитесь, что в файле `.env` настроены:
- `GOOGLE_SHEET_ID` - ID таблицы Google Sheets
- `GOOGLE_CREDENTIALS_FILE` - путь к файлу с учетными данными

## Примеры использования

### Создание жалобы через API
```python
import requests

complaint_data = {
    "complaint_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user_123",
    "full_name": "Иванов Иван Иванович",
    "email": "ivanov@example.com",
    "complaint_text": "Некачественное обслуживание",
    "category": "Банковские услуги",
    "priority": "Высокий"
}

response = requests.post("http://localhost:8000/api/complaints/submit", json=complaint_data)
print(response.json())
```

### Получение статистики
```python
import requests

# Общая статистика
response = requests.get("http://localhost:8000/api/reports/statistics")
stats = response.json()
print(f"Всего пользователей: {stats['total_users']}")
print(f"Всего жалоб: {stats['total_complaints']}")
print(f"Всего мероприятий: {stats['total_events']}")
```

### Работа с аналитикой чата
```python
import requests

# Завершение сессии с оценкой
response = requests.post(
    "http://localhost:8000/api/chat-analytics/end-session",
    params={"session_id": "session_123", "satisfaction_score": 4.5}
)
print(response.json())
```
