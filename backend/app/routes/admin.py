from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import FAQ, QuestionLog
from app.schemas import (
    AdminStatusResponse,
    FAQCreate,
    FAQRead,
    FAQUpdate,
    ReloadResponse,
)
from app.services.kb_service import create_faq, faq_to_read, reload_seed_faqs, update_faq


settings = get_settings()
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status", response_model=AdminStatusResponse)
def get_admin_status(db: Session = Depends(get_db)) -> AdminStatusResponse:
    return AdminStatusResponse(
        app_name=settings.app_name,
        environment=settings.app_env,
        use_mock_services=settings.use_mock_services,
        faq_count=db.query(FAQ).count(),
        questions_logged=db.query(QuestionLog).count(),
    )


@router.get("/faqs", response_model=list[FAQRead])
def admin_list_faqs(db: Session = Depends(get_db)) -> list[FAQRead]:
    faqs = db.query(FAQ).order_by(FAQ.updated_at.desc()).all()
    return [faq_to_read(faq) for faq in faqs]


@router.post("/faqs", response_model=FAQRead, status_code=201)
def admin_create_faq(payload: FAQCreate, db: Session = Depends(get_db)) -> FAQRead:
    existing = db.query(FAQ).filter(FAQ.question == payload.question).first()
    if existing:
        raise HTTPException(status_code=409, detail="FAQ with this question already exists")
    return faq_to_read(create_faq(db, payload))


@router.put("/faqs/{faq_id}", response_model=FAQRead)
def admin_update_faq(
    faq_id: int,
    payload: FAQUpdate,
    db: Session = Depends(get_db),
) -> FAQRead:
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq_to_read(update_faq(db, faq, payload))


@router.delete("/faqs/{faq_id}", status_code=204)
def admin_delete_faq(faq_id: int, db: Session = Depends(get_db)) -> None:
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    db.query(QuestionLog).filter(QuestionLog.matched_faq_id == faq_id).update(
        {QuestionLog.matched_faq_id: None},
        synchronize_session=False,
    )
    db.delete(faq)
    db.commit()


@router.post("/knowledge-base/reload", response_model=ReloadResponse)
def admin_reload_knowledge_base(db: Session = Depends(get_db)) -> ReloadResponse:
    faq_count = reload_seed_faqs(db)
    return ReloadResponse(
        message="Knowledge base reloaded from seed_faq.json",
        faq_count=faq_count,
    )
