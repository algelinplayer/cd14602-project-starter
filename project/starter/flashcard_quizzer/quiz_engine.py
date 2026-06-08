"""Quiz engine module for the Flashcard Quizzer application.

This module contains the core quiz logic that orchestrates a quiz session.
It ties together the data layer (Deck/Flashcard models), the strategy layer
(quiz modes), and the presentation layer (UI) to run an interactive
flashcard quiz from start to finish.

The QuizEngine class manages session state including correct/incorrect
counts and missed terms, delegating card selection to the active strategy
and user interaction to the UI component.
"""

from dataclasses import dataclass, field
from typing import List

from flashcard_quizzer.models import Deck, Flashcard
from flashcard_quizzer.quiz_modes import QuizStrategy
from flashcard_quizzer.ui import UIProtocol


@dataclass
class SessionStats:
    """Tracks statistics for a single quiz session.

    Attributes:
        total_questions: The total number of questions asked.
        correct_count: The number of correctly answered questions.
        missed_terms: A list of card fronts that were answered incorrectly.
    """

    total_questions: int = 0
    correct_count: int = 0
    missed_terms: List[str] = field(default_factory=list)

    @property
    def incorrect_count(self) -> int:
        """Return the number of incorrect answers.

        Returns:
            The difference between total questions and correct answers.
        """
        return self.total_questions - self.correct_count

    @property
    def accuracy(self) -> float:
        """Calculate the accuracy percentage for the session.

        Returns:
            The percentage of correct answers (0.0 to 100.0).
            Returns 0.0 if no questions have been asked.
        """
        if self.total_questions == 0:
            return 0.0
        return (self.correct_count / self.total_questions) * 100.0


class QuizEngine:
    """Orchestrates a flashcard quiz session.

    The QuizEngine connects the deck of flashcards, the quiz mode strategy,
    and the user interface to run an interactive quiz. It manages the session
    lifecycle: initialization, the question-answer loop, and result reporting.

    Attributes:
        deck: The flashcard deck being quizzed.
        strategy: The quiz mode strategy controlling card selection.
        ui: The user interface for displaying content and collecting input.
        stats: The session statistics tracker.
    """

    def __init__(
        self, deck: Deck, strategy: QuizStrategy, ui: UIProtocol
    ) -> None:
        """Initialize the quiz engine with its dependencies.

        Args:
            deck: The flashcard deck to quiz from.
            strategy: The strategy determining card selection order.
            ui: The user interface for interaction.
        """
        self.deck: Deck = deck
        self.strategy: QuizStrategy = strategy
        self.ui: UIProtocol = ui
        self.stats: SessionStats = SessionStats()
        self._mode_name: str = self._get_mode_name()

    def _get_mode_name(self) -> str:
        """Determine the mode name from the strategy class name.

        Returns:
            A human-readable mode name derived from the strategy class.
        """
        class_name = type(self.strategy).__name__
        return class_name.replace("Strategy", "").lower()

    def run(self) -> SessionStats:
        """Execute the full quiz session from start to finish.

        This method initializes the strategy, displays the welcome message,
        runs the question-answer loop, and displays the final statistics.

        Returns:
            The SessionStats object containing the session results.
        """
        self._initialize_session()
        self._run_quiz_loop()
        self._display_results()
        return self.stats

    def _initialize_session(self) -> None:
        """Set up the session by initializing the strategy and resetting stats."""
        self.stats = SessionStats()
        self.strategy.initialize(self.deck.cards)
        self.ui.display_welcome(self.deck.name, self.deck.size, self._mode_name)

    def _run_quiz_loop(self) -> None:
        """Execute the main question-answer loop.

        Iterates through cards provided by the strategy, presenting each
        to the user and recording their response. Continues until the
        strategy indicates no more cards are available.
        """
        card_number = 0

        while True:
            card = self.strategy.select_next_card()
            if card is None:
                break

            card_number += 1
            self._present_card(card, card_number)

    def _present_card(self, card: Flashcard, card_number: int) -> None:
        """Present a single flashcard and process the user's answer.

        Args:
            card: The flashcard to present.
            card_number: The sequential number of this card in the session.
        """
        self.ui.display_card(card_number, self.deck.size, card.front)
        user_answer = self.ui.get_answer()

        is_correct = card.check_answer(user_answer)
        self.stats.total_questions += 1

        if is_correct:
            self.stats.correct_count += 1
            self.ui.display_correct(card.back)
        else:
            self.ui.display_incorrect(user_answer, card.back)
            if card.front not in self.stats.missed_terms:
                self.stats.missed_terms.append(card.front)

        self.strategy.record_result(card, is_correct)

    def _display_results(self) -> None:
        """Display the final session statistics through the UI."""
        self.ui.display_stats(
            total_questions=self.stats.total_questions,
            correct_count=self.stats.correct_count,
            accuracy=self.stats.accuracy,
            missed_terms=self.stats.missed_terms,
        )
