from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import FAQItem
from app.schemas import FAQItemResponse

router = APIRouter(prefix="/faq", tags=["faq"])

@router.get("", response_model=list[FAQItemResponse])
def list_faq(db: Session = Depends(get_db)):
    items = db.query(FAQItem).all()
    return items