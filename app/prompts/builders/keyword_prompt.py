"""
Keyword Prompt Builder

Generates prompts for extracting meeting keywords.
"""

from app.models.prompt_request import PromptRequest
from app.prompts.builders.prompt_builder import PromptBuilder
from app.prompts.formatter.prompt_formatter import PromptFormatter


class KeywordPrompt(PromptBuilder):
    """
    Extract important keywords from a meeting.
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

Your task is to identify the most important
keywords discussed during the meeting.

Rules

- Extract only meaningful keywords.
- Ignore filler words.
- Do not invent keywords.
- Merge similar words.
- Return at most 20 keywords.
- Sort by importance.

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

Output Format

## Keywords

- Authentication
- REST API
- JWT
- MongoDB
- Deployment

Begin.
"""