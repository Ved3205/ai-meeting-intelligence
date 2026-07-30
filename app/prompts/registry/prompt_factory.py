"""
Prompt Factory

Responsible for creating prompt builders.
"""

from __future__ import annotations

from app.prompts.builders.qa_prompt import QAPrompt
from app.prompts.builders.summary_prompt import SummaryPrompt
# from app.prompts.builders.action_items_prompt import ActionItemsPrompt
# from app.prompts.keyword_prompt import KeywordPrompt
# from app.prompts.title_prompt import TitlePrompt


class PromptFactory:
    """
    Factory class for prompt builders.
    """

    _builders = {

        "qa": QAPrompt,
        "summary": SummaryPrompt,
        # "action_items": ActionItemsPrompt,
        # "keywords": KeywordPrompt,
        # "title": TitlePrompt,

    }

    @classmethod
    def get_builder(
        cls,
        prompt_type: str,
    ):

        prompt_type = prompt_type.lower()

        if prompt_type not in cls._builders:

            supported = ", ".join(cls._builders.keys())

            raise ValueError(

                f"Unknown prompt type '{prompt_type}'. "

                f"Supported types: {supported}"

            )

        return cls._builders[prompt_type]()