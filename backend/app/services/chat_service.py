from uuid import uuid4

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import QuestionLog
from app.schemas import ChatRequest, ChatResponse
from app.services.kb_service import get_best_faq, search_faqs
from app.services.llm_service import generate_answer_with_openai
from app.services.log_service import append_question_log


settings = get_settings()


def _build_mock_answer(question: str, matches: list[tuple]) -> str:
    if not matches:
        return settings.fallback_message

    faq, score = matches[0]
    if score >= 0.24:
        return (
            f"По локальной базе знаний я нашла близкую информацию. {faq.answer}"
        )
    return settings.fallback_message


def answer_question(db: Session, payload: ChatRequest) -> ChatResponse:
    session_id = payload.session_id or uuid4().hex[:12]
    question = payload.question.strip()

    matches = search_faqs(db, question, limit=3)
    best_faq, best_score = get_best_faq(db, question)

    answer = settings.fallback_message
    source = "fallback"
    fallback_used = True
    matched_faq_id = None
    matched_confidence = 0.0

    if best_faq and best_score >= settings.faq_match_threshold:
        answer = best_faq.answer
        source = "knowledge_base"
        fallback_used = False
        matched_faq_id = best_faq.id
        matched_confidence = best_score
    else:
        llm_answer = generate_answer_with_openai(question, matches)
        if llm_answer:
            answer = llm_answer
            source = "openai"
            fallback_used = False
            matched_faq_id = best_faq.id if best_faq else None
            matched_confidence = best_score
        elif settings.use_mock_services:
            answer = _build_mock_answer(question, matches)
            source = "mock"
            fallback_used = answer == settings.fallback_message
            matched_faq_id = best_faq.id if best_faq else None
            matched_confidence = best_score

    log_entry = QuestionLog(
        session_id=session_id,
        question=question,
        answer=answer,
        source=source,
        input_mode=payload.input_mode,
        matched_confidence=matched_confidence,
        fallback_used=fallback_used,
        matched_faq_id=matched_faq_id,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    append_question_log(
        {
            "id": log_entry.id,
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "source": source,
            "input_mode": payload.input_mode,
            "matched_confidence": matched_confidence,
            "fallback_used": fallback_used,
            "matched_faq_id": matched_faq_id,
            "created_at": log_entry.created_at,
        }
    )

    return ChatResponse(
        session_id=session_id,
        question=question,
        answer=answer,
        source=source,
        fallback_used=fallback_used,
        matched_faq_id=matched_faq_id,
        matched_confidence=matched_confidence,
    )
