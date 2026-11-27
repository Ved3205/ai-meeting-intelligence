"""
Question Answer Prompt
"""

from app.models.prompt_request import PromptRequest
from app.prompts.builders.prompt_builder import PromptBuilder
from app.prompts.formatter.prompt_formatter import PromptFormatter


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

Answer using the provided meeting context.

The context is excerpts of a meeting transcript.
For broad or vague questions (for example "what was discussed"),
summarize what the excerpts cover.
Combine details across excerpts and answer concisely.
The transcript has no speaker labels.
If asked what a person said, use the excerpts that mention
or introduce that person and say what is known about them.
Explain the answer in your own words and never mention IDs.
Do not use outside knowledge.

Only if the excerpts have nothing related to the question,
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