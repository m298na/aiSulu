from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FAQ
from app.schemas import FAQRead, KnowledgeSearchResponse
from app.services.kb_service import faq_to_read, search_faqs


router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.get("/faqs", response_model=list[FAQRead])
def list_faqs(db: Session = Depends(get_db)) -> list[FAQRead]:
    faqs = db.query(FAQ).filter(FAQ.is_active.is_(True)).order_by(FAQ.id.asc()).all()
    return [faq_to_read(faq) for faq in faqs]


@router.get("/faqs/{faq_id}", response_model=FAQRead)
def get_faq(faq_id: int, db: Session = Depends(get_db)) -> FAQRead:
    faq = db.query(FAQ).filter(FAQ.id == faq_id, FAQ.is_active.is_(True)).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq_to_read(faq)


@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge_base(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> KnowledgeSearchResponse:
    matches = search_faqs(db, query=q, limit=limit)
    return KnowledgeSearchResponse(
        query=q,
        results=[faq_to_read(faq) for faq, _score in matches],
    )
