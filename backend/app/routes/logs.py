from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Query

from app.database import get_db
from app.models import QuestionLog
from app.schemas import LogsStatsResponse, QuestionLogRead


router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/questions", response_model=list[QuestionLogRead])
def list_question_logs(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[QuestionLogRead]:
    return (
        db.query(QuestionLog)
        .order_by(QuestionLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/stats", response_model=LogsStatsResponse)
def get_logs_stats(db: Session = Depends(get_db)) -> LogsStatsResponse:
    total_questions = db.query(func.count(QuestionLog.id)).scalar() or 0
    fallback_count = (
        db.query(func.count(QuestionLog.id))
        .filter(QuestionLog.fallback_used.is_(True))
        .scalar()
        or 0
    )
    kb_answer_count = (
        db.query(func.count(QuestionLog.id))
        .filter(QuestionLog.source == "knowledge_base")
        .scalar()
        or 0
    )
    openai_answer_count = (
        db.query(func.count(QuestionLog.id))
        .filter(QuestionLog.source == "openai")
        .scalar()
        or 0
    )
    voice_questions_count = (
        db.query(func.count(QuestionLog.id))
        .filter(QuestionLog.input_mode == "voice")
        .scalar()
        or 0
    )

    return LogsStatsResponse(
        total_questions=total_questions,
        fallback_count=fallback_count,
        kb_answer_count=kb_answer_count,
        openai_answer_count=openai_answer_count,
        voice_questions_count=voice_questions_count,
    )
