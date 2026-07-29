"""
Question Answer Prompt Builder
"""

from app.models.prompt_request import PromptRequest
from app.prompts.prompt_builder import PromptBuilder


class QAPrompt(PromptBuilder):
    """
    Builds prompts for question answering.
    """

    def build(
        self,
        request: PromptRequest,
    ) -> str:

        if not request.question:

            raise ValueError(
                "Question cannot be empty."
            )

        if not request.retrieved_chunks:

            raise ValueError(
                "No retrieved chunks provided."
            )

        context = self._build_context(
            request
        )

        prompt = f"""
You are an AI Meeting Assistant.

You must answer ONLY using the supplied meeting context.

If the answer is not contained in the context, reply exactly:

"I could not find that information in this meeting."

{self.separator()}

{self.format_section(
    "Meeting Context",
    context,
)}

{self.separator()}

{self.format_section(
    "Question",
    request.question,
)}

Answer:
"""

        return self.clean_text(prompt)

    def _build_context(
        self,
        request: PromptRequest,
    ) -> str:

        sections = []

        for chunk in request.retrieved_chunks:

            sections.append(
                f"""
Chunk ID : {chunk.chunk_id}

Meeting ID : {chunk.meeting_id}

Timestamp : {chunk.start_time:.2f} - {chunk.end_time:.2f}

Content:
{chunk.text}
"""
            )

        return "\n\n".join(sections)