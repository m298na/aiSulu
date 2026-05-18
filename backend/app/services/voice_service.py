from fastapi import UploadFile

from app.config import get_settings


settings = get_settings()


async def transcribe_audio(file: UploadFile | None) -> tuple[str, str, bool]:
    if settings.use_mock_services or settings.whisper_provider == "mock":
        transcript = (
            f"Mock transcript for {file.filename}"
            if file is not None
            else "Mock transcript: Расскажите о приемной комиссии или расписании."
        )
        return transcript, "mock-whisper", True

    transcript = (
        "Speech-to-text provider is configured, but production transcription flow "
        "should be connected here with Whisper or another STT service."
    )
    return transcript, settings.whisper_provider, False


def synthesize_speech(text: str) -> tuple[str, bool, str | None, str]:
    if settings.use_mock_services or settings.tts_provider == "mock":
        return (
            "mock-tts",
            True,
            None,
            f"Mock TTS prepared for text: {text[:120]}",
        )

    return (
        settings.tts_provider,
        False,
        None,
        "TTS provider is configured, but audio generation should be connected here "
        "with ElevenLabs or Azure TTS.",
    )
