"""Picks the ASR provider based on config — this is the config-switchable part."""
from app.core.config import Settings
from app.providers.asr.base import ASRProvider
from app.providers.asr.faster_whisper_provider import FasterWhisperProvider


def get_asr_provider(settings: Settings) -> ASRProvider:
    if settings.asr_engine == "faster_whisper":
        return FasterWhisperProvider(model_size=settings.whisper_model_size)

    raise ValueError(f"Unknown ASR_ENGINE: {settings.asr_engine}")