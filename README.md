# Mini Support Agent Backend

Тестовый backend-сервис на FastAPI, имитирующий работу чатового AI-агента поддержки.  
Использует `FakeLLMClient` вместо реальной LLM.

Убедитесь,что установлен Python 3.10.6 
(Более поздние версии также должны работать, в случае ошибки, установите конкретную версию)


1. Клонируйте или скачайте репозиторий и перейдите в папку проекта.

2. Создайте виртуальное окружение:

python -m venv venv
source venv/bin/activate      # для Linux/macOS
venv\Scripts\activate         # для Windows

3. Установите зависимости:

pip install -r requirements.txt

4. Запустите приложение одним из способов:

1 способ : Скрипт

./start.sh   # или start.bat для Windows

2 способ : Вручную

uvicorn app.main:app --reload

5. Откройте документацию: http://127.0.0.1:8000/docs

6. Запуск тестов

pytest -v

7. API Endpoints

POST /chats – создать новый чат.

GET /chats/{chat_id} – получить информацию о чате.

POST /chats/{chat_id}/messages – отправить сообщение, получить ответ ассистента.

GET /chats/{chat_id}/messages – история сообщений чата.

GET /chats/{chat_id}/events – события агента (tool_call / tool_result), можно фильтровать ?event_type=tool_call.

GET /tickets – список обращений (фильтр ?status=open).

GET /tickets/{ticket_id} – детали обращения.

PATCH /tickets/{ticket_id} – обновить статус обращения (open, in_progress, closed).

GET /faq – список FAQ‑записей.

Как работает обработка сообщения
Сохраняется сообщение пользователя (роль user).

Определяется контекст: последний order_id из истории сообщений.

FakeLLMClient решает, нужен ли вызов инструмента (get_order_status, create_support_ticket, search_faq) или прямой ответ.

При вызове инструмента:

сохраняется событие tool_call,

выполняется инструмент,

результат сохраняется как сообщение role="tool",

сохраняется событие tool_result,

генерируется ответ ассистента на основе результата.

Ответ ассистента сохраняется и возвращается клиенту.

8. Структура проекта

app/main.py – инициализация FastAPI

app/database.py – подключение SQLite

app/models.py – SQLAlchemy модели

app/schemas.py – Pydantic схемы

app/services/llm_client.py – эмуляция LLM

app/services/tools.py – инструменты агента

app/services/message_processor.py – обработка сообщения

app/routers/ – HTTP эндпоинты

tests/ – тесты и eval‑сценарии