import json
import re
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import FAQ
from app.schemas import FAQCreate, FAQRead, FAQUpdate


settings = get_settings()


def tags_to_storage(tags: list[str] | None) -> str:
    return json.dumps(tags or [], ensure_ascii=False)


def tags_from_storage(raw_tags: str | None) -> list[str]:
    if not raw_tags:
        return []
    try:
        parsed = json.loads(raw_tags)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def faq_to_read(faq: FAQ) -> FAQRead:
    return FAQRead(
        id=faq.id,
        question=faq.question,
        answer=faq.answer,
        category=faq.category,
        tags=tags_from_storage(faq.tags),
        source=faq.source,
        is_active=faq.is_active,
        created_at=faq.created_at,
        updated_at=faq.updated_at,
    )


def normalize_text(text: str) -> str:
    normalized = text.lower().strip()
    normalized = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def tokenize(text: str) -> set[str]:
    return {token for token in normalize_text(text).split(" ") if token}


def compute_match_score(query: str, faq: FAQ) -> float:
    query_normalized = normalize_text(query)
    faq_text = " ".join(
        [
            faq.question,
            faq.answer[:240],
            faq.category,
            " ".join(tags_from_storage(faq.tags)),
        ]
    )
    faq_normalized = normalize_text(faq_text)

    query_tokens = tokenize(query_normalized)
    faq_tokens = tokenize(faq_normalized)
    overlap_score = (
        len(query_tokens & faq_tokens) / len(query_tokens) if query_tokens else 0.0
    )
    sequence_score = SequenceMatcher(None, query_normalized, faq_normalized).ratio()
    direct_hit_bonus = 1.0 if query_normalized in faq_normalized else 0.0

    score = (sequence_score * 0.35) + (overlap_score * 0.5) + (direct_hit_bonus * 0.15)
    return round(score, 3)


def search_faqs(db: Session, query: str, limit: int = 5) -> list[tuple[FAQ, float]]:
    faqs = db.query(FAQ).filter(FAQ.is_active.is_(True)).order_by(FAQ.id.asc()).all()
    scored = [(faq, compute_match_score(query, faq)) for faq in faqs]
    scored = [item for item in scored if item[1] > 0]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:limit]


def get_best_faq(db: Session, query: str) -> tuple[FAQ | None, float]:
    matches = search_faqs(db, query=query, limit=1)
    if not matches:
        return None, 0.0
    return matches[0]


def _load_seed_payload() -> list[dict]:
    with settings.seed_faq_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return payload if isinstance(payload, list) else []


def seed_faqs_if_empty(db: Session) -> int:
    existing_count = db.query(FAQ).count()
    if existing_count > 0:
        return existing_count

    payload = _load_seed_payload()
    for item in payload:
        faq = FAQ(
            question=item["question"],
            answer=item["answer"],
            category=item.get("category", "general"),
            tags=tags_to_storage(item.get("tags", [])),
            source=item.get("source", "seed"),
            is_active=item.get("is_active", True),
        )
        db.add(faq)
    db.commit()
    return db.query(FAQ).count()


def reload_seed_faqs(db: Session) -> int:
    payload = _load_seed_payload()
    existing_by_question = {
        faq.question: faq for faq in db.query(FAQ).order_by(FAQ.id.asc()).all()
    }

    for item in payload:
        existing = existing_by_question.get(item["question"])
        if existing:
            existing.answer = item["answer"]
            existing.category = item.get("category", existing.category)
            existing.tags = tags_to_storage(item.get("tags", []))
            existing.source = item.get("source", "seed")
            existing.is_active = item.get("is_active", True)
        else:
            db.add(
                FAQ(
                    question=item["question"],
                    answer=item["answer"],
                    category=item.get("category", "general"),
                    tags=tags_to_storage(item.get("tags", [])),
                    source=item.get("source", "seed"),
                    is_active=item.get("is_active", True),
                )
            )
    db.commit()
    return db.query(FAQ).count()


def create_faq(db: Session, payload: FAQCreate) -> FAQ:
    faq = FAQ(
        question=payload.question,
        answer=payload.answer,
        category=payload.category,
        tags=tags_to_storage(payload.tags),
        source=payload.source,
        is_active=payload.is_active,
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


def update_faq(db: Session, faq: FAQ, payload: FAQUpdate) -> FAQ:
    data = payload.model_dump(exclude_unset=True)
    if "tags" in data:
        data["tags"] = tags_to_storage(data["tags"])

    for field_name, value in data.items():
        setattr(faq, field_name, value)
    db.commit()
    db.refresh(faq)
    return faq
