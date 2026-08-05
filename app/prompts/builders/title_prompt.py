"""
Meeting Title Prompt Builder
"""

from app.models.prompt_request import PromptRequest

from app.prompts.builders.prompt_builder import (
    PromptBuilder,
)

from app.prompts.formatter.prompt_formatter import (
    PromptFormatter,
)


class TitlePrompt(PromptBuilder):
    """
    Generates an informative meeting title.
    """

    def build(
        self,
        request: PromptRequest,
    ) -> str:

        if not request.transcript:

            raise ValueError(
                "Transcript is required."
            )

        transcript = PromptFormatter.format_transcript(
            request.transcript
        )

        metadata = PromptFormatter.format_metadata(
            request.metadata
        )

        return f"""
You are an expert AI Meeting Assistant.

Generate ONE concise title for this meeting.

Rules

- Maximum 10 words.
- No quotation marks.
- Do not use generic titles.
- Mention the main discussion topic.
- Do not invent information.

{self.separator()}

{PromptFormatter.section(
    "Meeting Metadata",
    metadata,
)}

{self.separator()}

{PromptFormatter.section(
    "Transcript",
    transcript,
)}

{self.separator()}

Return ONLY the title.

Begin.
"""