"""Cloud LLM summarization via Groq (free tier, no local compute needed)."""
import json

from groq import Groq

from app.providers.llm.base import LLMProvider, SummaryResult
from app.providers.llm.prompts import SUMMARIZATION_SYSTEM_PROMPT, build_summarization_prompt


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.client = Groq(api_key=api_key)
        self.model = model

    def summarize(self, transcript: str) -> SummaryResult:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SUMMARIZATION_SYSTEM_PROMPT},
                {"role": "user", "content": build_summarization_prompt(transcript)},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        data = json.loads(raw)

        return SummaryResult(
            summary=data.get("summary", ""),
            key_decisions=data.get("key_decisions", []),
            action_items=data.get("action_items", []),
        )