from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FAQBase(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    answer: str = Field(..., min_length=3)
    category: str = Field(default="general", max_length=100)
    tags: list[str] = Field(default_factory=list)
    source: str = Field(default="manual", max_length=255)
    is_active: bool = True


class FAQCreate(FAQBase):
    pass


class FAQUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=3, max_length=500)
    answer: str | None = Field(default=None, min_length=3)
    category: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = None
    source: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class FAQRead(FAQBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[FAQRead]


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    session_id: str | None = Field(default=None, max_length=64)
    input_mode: Literal["text", "voice"] = "text"


class ChatResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    source: str
    fallback_used: bool
    matched_faq_id: int | None = None
    matched_confidence: float = 0.0


class QuestionLogRead(BaseModel):
    id: int
    session_id: str
    question: str
    answer: str
    source: str
    input_mode: str
    matched_confidence: float
    fallback_used: bool
    created_at: datetime
    matched_faq_id: int | None = None

    model_config = {"from_attributes": True}


class LogsStatsResponse(BaseModel):
    total_questions: int
    fallback_count: int
    kb_answer_count: int
    openai_answer_count: int
    voice_questions_count: int


class AdminStatusResponse(BaseModel):
    app_name: str
    environment: str
    use_mock_services: bool
    faq_count: int
    questions_logged: int


class ReloadResponse(BaseModel):
    message: str
    faq_count: int


class TranscriptionResponse(BaseModel):
    transcript: str
    provider: str
    mock_mode: bool


class SpeechRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=1000)


class SpeechResponse(BaseModel):
    provider: str
    mock_mode: bool
    audio_url: str | None = None
    message: str
