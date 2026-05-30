import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_faq_search_return(test_client: AsyncClient):
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    resp = await test_client.post(f"/chats/{chat_id}/messages", json={"content": "как оформить возврат?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Возврат можно оформить" in data["assistant_message"]["content"]
    assert "faq:return_policy" in data["assistant_message"]["content"]

@pytest.mark.asyncio
async def test_faq_not_found(test_client: AsyncClient):
    chat_resp = await test_client.post("/chats")
    chat_id = chat_resp.json()["id"]
    resp = await test_client.post(f"/chats/{chat_id}/messages", json={"content": "оплата криптовалютой"})
    assert resp.status_code == 200
    data = resp.json()
    assert "не нашел информацию" in data["assistant_message"]["content"].lower()

@pytest.mark.asyncio
async def test_faq_list_endpoint(test_client: AsyncClient):
    resp = await test_client.get("/faq")
    assert resp.status_code == 200
    assert len(resp.json()) == 3