"""Local, free ASR using faster-whisper (CTranslate2-optimized Whisper)."""
from faster_whisper import WhisperModel

from app.providers.asr.base import ASRProvider, TranscriptionResult


class FasterWhisperProvider(ASRProvider):
    def __init__(self, model_size: str = "base"):
        # compute_type="int8" keeps this runnable on CPU-only machines
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_path: str, language: str | None = None) -> TranscriptionResult:
        segments, info = self.model.transcribe(audio_path, beam_size=5, language=language)
        text = " ".join(segment.text.strip() for segment in segments)
        return TranscriptionResult(
            text=text.strip(),
            language=info.language,
            duration_seconds=info.duration,
        )