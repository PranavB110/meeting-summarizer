"""Abstract interface every LLM (summarization) provider must implement."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SummaryResult:
    summary: str
    key_decisions: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)


class LLMProvider(ABC):
    """All LLM backends (local or cloud) implement this single method."""

    @abstractmethod
    def summarize(self, transcript: str) -> SummaryResult:
        ...