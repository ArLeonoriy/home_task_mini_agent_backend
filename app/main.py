from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.models import Order, FAQItem
from app.routers import chats, tickets, faq

app = FastAPI(title="Support Chat Agent")

app.include_router(chats.router)
app.include_router(tickets.router)
app.include_router(faq.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
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