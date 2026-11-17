"""
LLM Service

Generates final answers using retrieved context.
"""

import ollama

from app.config.settings import (
    LLM_MODEL,
    LLM_TEMPERATURE,
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

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": LLM_TEMPERATURE,
            },
        )

        answer = response["message"]["content"]

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
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": LLM_TEMPERATURE,
            },
        )

        return response["message"]["content"]