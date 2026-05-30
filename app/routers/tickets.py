from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Ticket
from ..schemas import TicketResponse, TicketUpdateRequest

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("", response_model=list[TicketResponse])
def list_tickets(status: str = Query(None, description="Фильтр по статусу (open, in_progress, closed)"),
                 db: Session = Depends(get_db)):
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    tickets = query.order_by(Ticket.created_at).all()
    return tickets

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    return ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, req: TicketUpdateRequest, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    ticket.status = req.status
    db.commit()
    db.refresh(ticket)
    return ticket