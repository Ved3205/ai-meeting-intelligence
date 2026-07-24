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

        context = self._build_context(
            request.retrieved_chunks
        )

        prompt = self._build_prompt(
            request.question,
            context,
        )

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

    @staticmethod
    def _build_context(chunks):

        sections = []

        for chunk in chunks:

            sections.append(

                f"""
Chunk ID : {chunk.chunk_id}

Meeting : {chunk.meeting_id}

Timestamp : {chunk.start_time:.2f} - {chunk.end_time:.2f}

Content:
{chunk.text}
"""
            )

        return "\n\n".join(sections)

    @staticmethod
    def _build_prompt(
        question: str,
        context: str,
    ) -> str:

        return f"""
You are an AI Meeting Assistant.

Answer ONLY using the supplied meeting context.

If the answer is not present in the context,
reply exactly:

"I could not find that information in this meeting."

Meeting Context
====================

{context}

====================

Question

{question}

Answer:
"""