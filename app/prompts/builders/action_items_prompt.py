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

Your job is to identify EVERY action item in the meeting:
tasks someone agreed to do, was asked to do, or that the group
decided must happen (for example "I'll check...", "can you
work with...", "we need to...", "let's do that instead",
"I'll put it in the review").

For EACH action item extract:

- owner: the person responsible, or null if not stated
- description: one clear sentence describing the task
- deadline: the due date or time frame, or null if not stated

Rules

- Do NOT invent information.
- Only include things actually said in the transcript.
- Output ONLY a JSON array, no other text and no markdown fences.
- If there are no action items, output [].

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

[
  {{"owner": "Name or null", "description": "What must be done", "deadline": "When or null"}}
]

JSON array:
"""