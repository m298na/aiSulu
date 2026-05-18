import json
from datetime import datetime

from app.config import get_settings


settings = get_settings()


def append_question_log(record: dict) -> None:
    serializable_record = {
        **record,
        "created_at": record.get("created_at", datetime.utcnow()).isoformat(),
    }
    with settings.questions_log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(serializable_record, ensure_ascii=False) + "\n")
