from openai import OpenAI
from src.core.exception import LLMError
import os
import logging
from src.llm.base import BaseLLM

logger = logging.getLogger(__name__)


class OpenAILLM(BaseLLM):

    DEFAULT_MODEL = ""

    def __init__(self,
                model_name : str | None = None,
                api_key : str | None = None,
                temperature : float | None = 1.0,
                max_token : int | None = None
                ):

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                f"Api key not found"
            ) 

        self.model = model_name or self.DEFAULT_MODEL
        self.api_key = api_key
        self.temperature = temperature
        self.max_token = max_token

        try:
            self.client = OpenAI(
                api_key = self.api_key
            )
        except:
            raise LLMError(
                f"Failed to initilize client for OpenAI"
            )

        logger.info("Model ready - model: %s",self.model)

    def generate(self,
                query : str
                ) -> str:
        if not query.strip():
            raise ValueError(
                f"Input Was None"
            )
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = [
                    {
                        "role" : "system",
                        "content" : "You are a rag chat bot "
                    },
                    {
                        "role" : "user",
                        "content" : query
                    }
                ],
                temperature = self.temperature,
                max_tokens = self.max_token
            )
            return response.choices[0].message.content
        except:
            raise LLMError(
                f"Failed to Generate output "
            )

