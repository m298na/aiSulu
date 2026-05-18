from collections.abc import Iterable

from openai import OpenAI

from app.config import get_settings
from app.models import FAQ
from app.services.kb_service import tags_from_storage


settings = get_settings()


def openai_is_available() -> bool:
    return bool(
        settings.openai_enabled and settings.openai_api_key and not settings.use_mock_services
    )


def _build_context_block(matches: Iterable[tuple[FAQ, float]]) -> str:
    lines: list[str] = []
    for faq, score in matches:
        tags = ", ".join(tags_from_storage(faq.tags))
        lines.append(
            "\n".join(
                [
                    f"Вопрос: {faq.question}",
                    f"Ответ: {faq.answer}",
                    f"Категория: {faq.category}",
                    f"Теги: {tags or '-'}",
                    f"Релевантность: {score}",
                ]
            )
        )
    return "\n\n".join(lines)


def generate_answer_with_openai(
    question: str,
    matches: list[tuple[FAQ, float]],
) -> str | None:
    if not openai_is_available():
        return None

    context = _build_context_block(matches)
    client = OpenAI(api_key=settings.openai_api_key)

    system_prompt = (
        "Ты AI.Sulu, цифровой ассистент университета. "
        "Отвечай только на основе предоставленного контекста базы знаний. "
        "Если контекста недостаточно, верни только строку __FALLBACK__."
    )

    user_prompt = (
        f"Контекст базы знаний:\n{context or 'Контекст не найден.'}\n\n"
        f"Вопрос пользователя: {question}\n\n"
        "Сформулируй вежливый, краткий, полезный ответ на русском языке."
    )

    try:
        completion = client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        answer = (completion.choices[0].message.content or "").strip()
        if not answer or "__FALLBACK__" in answer:
            return None
        return answer
    except Exception:
        return None
