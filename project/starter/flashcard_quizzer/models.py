"""Domain models for the Flashcard Quizzer application.

This module defines the core data structures used throughout the application,
including the Flashcard and Deck classes. These models serve as the foundation
for data ingestion, quiz logic, and session tracking.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Flashcard:
    """Represents a single flashcard with a front (question) and back (answer).

    Attributes:
        front: The question or prompt displayed to the user.
        back: The correct answer to the question.
    """

    front: str
    back: str

    def check_answer(self, user_answer: str) -> bool:
        """Compare the user's answer to the correct answer (case-insensitive).

        Args:
            user_answer: The answer provided by the user.

        Returns:
            True if the answer matches (case-insensitive), False otherwise.
        """
        return user_answer.strip().lower() == self.back.strip().lower()


@dataclass
class Deck:
    """Represents a collection of flashcards loaded from a data source.

    Attributes:
        name: The name or title of the flashcard deck.
        cards: A list of Flashcard objects in this deck.
    """

    name: str
    cards: List[Flashcard] = field(default_factory=list)

    @property
    def size(self) -> int:
        """Return the number of cards in the deck.

        Returns:
            The total number of flashcards.
        """
        return len(self.cards)

    def is_empty(self) -> bool:
        """Check if the deck has no cards.

        Returns:
            True if the deck contains no flashcards, False otherwise.
        """
        return len(self.cards) == 0
