"""Tests for the quiz_modes module.

This module verifies the Strategy Pattern implementation for all quiz modes:
Sequential, Random, and Adaptive. It tests card selection logic, result
recording, reset behavior, and the factory function.
"""

from typing import List

import pytest

from flashcard_quizzer.models import Flashcard
from flashcard_quizzer.quiz_modes import (
    AdaptiveStrategy,
    QuizStrategy,
    RandomStrategy,
    SequentialStrategy,
    create_strategy,
)


def make_sample_cards() -> List[Flashcard]:
    """Create a sample list of flashcards for testing.

    Returns:
        A list of 5 flashcards with predictable content.
    """
    return [
        Flashcard(front="Q1", back="A1"),
        Flashcard(front="Q2", back="A2"),
        Flashcard(front="Q3", back="A3"),
        Flashcard(front="Q4", back="A4"),
        Flashcard(front="Q5", back="A5"),
    ]


class TestSequentialStrategy:
    """Tests for the SequentialStrategy class."""

    def test_presents_cards_in_order(self) -> None:
        """Cards should be presented in their original order."""
        cards = make_sample_cards()
        strategy = SequentialStrategy()
        strategy.initialize(cards)

        for i, expected_card in enumerate(cards):
            assert strategy.has_more_cards() is True
            card = strategy.select_next_card()
            assert card is not None
            assert card.front == expected_card.front
            assert card.back == expected_card.back

    def test_returns_none_when_exhausted(self) -> None:
        """Should return None after all cards have been presented."""
        cards = make_sample_cards()
        strategy = SequentialStrategy()
        strategy.initialize(cards)

        for _ in range(len(cards)):
            strategy.select_next_card()

        assert strategy.has_more_cards() is False
        assert strategy.select_next_card() is None

    def test_reset_restarts_from_beginning(self) -> None:
        """After reset, cards should be presented from the start again."""
        cards = make_sample_cards()
        strategy = SequentialStrategy()
        strategy.initialize(cards)

        # Go through half the cards
        strategy.select_next_card()
        strategy.select_next_card()

        # Reset
        strategy.reset()

        # Should start from the beginning
        card = strategy.select_next_card()
        assert card is not None
        assert card.front == "Q1"

    def test_record_result_is_noop(self) -> None:
        """Recording results should not affect sequential ordering."""
        cards = make_sample_cards()
        strategy = SequentialStrategy()
        strategy.initialize(cards)

        card = strategy.select_next_card()
        assert card is not None
        strategy.record_result(card, correct=False)

        # Next card should still be Q2, unaffected by the result
        next_card = strategy.select_next_card()
        assert next_card is not None
        assert next_card.front == "Q2"

    def test_empty_card_list(self) -> None:
        """An empty card list should immediately return None."""
        strategy = SequentialStrategy()
        strategy.initialize([])

        assert strategy.has_more_cards() is False
        assert strategy.select_next_card() is None

    def test_does_not_mutate_original_list(self) -> None:
        """The strategy should work on a copy, not mutate the input."""
        cards = make_sample_cards()
        original_length = len(cards)
        strategy = SequentialStrategy()
        strategy.initialize(cards)

        # Exhaust the strategy
        while strategy.has_more_cards():
            strategy.select_next_card()

        assert len(cards) == original_length


