"""Abstract interface every ASR (speech-to-text) provider must implement."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    text: str
    language: str | None = None
    duration_seconds: float | None = None


class ASRProvider(ABC):
    """All ASR backends (local or cloud) implement this single method."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        ...