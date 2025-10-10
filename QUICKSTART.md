# ⚡ Быстрый старт

## За 5 минут к работающему ассистенту!

### 1️⃣ Установка (2 минуты)

```bash
# Клонируйте проект
git clone <url>
cd AIAI

# Создайте виртуальное окружение
python -m venv venv

# Активируйте (Windows)
venv\Scripts\activate

# Активируйте (Linux/Mac)
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 2️⃣ Настройка Google Sheets (1 минута)

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API
3. Создайте Service Account → Скачайте `credentials.json`
4. Создайте [Google Sheets таблицу](https://sheets.google.com/)
5. Поделитесь таблицей с email из `credentials.json`

### 3️⃣ Получите OpenAI ключ (1 минута)

1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com/)
2. Создайте API ключ
3. Пополните баланс ($5 минимум)

### 4️⃣ Настройте .env (30 секунд)

Создайте файл `.env`:

```env
OPENAI_API_KEY=sk-proj-ваш_ключ
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID=ваш_id_из_url_таблицы
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 5️⃣ Проверьте настройки (30 секунд)

```bash
python test_setup.py
```

Если все ✓ - переходите к следующему шагу!

### 6️⃣ Запустите приложение! (10 секунд)

```bash
python main.py
```

### 7️⃣ Проверьте работу

Откройте в браузере:

- 🏠 **Главная:** http://localhost:8000
- 📖 **API Docs:** http://localhost:8000/docs
- 💬 **Чат:** http://localhost:8000/static/chat-widget.html

## 🎉 Готово!

Теперь у вас работает полноценный AI-ассистент!

## 🚀 Что дальше?

### Протестируйте функции:

1. **Чат с ассистентом**
   - Откройте http://localhost:8000/static/chat-widget.html
   - Напишите "Привет!"

2. **Анализ МСП**
   - В чате нажмите кнопку "📊 Анализ МСП"
   - Или напишите: "Покажи тренды малого бизнеса"

3. **Подача заявки**
   - Нажмите "📝 Подать заявку"
   - Заполните данные в диалоге

4. **Посмотрите API документацию**
   - http://localhost:8000/docs
   - Попробуйте эндпоинты прямо в браузере!

5. **Проверьте Google Sheets**
   - Откройте вашу таблицу
   - Должны появиться новые листы с данными

### Настройте под себя:

1. **Измените промпт ассистента**
   - Файл: `integrations/openai_service.py`
   - Переменная: `system_prompt`

2. **Добавьте свои шаблоны документов**
   - Папка: `templates/documents/`
   - Код: `services/document_service.py`

3. **Настройте расписание задач**
   - Файл: `main.py`
   - Функции: `scheduled_*`

4. **Кастомизируйте виджет**
   - Стили: `static/chat-widget.css`
   - Логика: `static/chat-widget.js`

## 📚 Полная документация

- [README.md](README.md) - Полное описание проекта
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Детальная настройка
- http://localhost:8000/docs - API документация

## 🆘 Нужна помощь?

### Частые вопросы:

**Q: Ошибка "credentials.json not found"**  
A: Поместите файл `credentials.json` в корень проекта

**Q: OpenAI возвращает ошибку**  
A: Проверьте баланс на аккаунте и правильность API ключа

**Q: Google Sheets не работает**  
A: Убедитесь, что Service Account добавлен в таблицу с правами редактора

**Q: CORS ошибка в браузере**  
A: Это нормально для localhost. В продакшене настройте правильные origins

### Дополнительная помощь:

- 📧 Создайте Issue в репозитории
- 📖 Читайте логи в консоли
- 🔍 Проверьте `.env` файл

---

**Приятной работы с AI-ассистентом! 🤖✨**