class TestRandomStrategy:
    """Tests for the RandomStrategy class."""

    def test_presents_all_cards_exactly_once(self) -> None:
        """All cards should be presented exactly once, regardless of order."""
        cards = make_sample_cards()
        strategy = RandomStrategy(seed=42)
        strategy.initialize(cards)

        presented = []
        while strategy.has_more_cards():
            card = strategy.select_next_card()
            assert card is not None
            presented.append(card)

        assert len(presented) == len(cards)
        # All original cards should be present (by content)
        presented_fronts = {c.front for c in presented}
        expected_fronts = {c.front for c in cards}
        assert presented_fronts == expected_fronts

    def test_order_differs_from_sequential(self) -> None:
        """With a seed, the random order should differ from sequential."""
        cards = make_sample_cards()
        strategy = RandomStrategy(seed=42)
        strategy.initialize(cards)

        presented = []
        while strategy.has_more_cards():
            card = strategy.select_next_card()
            presented.append(card)

        # With seed=42 and 5 cards, the order should differ from original
        # (statistically almost certain with any seed)
        original_fronts = [c.front for c in cards]
        presented_fronts = [c.front for c in presented]
        # At least one card should be in a different position
        assert presented_fronts != original_fronts or len(cards) <= 1

    def test_reproducible_with_seed(self) -> None:
        """Same seed should produce the same order."""
        cards = make_sample_cards()

        strategy1 = RandomStrategy(seed=123)
        strategy1.initialize(cards)
        order1 = []
        while strategy1.has_more_cards():
            order1.append(strategy1.select_next_card())

        strategy2 = RandomStrategy(seed=123)
        strategy2.initialize(cards)
        order2 = []
        while strategy2.has_more_cards():
            order2.append(strategy2.select_next_card())

        for c1, c2 in zip(order1, order2):
            assert c1 is not None and c2 is not None
            assert c1.front == c2.front

    def test_returns_none_when_exhausted(self) -> None:
        """Should return None after all cards have been presented."""
        cards = make_sample_cards()
        strategy = RandomStrategy(seed=42)
        strategy.initialize(cards)

        for _ in range(len(cards)):
            strategy.select_next_card()

        assert strategy.has_more_cards() is False
        assert strategy.select_next_card() is None

    def test_reset_allows_full_replay(self) -> None:
        """After reset, all cards should be available again."""
        cards = make_sample_cards()
        strategy = RandomStrategy(seed=42)
        strategy.initialize(cards)

        # Exhaust all cards
        first_run = []
        while strategy.has_more_cards():
            card = strategy.select_next_card()
            assert card is not None
            first_run.append(card)

        assert strategy.select_next_card() is None

        # Reset and verify all cards are available again
        strategy.reset()
        second_run = []
        while strategy.has_more_cards():
            card = strategy.select_next_card()
            assert card is not None
            second_run.append(card)

        assert len(second_run) == len(cards)
        assert {c.front for c in second_run} == {c.front for c in cards}

    def test_record_result_is_noop(self) -> None:
        """Recording results should not affect random ordering."""
        cards = make_sample_cards()
        strategy = RandomStrategy(seed=42)
        strategy.initialize(cards)

        card = strategy.select_next_card()
        assert card is not None
        strategy.record_result(card, correct=False)

        # Should still have remaining cards
        assert strategy.has_more_cards() is True


