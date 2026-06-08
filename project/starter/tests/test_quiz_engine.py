"""Tests for the quiz_engine module.

This module verifies the core quiz logic by mocking the UI layer to
simulate user interaction. It tests the quiz loop, session statistics,
correct/incorrect tracking, and integration with different strategies.
"""

from typing import List
from unittest.mock import MagicMock, call, patch

import pytest

from flashcard_quizzer.models import Deck, Flashcard
from flashcard_quizzer.quiz_engine import QuizEngine, SessionStats
from flashcard_quizzer.quiz_modes import (
    AdaptiveStrategy,
    RandomStrategy,
    SequentialStrategy,
)


class MockUI:
    """Mock UI implementation for testing the quiz engine.

    This mock records all method calls and provides predetermined
    answers for the get_answer method.

    Attributes:
        answers: A list of answers to return sequentially from get_answer.
        calls: A list recording all method calls made to this mock.
    """

    def __init__(self, answers: List[str]) -> None:
        """Initialize with a list of predetermined answers.

        Args:
            answers: Answers to return in order from get_answer().
        """
        self.answers: List[str] = list(answers)
        self._answer_index: int = 0
        self.calls: List[tuple] = []
        self.welcome_called: bool = False
        self.stats_called: bool = False
        self.last_stats: dict = {}

    def display_welcome(self, deck_name: str, card_count: int, mode: str) -> None:
        """Record the welcome display call."""
        self.welcome_called = True
        self.calls.append(("display_welcome", deck_name, card_count, mode))

    def display_card(self, card_number: int, total_cards: int, front: str) -> None:
        """Record the card display call."""
        self.calls.append(("display_card", card_number, total_cards, front))

    def get_answer(self) -> str:
        """Return the next predetermined answer.

        Returns:
            The next answer from the answers list, or empty string if exhausted.
        """
        if self._answer_index < len(self.answers):
            answer = self.answers[self._answer_index]
            self._answer_index += 1
            return answer
        return ""

    def display_correct(self, answer: str) -> None:
        """Record the correct feedback call."""
        self.calls.append(("display_correct", answer))

    def display_incorrect(self, user_answer: str, correct_answer: str) -> None:
        """Record the incorrect feedback call."""
        self.calls.append(("display_incorrect", user_answer, correct_answer))

    def display_stats(
        self,
        total_questions: int,
        correct_count: int,
        accuracy: float,
        missed_terms: List[str],
    ) -> None:
        """Record the stats display call."""
        self.stats_called = True
        self.last_stats = {
            "total_questions": total_questions,
            "correct_count": correct_count,
            "accuracy": accuracy,
            "missed_terms": missed_terms,
        }
        self.calls.append(
            ("display_stats", total_questions, correct_count, accuracy, missed_terms)
        )

    def display_message(self, message: str) -> None:
        """Record the message display call."""
        self.calls.append(("display_message", message))

    def display_error(self, message: str) -> None:
        """Record the error display call."""
        self.calls.append(("display_error", message))


def make_test_deck() -> Deck:
    """Create a test deck with 3 flashcards.

    Returns:
        A Deck with 3 cards for testing.
    """
    return Deck(
        name="Test Deck",
        cards=[
            Flashcard(front="What is 2+2?", back="4"),
            Flashcard(front="Capital of France?", back="Paris"),
            Flashcard(front="Color of the sky?", back="Blue"),
        ],
    )


class TestSessionStats:
    """Tests for the SessionStats dataclass."""

    def test_initial_state(self) -> None:
        """A new SessionStats should have zero counts and empty missed terms."""
        stats = SessionStats()
        assert stats.total_questions == 0
        assert stats.correct_count == 0
        assert stats.incorrect_count == 0
        assert stats.missed_terms == []

    def test_accuracy_with_no_questions(self) -> None:
        """Accuracy should be 0.0 when no questions have been asked."""
        stats = SessionStats()
        assert stats.accuracy == 0.0

    def test_accuracy_calculation(self) -> None:
        """Accuracy should be correctly calculated as a percentage."""
        stats = SessionStats(total_questions=10, correct_count=7)
        assert stats.accuracy == 70.0

    def test_perfect_accuracy(self) -> None:
        """Accuracy should be 100.0 when all answers are correct."""
        stats = SessionStats(total_questions=5, correct_count=5)
        assert stats.accuracy == 100.0

    def test_zero_accuracy(self) -> None:
        """Accuracy should be 0.0 when no answers are correct."""
        stats = SessionStats(total_questions=5, correct_count=0)
        assert stats.accuracy == 0.0

    def test_incorrect_count(self) -> None:
        """Incorrect count should be total minus correct."""
        stats = SessionStats(total_questions=10, correct_count=6)
        assert stats.incorrect_count == 4


