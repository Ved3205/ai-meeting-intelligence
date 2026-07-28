"""
Base Prompt Builder

Defines the interface for all prompt builders.

Every prompt in the project should inherit from this class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class PromptBuilder(ABC):
    """
    Abstract base class for prompt builders.

    Every subclass must implement the build() method.
    """

    @abstractmethod
    def build(self, *args, **kwargs) -> str:
        """
        Build and return the final prompt.

        Returns
        -------
        str
            Prompt to send to the LLM.
        """
        raise NotImplementedError(
            "Prompt builders must implement build()."
        )

    @staticmethod
    def separator(length: int = 80) -> str:
        """
        Returns a separator line.

        Useful for making prompts readable.
        """

        return "=" * length

    @staticmethod
    def format_section(
        title: str,
        content: str,
    ) -> str:
        """
        Formats a section.

        Example

        QUESTION
        -----------------------
        What is RAG?

        """

        return (
            f"{title.upper()}\n"
            f"{'-' * len(title)}\n"
            f"{content.strip()}\n"
        )

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Normalize whitespace.

        Prevents prompts from containing
        unnecessary blank lines.
        """

        return " ".join(text.split())