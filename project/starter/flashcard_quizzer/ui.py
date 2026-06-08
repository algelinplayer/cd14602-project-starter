"""Terminal user interface module for the Flashcard Quizzer.

This module handles all interaction with the user through the terminal,
including displaying flashcard prompts, collecting answers, showing
feedback, and presenting session statistics. It separates presentation
logic from business logic to maintain clean architecture.
"""

from typing import List, Protocol


class UIProtocol(Protocol):
    """Protocol defining the interface for user interaction.

    This protocol allows the quiz engine to interact with any UI
    implementation (terminal, GUI, or mock for testing) without
    tight coupling to a specific presentation layer.
    """

    def display_welcome(self, deck_name: str, card_count: int, mode: str) -> None:
        """Display the welcome message at the start of a quiz session."""
        ...

    def display_card(self, card_number: int, total_cards: int, front: str) -> None:
        """Display a flashcard's front (question) to the user."""
        ...

    def get_answer(self) -> str:
        """Prompt the user for their answer and return it."""
        ...

    def display_correct(self, answer: str) -> None:
        """Display feedback for a correct answer."""
        ...

    def display_incorrect(self, user_answer: str, correct_answer: str) -> None:
        """Display feedback for an incorrect answer."""
        ...

    def display_stats(
        self,
        total_questions: int,
        correct_count: int,
        accuracy: float,
        missed_terms: List[str],
    ) -> None:
        """Display the end-of-session statistics."""
        ...

    def display_message(self, message: str) -> None:
        """Display a general informational message."""
        ...

    def display_error(self, message: str) -> None:
        """Display an error message."""
        ...


class TerminalUI:
    """Concrete implementation of the UI for terminal-based interaction.

    This class handles formatting and displaying quiz content in the
    terminal, using ANSI-compatible text formatting for readability.
    """

    SEPARATOR = "-" * 50
    HEADER_SEPARATOR = "=" * 50

    def display_welcome(self, deck_name: str, card_count: int, mode: str) -> None:
        """Display the welcome banner with session information.

        Args:
            deck_name: The name of the flashcard deck being quizzed.
            card_count: The total number of cards in the deck.
            mode: The quiz mode being used (e.g., 'sequential', 'random').
        """
        print()
        print(self.HEADER_SEPARATOR)
        print(f"  FLASHCARD QUIZZER")
        print(self.HEADER_SEPARATOR)
        print(f"  Deck: {deck_name}")
        print(f"  Cards: {card_count}")
        print(f"  Mode: {mode.capitalize()}")
        print(self.HEADER_SEPARATOR)
        print()

    def display_card(self, card_number: int, total_cards: int, front: str) -> None:
        """Display the front of a flashcard with its position number.

        Args:
            card_number: The current card number in the session.
            total_cards: The total number of cards to be presented.
            front: The question text on the front of the card.
        """
        print(self.SEPARATOR)
        print(f"  Card {card_number}/{total_cards}")
        print(f"  Q: {front}")
        print()

    def get_answer(self) -> str:
        """Prompt the user for their answer via terminal input.

        Returns:
            The user's input string (stripped of leading/trailing whitespace).
        """
        try:
            answer = input("  Your answer: ")
            return answer.strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return ""

    def display_correct(self, answer: str) -> None:
        """Display positive feedback for a correct answer.

        Args:
            answer: The correct answer that was given.
        """
        print(f"  ✓ Correct! The answer is: {answer}")
        print()

    def display_incorrect(self, user_answer: str, correct_answer: str) -> None:
        """Display feedback for an incorrect answer, showing the correct one.

        Args:
            user_answer: The answer the user provided.
            correct_answer: The actual correct answer.
        """
        print(f"  ✗ Incorrect. You said: '{user_answer}'")
        print(f"    The correct answer is: {correct_answer}")
        print()

    def display_stats(
        self,
        total_questions: int,
        correct_count: int,
        accuracy: float,
        missed_terms: List[str],
    ) -> None:
        """Display the end-of-session statistics summary.

        Args:
            total_questions: Total number of questions asked.
            correct_count: Number of correct answers.
            accuracy: Accuracy percentage (0.0 to 100.0).
            missed_terms: List of terms (fronts) that were answered incorrectly.
        """
        print()
        print(self.HEADER_SEPARATOR)
        print("  SESSION RESULTS")
        print(self.HEADER_SEPARATOR)
        print(f"  Total Questions: {total_questions}")
        print(f"  Correct: {correct_count}")
        print(f"  Incorrect: {total_questions - correct_count}")
        print(f"  Accuracy: {accuracy:.1f}%")
        print()

        if missed_terms:
            print("  Missed Terms:")
            for term in missed_terms:
                print(f"    - {term}")
        else:
            print("  Perfect score! No missed terms.")

        print(self.HEADER_SEPARATOR)
        print()

    def display_message(self, message: str) -> None:
        """Display a general informational message.

        Args:
            message: The message text to display.
        """
        print(f"  {message}")

    def display_error(self, message: str) -> None:
        """Display an error message with a prefix indicator.

        Args:
            message: The error message text to display.
        """
        print(f"  ERROR: {message}")
