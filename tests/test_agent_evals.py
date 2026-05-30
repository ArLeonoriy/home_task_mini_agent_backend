import pytest
import json
from httpx import AsyncClient

# Eval-сценарии: (сообщение, ожидаемая подстрока в ответе, ожидаемые роли в истории, ожидаемые типы событий)
eval_scenarios = [
    # 1. Обычное сообщение без tool call
    ("Привет!", "Echo: Привет!", ["user", "assistant"], []),
    # 2. Статус существующего заказа
    ("статус заказа 123", "shipped", ["user", "tool", "assistant"], ["tool_call", "tool_result"]),
    # 3. Статус несуществующего заказа
    ("статус заказа 999", "Не нашел заказ", ["user", "tool", "assistant"], ["tool_call", "tool_result"]),
    # 4. Сообщение о проблеме с заказом
    ("проблема с заказом 124", "Создал обращение", ["user", "tool", "assistant"], ["tool_call", "tool_result"]),
    # 5. Сообщение о проблеме без номера заказа
    ("у меня проблема, товар сломался", "Создал обращение", ["user", "tool", "assistant"], ["tool_call", "tool_result"]),
    # 6. FAQ вопрос про возврат
    ("как вернуть товар?", "Возврат можно оформить", ["user", "tool", "assistant"], ["tool_call", "tool_result"]),
    # 7. FAQ вопрос без результата (содержит ключевое слово, но ничего не находит)
    ("оплата криптовалютой", "не нашел информацию", ["user", "tool", "assistant"], ["tool_call", "tool_result"]),
    # 8. Follow-up вопрос (предварительно задаём контекст)
    # Этот сценарий проверяется отдельной логикой: сначала статус заказа, потом follow-up.
]

@pytest.mark.asyncio
@pytest.mark.parametrize("message, expected_substr, expected_roles, expected_event_types", eval_scenarios)
async def test_eval_scenario(test_client: AsyncClient, message, expected_substr, expected_roles, expected_event_types):
    # Создаём новый чат для каждого сценария
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    resp = await test_client.post(f"/chats/{chat_id}/messages", json={"content": message})
    assert resp.status_code == 200
    data = resp.json()
    assert expected_substr in data["assistant_message"]["content"]

    # Проверяем роли в истории
    hist_resp = await test_client.get(f"/chats/{chat_id}/messages")
    messages = hist_resp.json()
    roles = [m["role"] for m in messages]
    for role in expected_roles:
        assert role in roles

    # Проверяем события агента
    events_resp = await test_client.get(f"/chats/{chat_id}/events")
    events = events_resp.json()
    event_types = [e["event_type"] for e in events]
    for etype in expected_event_types:
        assert etype in event_types

@pytest.mark.asyncio
async def test_eval_followup(test_client: AsyncClient):
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    # Первое сообщение – статус заказа
    await test_client.post(f"/chats/{chat_id}/messages", json={"content": "какой статус заказа 123?"})
    # Follow-up
    resp = await test_client.post(f"/chats/{chat_id}/messages", json={"content": "а когда он был создан?"})
    data = resp.json()
    assert "shipped" in data["assistant_message"]["content"]  # должно быть про заказ 123
    # Проверяем, что в истории два ассистентских ответа и два tool-сообщения
    hist_resp = await test_client.get(f"/chats/{chat_id}/messages")
    messages = hist_resp.json()
    roles = [m["role"] for m in messages]
    assert roles.count("user") == 2
    assert roles.count("tool") == 2
    assert roles.count("assistant") == 2