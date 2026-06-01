from sqlalchemy.orm import Session
from app.models import Order, Ticket, FAQItem

def get_order_status(db: Session, order_id: int) -> dict:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"found": False, "order_id": order_id}
    return {"found": True, "order_id": order.id, "status": order.status, "title": order.title}

def create_support_ticket(db: Session, chat_id: int, text: str, order_id: int = None) -> dict:
    ticket = Ticket(chat_id=chat_id, text=text, order_id=order_id, status="open")
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {"id": ticket.id, "status": ticket.status}

def search_faq(db: Session, query: str) -> dict:
    items = db.query(FAQItem).all()
    best = None
    best_score = 0
    q_lower = query.lower()
    for item in items:
        score = 0
        tags = [t.strip().lower() for t in item.tags.split(",")]
        for tag in tags:
            if tag in q_lower:
                score += 2
        for word in q_lower.split():
            if word in item.question.lower():
                score += 1
        if score > best_score:
            best_score = score
            best = item
    if best and best_score > 0:
        return {"found": True, "answer": best.answer, "source": f"faq:{best.slug}"}
    return {"found": False}