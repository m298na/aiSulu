from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ChatRequest,
    ChatResponse,
    SpeechRequest,
    SpeechResponse,
    TranscriptionResponse,
)
from app.services.chat_service import answer_question
from app.services.voice_service import synthesize_speech, transcribe_audio


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
def ask_question(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return answer_question(db, payload)


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_question(
    file: UploadFile | None = File(default=None),
) -> TranscriptionResponse:
    transcript, provider, mock_mode = await transcribe_audio(file)
    return TranscriptionResponse(
        transcript=transcript,
        provider=provider,
        mock_mode=mock_mode,
    )


@router.post("/speak", response_model=SpeechResponse)
def speak_answer(payload: SpeechRequest) -> SpeechResponse:
    provider, mock_mode, audio_url, message = synthesize_speech(payload.text)
    return SpeechResponse(
        provider=provider,
        mock_mode=mock_mode,
        audio_url=audio_url,
        message=message,
    )
