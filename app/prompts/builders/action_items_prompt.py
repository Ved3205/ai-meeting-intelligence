"""
Action Items Prompt Builder

Creates prompts for extracting meeting action items.
"""

from app.models.prompt_request import PromptRequest

from app.prompts.builders.prompt_builder import PromptBuilder

from app.prompts.formatter.prompt_formatter import (
    PromptFormatter,
)


class ActionItemsPrompt(PromptBuilder):
    """
    Prompt builder responsible for extracting
    action items from a meeting transcript.
    """

    def build(
        self,
        request: PromptRequest,
    ) -> str:

        if not request.transcript:

            raise ValueError(
                "Transcript is required."
            )

        transcript = (
            PromptFormatter.format_transcript(
                request.transcript
            )
        )

        metadata = (
            PromptFormatter.format_metadata(
                request.metadata
            )
        )

        return f"""
You are an expert AI Meeting Assistant.

Your job is to identify EVERY actionable task discussed
during the meeting.

For EACH action item extract:

1. Owner
2. Task
3. Deadline
4. Priority
5. Supporting Evidence

Rules

- Do NOT invent information.
- If the owner is unknown, write "Unknown".
- If the deadline is missing, write "Not Mentioned".
- If priority cannot be inferred, write "Medium".
- Output in Markdown.

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

## Action Item 1

Owner:

Task:

Deadline:

Priority:

Evidence:


## Action Item 2

Owner:

Task:

Deadline:

Priority:

Evidence:

Begin.
"""