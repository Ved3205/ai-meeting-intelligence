"""
LLM Service

Generates final answers using retrieved context.
"""

import ollama

from app.config.settings import (
    LLM_MODEL,
    LLM_NUM_CTX,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
)

from app.models.llm_request import LLMRequest
from app.models.llm_response import LLMResponse
from app.models.prompt_request import PromptRequest

from app.prompts.registry.prompt_factory import PromptFactory


class LLMService:
    """
    Uses retrieved chunks to generate answers.
    """

    def __init__(self):

        self.model = LLM_MODEL
        self.client = ollama.Client(timeout=LLM_TIMEOUT_SECONDS)

    def generate_answer(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        builder = PromptFactory.get_builder("qa")

        prompt_request = PromptRequest(
            question=request.question,
            retrieved_chunks=request.retrieved_chunks,
        )

        prompt = builder.build(prompt_request)

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": LLM_TEMPERATURE,
                "num_ctx": LLM_NUM_CTX,
            },
        )

        answer =response["message"]["content"]

        source_chunks = [
            chunk.chunk_id
            for chunk in request.retrieved_chunks
        ]

        return LLMResponse(
            answer=answer,
            source_chunks=source_chunks,
        )

    def generate_from_prompt(
        self,
        prompt: str,
    ) -> str:
        """
        Generate an LLM response from an already-rendered prompt.

        This method is intended for specialized pipelines that construct
        their own prompts through PromptFactory, such as SummaryPipeline.
        Unlike generate_answer(), it does not rebuild the prompt through
        the QA prompt builder.
        """
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": LLM_TEMPERATURE,
                "num_ctx": LLM_NUM_CTX,
            },
        )

        return response["message"]["content"]