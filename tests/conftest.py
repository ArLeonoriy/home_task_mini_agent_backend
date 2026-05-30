import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Order, FAQItem

@pytest.fixture(autouse=True)
def setup_database():
    # Создаём таблицы
    Base.metadata.create_all(bind=engine)
    # Наполняем тестовыми данными
    db = SessionLocal()
    try:
        if not db.query(Order).count():
            db.add_all([
                Order(id=123, status="shipped", title="Keyboard"),
                Order(id=124, status="processing", title="Mouse"),
                Order(id=125, status="cancelled", title="Monitor"),
            ])
        if not db.query(FAQItem).count():
            db.add_all([
                FAQItem(slug="delivery_time", question="Сколько длится доставка?",
                        answer="Доставка обычно занимает от 2 до 5 рабочих дней.", tags="delivery"),
                FAQItem(slug="return_policy", question="Как оформить возврат?",
                        answer="Возврат можно оформить в течение 14 дней после получения заказа.", tags="return"),
                FAQItem(slug="payment_methods", question="Как оплатить заказ?",
                        answer="Можно оплатить картой или по счету.", tags="payment"),
            ])
        db.commit()
    finally:
        db.close()
    yield
    # После теста удаляем таблицы
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
async def test_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client