class TestAdaptiveStrategy:
    """Tests for the AdaptiveStrategy class."""

    def test_first_pass_presents_all_cards(self) -> None:
        """The first pass should present all cards exactly once."""
        cards = make_sample_cards()
        strategy = AdaptiveStrategy(seed=42)
        strategy.initialize(cards)

        presented = []
        # Present all cards in first pass, marking all correct
        for _ in range(len(cards)):
            card = strategy.select_next_card()
            assert card is not None
            presented.append(card)
            strategy.record_result(card, correct=True)

        presented_fronts = {c.front for c in presented}
        expected_fronts = {c.front for c in cards}
        assert presented_fronts == expected_fronts

    def test_no_second_pass_if_all_correct(self) -> None:
        """If all cards are correct, no second pass should occur."""
        cards = make_sample_cards()
        strategy = AdaptiveStrategy(seed=42)
        strategy.initialize(cards)

        for _ in range(len(cards)):
            card = strategy.select_next_card()
            assert card is not None
            strategy.record_result(card, correct=True)

        # Should be done now
        assert strategy.select_next_card() is None
        assert strategy.has_more_cards() is False

    def test_missed_cards_are_repeated(self) -> None:
        """Cards answered incorrectly should appear in the second pass."""
        cards = make_sample_cards()
        strategy = AdaptiveStrategy(seed=42)
        strategy.initialize(cards)

        missed_fronts = set()
        # First pass: mark some cards as incorrect
        for i in range(len(cards)):
            card = strategy.select_next_card()
            assert card is not None
            if i % 2 == 0:  # Miss every other card
                strategy.record_result(card, correct=False)
                missed_fronts.add(card.front)
            else:
                strategy.record_result(card, correct=True)

        # Second pass: should only contain missed cards
        second_pass_fronts = set()
        while True:
            card = strategy.select_next_card()
            if card is None:
                break
            second_pass_fronts.add(card.front)
            strategy.record_result(card, correct=True)

        assert second_pass_fronts == missed_fronts

    def test_second_pass_only_contains_missed(self) -> None:
        """The second pass should not contain correctly answered cards."""
        cards = make_sample_cards()
        strategy = AdaptiveStrategy(seed=42)
        strategy.initialize(cards)

        # First pass: only miss Q1 and Q3
        correct_fronts = set()
        for _ in range(len(cards)):
            card = strategy.select_next_card()
            assert card is not None
            if card.front in ("Q1", "Q3"):
                strategy.record_result(card, correct=False)
            else:
                strategy.record_result(card, correct=True)
                correct_fronts.add(card.front)

        # Second pass
        second_pass = []
        while True:
            card = strategy.select_next_card()
            if card is None:
                break
            second_pass.append(card)
            strategy.record_result(card, correct=True)

        # Verify no correctly answered cards appear in second pass
        for card in second_pass:
            assert card.front not in correct_fronts

    def test_total_cards_presented_with_misses(self) -> None:
        """Total presentations should equal N + number of missed cards."""
        cards = make_sample_cards()
        strategy = AdaptiveStrategy(seed=42)
        strategy.initialize(cards)

        total_presented = 0
        missed_count = 0

        # First pass
        for i in range(len(cards)):
            card = strategy.select_next_card()
            assert card is not None
            total_presented += 1
            if i < 2:  # Miss first 2 cards
                strategy.record_result(card, correct=False)
                missed_count += 1
            else:
                strategy.record_result(card, correct=True)

        # Second pass
        while True:
            card = strategy.select_next_card()
            if card is None:
                break
            total_presented += 1
            strategy.record_result(card, correct=True)

        assert total_presented == len(cards) + missed_count

    def test_reset_clears_missed_cards(self) -> None:
        """After reset, missed cards should be cleared."""
        cards = make_sample_cards()
        strategy = AdaptiveStrategy(seed=42)
        strategy.initialize(cards)

        # First pass with all incorrect
        for _ in range(len(cards)):
            card = strategy.select_next_card()
            assert card is not None
            strategy.record_result(card, correct=False)

        # Reset
        strategy.reset()

        # Now do a pass with all correct
        for _ in range(len(cards)):
            card = strategy.select_next_card()
            assert card is not None
            strategy.record_result(card, correct=True)

        # Should have no second pass
        assert strategy.select_next_card() is None

    def test_has_more_cards_during_transition(self) -> None:
        """has_more_cards should be True during the transition to second pass."""
        cards = [Flashcard(front="Q1", back="A1")]
        strategy = AdaptiveStrategy(seed=42)
        strategy.initialize(cards)

        card = strategy.select_next_card()
        assert card is not None
        strategy.record_result(card, correct=False)

        # After first pass exhausted but missed cards exist
        assert strategy.has_more_cards() is True


class TestCreateStrategy:
    """Tests for the create_strategy factory function."""

    def test_create_sequential(self) -> None:
        """Should create a SequentialStrategy instance."""
        strategy = create_strategy("sequential")
        assert isinstance(strategy, SequentialStrategy)

    def test_create_random(self) -> None:
        """Should create a RandomStrategy instance."""
        strategy = create_strategy("random")
        assert isinstance(strategy, RandomStrategy)

    def test_create_adaptive(self) -> None:
        """Should create an AdaptiveStrategy instance."""
        strategy = create_strategy("adaptive")
        assert isinstance(strategy, AdaptiveStrategy)

    def test_case_insensitive(self) -> None:
        """Mode names should be case-insensitive."""
        assert isinstance(create_strategy("Sequential"), SequentialStrategy)
        assert isinstance(create_strategy("RANDOM"), RandomStrategy)
        assert isinstance(create_strategy("Adaptive"), AdaptiveStrategy)

    def test_strips_whitespace(self) -> None:
        """Mode names with leading/trailing whitespace should work."""
        assert isinstance(create_strategy("  sequential  "), SequentialStrategy)

    def test_invalid_mode_raises_error(self) -> None:
        """An unrecognized mode name should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown quiz mode"):
            create_strategy("nonexistent")

    def test_random_with_seed(self) -> None:
        """Creating a random strategy with a seed should work."""
        strategy = create_strategy("random", seed=42)
        assert isinstance(strategy, RandomStrategy)

    def test_adaptive_with_seed(self) -> None:
        """Creating an adaptive strategy with a seed should work."""
        strategy = create_strategy("adaptive", seed=42)
        assert isinstance(strategy, AdaptiveStrategy)

    def test_all_strategies_implement_interface(self) -> None:
        """All strategies should be instances of QuizStrategy."""
        for mode in ["sequential", "random", "adaptive"]:
            strategy = create_strategy(mode)
            assert isinstance(strategy, QuizStrategy)
