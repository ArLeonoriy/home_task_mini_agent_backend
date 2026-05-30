import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_chat(test_client: AsyncClient):
    resp = await test_client.post("/chats")
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_get_chat_404(test_client: AsyncClient):
    resp = await test_client.get("/chats/9999")
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_send_simple_message(test_client: AsyncClient):
    # Создаём чат
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    # Отправляем обычное сообщение
    msg_resp = await test_client.post(f"/chats/{chat_id}/messages", json={"content": "Привет"})
    assert msg_resp.status_code == 200
    data = msg_resp.json()
    assert data["assistant_message"]["content"] == "Echo: Привет"

@pytest.mark.asyncio
async def test_order_status_existing(test_client: AsyncClient):
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    resp = await test_client.post(f"/chats/{chat_id}/messages", json={"content": "какой статус заказа 123?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "shipped" in data["assistant_message"]["content"]

@pytest.mark.asyncio
async def test_order_status_non_existing(test_client: AsyncClient):
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    resp = await test_client.post(f"/chats/{chat_id}/messages", json={"content": "статус заказа 999"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Не нашел заказ" in data["assistant_message"]["content"]

@pytest.mark.asyncio
async def test_followup_order(test_client: AsyncClient):
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    # Первое сообщение с номером заказа
    await test_client.post(f"/chats/{chat_id}/messages", json={"content": "какой статус заказа 123?"})
    # Follow-up без номера
    resp = await test_client.post(f"/chats/{chat_id}/messages", json={"content": "а когда он был создан?"})
    assert resp.status_code == 200
    data = resp.json()
    # Ответ должен содержать статус заказа 123
    assert "123" in data["assistant_message"]["content"] and "shipped" in data["assistant_message"]["content"]

@pytest.mark.asyncio
async def test_missing_order_number(test_client: AsyncClient):
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    resp = await test_client.post(f"/chats/{chat_id}/messages", json={"content": "какой статус заказа?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "укажите номер заказа" in data["assistant_message"]["content"].lower()

@pytest.mark.asyncio
async def test_history_and_events(test_client: AsyncClient):
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    # Отправляем сообщение с заказом
    await test_client.post(f"/chats/{chat_id}/messages", json={"content": "статус заказа 124"})
    # Проверяем историю сообщений
    hist_resp = await test_client.get(f"/chats/{chat_id}/messages")
    messages = hist_resp.json()
    roles = [m["role"] for m in messages]
    assert "user" in roles
    assert "tool" in roles
    assert "assistant" in roles

    # Проверяем события агента
    events_resp = await test_client.get(f"/chats/{chat_id}/events")
    events = events_resp.json()
    event_types = [e["event_type"] for e in events]
    assert "tool_call" in event_types
    assert "tool_result" in event_types

@pytest.mark.asyncio
async def test_get_chat_success(test_client: AsyncClient):
    chat_resp = await test_client.post("/chats")
    assert chat_resp.status_code == 201
    chat_id = chat_resp.json()["id"]
    get_resp = await test_client.get(f"/chats/{chat_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == chat_id
    assert "created_at" in data

    