class TestQuizEngineAllCorrect:
    """Tests for QuizEngine when all answers are correct."""

    def test_all_correct_answers(self) -> None:
        """All correct answers should yield 100% accuracy."""
        deck = make_test_deck()
        strategy = SequentialStrategy()
        ui = MockUI(answers=["4", "Paris", "Blue"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        assert stats.total_questions == 3
        assert stats.correct_count == 3
        assert stats.accuracy == 100.0
        assert stats.missed_terms == []

    def test_welcome_displayed(self) -> None:
        """The welcome message should be displayed at session start."""
        deck = make_test_deck()
        strategy = SequentialStrategy()
        ui = MockUI(answers=["4", "Paris", "Blue"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        engine.run()

        assert ui.welcome_called is True

    def test_stats_displayed(self) -> None:
        """The session stats should be displayed at session end."""
        deck = make_test_deck()
        strategy = SequentialStrategy()
        ui = MockUI(answers=["4", "Paris", "Blue"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        engine.run()

        assert ui.stats_called is True
        assert ui.last_stats["total_questions"] == 3
        assert ui.last_stats["correct_count"] == 3
        assert ui.last_stats["accuracy"] == 100.0
        assert ui.last_stats["missed_terms"] == []

    def test_correct_feedback_shown(self) -> None:
        """Correct feedback should be shown for each correct answer."""
        deck = make_test_deck()
        strategy = SequentialStrategy()
        ui = MockUI(answers=["4", "Paris", "Blue"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        engine.run()

        correct_calls = [c for c in ui.calls if c[0] == "display_correct"]
        assert len(correct_calls) == 3


class TestQuizEngineAllIncorrect:
    """Tests for QuizEngine when all answers are incorrect."""

    def test_all_incorrect_answers(self) -> None:
        """All incorrect answers should yield 0% accuracy."""
        deck = make_test_deck()
        strategy = SequentialStrategy()
        ui = MockUI(answers=["wrong", "wrong", "wrong"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        assert stats.total_questions == 3
        assert stats.correct_count == 0
        assert stats.accuracy == 0.0

    def test_missed_terms_tracked(self) -> None:
        """All missed card fronts should appear in missed_terms."""
        deck = make_test_deck()
        strategy = SequentialStrategy()
        ui = MockUI(answers=["wrong", "wrong", "wrong"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        assert "What is 2+2?" in stats.missed_terms
        assert "Capital of France?" in stats.missed_terms
        assert "Color of the sky?" in stats.missed_terms

    def test_incorrect_feedback_shown(self) -> None:
        """Incorrect feedback should be shown for each wrong answer."""
        deck = make_test_deck()
        strategy = SequentialStrategy()
        ui = MockUI(answers=["wrong", "wrong", "wrong"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        engine.run()

        incorrect_calls = [c for c in ui.calls if c[0] == "display_incorrect"]
        assert len(incorrect_calls) == 3


class TestQuizEngineMixedAnswers:
    """Tests for QuizEngine with a mix of correct and incorrect answers."""

    def test_mixed_results(self) -> None:
        """Mixed answers should yield correct accuracy and missed terms."""
        deck = make_test_deck()
        strategy = SequentialStrategy()
        # Correct: "4", Incorrect: "London", Correct: "Blue"
        ui = MockUI(answers=["4", "London", "Blue"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        assert stats.total_questions == 3
        assert stats.correct_count == 2
        assert stats.incorrect_count == 1
        assert abs(stats.accuracy - 66.7) < 0.1
        assert "Capital of France?" in stats.missed_terms
        assert "What is 2+2?" not in stats.missed_terms

    def test_case_insensitive_matching(self) -> None:
        """Answers should be matched case-insensitively."""
        deck = make_test_deck()
        strategy = SequentialStrategy()
        ui = MockUI(answers=["4", "paris", "BLUE"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        assert stats.correct_count == 3
        assert stats.accuracy == 100.0


class TestQuizEngineWithRandomStrategy:
    """Tests for QuizEngine using the RandomStrategy."""

    def test_all_cards_presented(self) -> None:
        """All cards should be presented regardless of random order."""
        deck = make_test_deck()
        strategy = RandomStrategy(seed=42)
        # Provide enough answers for all cards
        ui = MockUI(answers=["4", "Paris", "Blue", "4", "Paris", "Blue"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        assert stats.total_questions == 3

    def test_cards_displayed_in_ui(self) -> None:
        """Each card should trigger a display_card call."""
        deck = make_test_deck()
        strategy = RandomStrategy(seed=42)
        ui = MockUI(answers=["wrong", "wrong", "wrong"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        engine.run()

        card_calls = [c for c in ui.calls if c[0] == "display_card"]
        assert len(card_calls) == 3


class TestQuizEngineWithAdaptiveStrategy:
    """Tests for QuizEngine using the AdaptiveStrategy."""

    def test_missed_cards_repeated(self) -> None:
        """Missed cards should be presented again in the second pass."""
        deck = Deck(
            name="Small Deck",
            cards=[
                Flashcard(front="Q1", back="A1"),
                Flashcard(front="Q2", back="A2"),
            ],
        )
        strategy = AdaptiveStrategy(seed=42)
        # First pass: miss both, Second pass: get both correct
        ui = MockUI(answers=["wrong", "wrong", "A1", "A2"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        # 2 first pass + 2 second pass = 4 total questions
        assert stats.total_questions == 4

    def test_no_repeat_if_all_correct(self) -> None:
        """If all correct on first pass, no second pass occurs."""
        deck = Deck(
            name="Small Deck",
            cards=[
                Flashcard(front="Q1", back="A1"),
                Flashcard(front="Q2", back="A2"),
            ],
        )
        strategy = AdaptiveStrategy(seed=42)
        # With seed=42, order is Q2, Q1 so answers must match that order
        ui = MockUI(answers=["A2", "A1"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        assert stats.total_questions == 2
        assert stats.correct_count == 2


class TestQuizEngineEdgeCases:
    """Tests for edge cases in the QuizEngine."""

    def test_empty_answer_is_incorrect(self) -> None:
        """An empty answer should be treated as incorrect."""
        deck = Deck(
            name="Single Card",
            cards=[Flashcard(front="Q1", back="A1")],
        )
        strategy = SequentialStrategy()
        ui = MockUI(answers=[""])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        assert stats.correct_count == 0
        assert stats.incorrect_count == 1

    def test_whitespace_answer_matching(self) -> None:
        """Answers with extra whitespace should still match."""
        deck = Deck(
            name="Single Card",
            cards=[Flashcard(front="Q1", back="A1")],
        )
        strategy = SequentialStrategy()
        ui = MockUI(answers=["  A1  "])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        assert stats.correct_count == 1

    def test_mode_name_detection(self) -> None:
        """The engine should correctly detect the mode name from the strategy."""
        deck = make_test_deck()
        ui = MockUI(answers=["4", "Paris", "Blue"])

        engine_seq = QuizEngine(deck=deck, strategy=SequentialStrategy(), ui=ui)
        assert engine_seq._mode_name == "sequential"

        engine_rand = QuizEngine(deck=deck, strategy=RandomStrategy(), ui=ui)
        assert engine_rand._mode_name == "random"

        engine_adapt = QuizEngine(deck=deck, strategy=AdaptiveStrategy(), ui=ui)
        assert engine_adapt._mode_name == "adaptive"

    def test_missed_terms_not_duplicated(self) -> None:
        """A card missed multiple times should only appear once in missed_terms."""
        deck = Deck(
            name="Single Card",
            cards=[Flashcard(front="Q1", back="A1")],
        )
        strategy = AdaptiveStrategy(seed=42)
        # Miss on first pass, miss again on second pass
        ui = MockUI(answers=["wrong", "wrong"])

        engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)
        stats = engine.run()

        # Q1 should appear only once in missed_terms even though missed twice
        assert stats.missed_terms.count("Q1") == 1
