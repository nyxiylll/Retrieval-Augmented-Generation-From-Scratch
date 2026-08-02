from abc import ABC, abstractmethod
from src.core.exception import LLMError
import os
import logging
from src.llm.base import BaseLLM
from groq import Groq

logger = logging.getLogger(__name__)


#primary Model 
class GroqLLM(BaseLLM):

    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ):

        key = api_key or os.environ.get("GROQ_API_KEY")

        if not key:
            raise LLMError(
                "GROQ_API_KEY not found. Set it in your .env file or pass api_key explicitly."
            )

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        try:
            self._client = Groq(api_key=key)
        except Exception as e:
            raise LLMError("Failed to initialize Groq client") from e

        logger.info("GroqLLM ready — model: %s", self.model)

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise LLMError("Prompt cannot be empty")

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role" : "system",
                    "content" : "You are a RAG Chatbot now act like one"
                },
                    {"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise LLMError(f"Groq API call failed: {e}") from e
