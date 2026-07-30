"""
Meeting Summary Prompt
"""

from app.models.prompt_request import PromptRequest
from app.prompts.prompt_builder import PromptBuilder
from app.prompts.prompt_formatter import PromptFormatter


class SummaryPrompt(PromptBuilder):
    """
    Generates a concise meeting summary.
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
You are an expert meeting assistant.

Generate a professional meeting summary.

Your summary must contain exactly these sections.

1. Meeting Overview

2. Key Discussion Points

3. Important Decisions

4. Action Items

5. Risks / Blockers

6. Next Steps

Keep the summary concise.

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

Generate the summary.
"""