"""
Question Answer Prompt
"""

from app.models.prompt_request import PromptRequest
from app.prompts.prompt_builder import PromptBuilder
from app.prompts.prompt_formatter import PromptFormatter


class QAPrompt(PromptBuilder):

    def build(
        self,
        request: PromptRequest,
    ) -> str:

        if not request.question:

            raise ValueError(
                "Question is required."
            )

        if not request.retrieved_chunks:

            raise ValueError(
                "Retrieved chunks are required."
            )

        context = PromptFormatter.format_retrieved_chunks(
            request.retrieved_chunks
        )

        return f"""
You are an AI Meeting Assistant.

Answer ONLY using the provided meeting context.

If the answer is unavailable,
reply exactly:

"I could not find that information in this meeting."

{self.separator()}

{PromptFormatter.section(
    "Meeting Context",
    context,
)}

{self.separator()}

{PromptFormatter.section(
    "Question",
    request.question,
)}

Answer:
"""