import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_ticket_through_agent(test_client: AsyncClient):
    # Создаём чат и отправляем сообщение о проблеме
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    resp = await test_client.post(f"/chats/{chat_id}/messages",
                                  json={"content": "у меня проблема с заказом 123, товар не пришел"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Создал обращение" in data["assistant_message"]["content"]

    # Проверяем, что обращение появилось в списке
    tickets_resp = await test_client.get("/tickets")
    tickets = tickets_resp.json()
    assert len(tickets) == 1
    assert tickets[0]["order_id"] == 123

@pytest.mark.asyncio
async def test_get_ticket(test_client: AsyncClient):
    # Создаём обращение
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    await test_client.post(f"/chats/{chat_id}/messages", json={"content": "проблема с заказом 124"})
    tickets = (await test_client.get("/tickets")).json()
    ticket_id = tickets[0]["id"]

    resp = await test_client.get(f"/tickets/{ticket_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == ticket_id

@pytest.mark.asyncio
async def test_update_ticket_status(test_client: AsyncClient):
    # Создаём обращение
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    await test_client.post(f"/chats/{chat_id}/messages", json={"content": "жалоба на заказ 125"})
    tickets = (await test_client.get("/tickets")).json()
    ticket_id = tickets[0]["id"]

    # Обновляем статус
    update_resp = await test_client.patch(f"/tickets/{ticket_id}", json={"status": "in_progress"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "in_progress"

    # Проверяем, что неверный статус вызывает ошибку
    invalid_resp = await test_client.patch(f"/tickets/{ticket_id}", json={"status": "unknown"})
    assert invalid_resp.status_code == 422

@pytest.mark.asyncio
async def test_ticket_404(test_client: AsyncClient):
    resp = await test_client.get("/tickets/9999")
    assert resp.status_code == 404