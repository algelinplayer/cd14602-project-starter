"""Quiz mode strategies for the Flashcard Quizzer application.

This module implements the Strategy Pattern to provide different algorithms
for selecting and ordering flashcards during a quiz session. Each strategy
encapsulates a distinct approach to card selection, allowing the quiz engine
to switch between modes without modifying its core logic.

Design Pattern: Strategy
- QuizStrategy (Abstract Base Class): Defines the interface for all modes.
- SequentialStrategy: Presents cards in their original order (1 to N).
- RandomStrategy: Shuffles the deck and presents cards in random order.
- AdaptiveStrategy: Prioritizes cards the user previously got wrong.
"""

import random
from abc import ABC, abstractmethod
from typing import List, Optional

from flashcard_quizzer.models import Flashcard


class QuizStrategy(ABC):
    """Abstract base class defining the interface for quiz mode strategies.

    All quiz modes must implement the `select_next_card` method and the
    `reset` method. The strategy maintains internal state to track which
    cards have been presented and manages the ordering logic.
    """

    @abstractmethod
    def initialize(self, cards: List[Flashcard]) -> None:
        """Prepare the strategy with the deck of cards for a new session.

        This method is called at the start of each quiz session to set up
        the internal state of the strategy.

        Args:
            cards: The list of flashcards to be used in this session.
        """
        pass

    @abstractmethod
    def select_next_card(self) -> Optional[Flashcard]:
        """Select and return the next flashcard to present to the user.

        Returns:
            The next Flashcard to display, or None if all cards have been
            presented and the session is complete.
        """
        pass

    @abstractmethod
    def record_result(self, card: Flashcard, correct: bool) -> None:
        """Record whether the user answered a card correctly.

        This information may be used by adaptive strategies to adjust
        future card selection.

        Args:
            card: The flashcard that was just answered.
            correct: True if the user answered correctly, False otherwise.
        """
        pass

    @abstractmethod
    def has_more_cards(self) -> bool:
        """Check if there are more cards to present in this session.

        Returns:
            True if there are remaining cards, False if the session is complete.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the strategy state for a new quiz session.

        Clears all internal tracking and prepares for a fresh start.
        """
        pass


class SequentialStrategy(QuizStrategy):
    """Presents flashcards in their original order from first to last.

    This is the simplest strategy, iterating through cards sequentially
    from index 0 to N-1. Each card is presented exactly once per session.
    """

    def __init__(self) -> None:
        """Initialize the sequential strategy with empty state."""
        self._cards: List[Flashcard] = []
        self._current_index: int = 0

    def initialize(self, cards: List[Flashcard]) -> None:
        """Set up the card list and reset the index to the beginning.

        Args:
            cards: The list of flashcards in their original order.
        """
        self._cards = list(cards)
        self._current_index = 0

    def select_next_card(self) -> Optional[Flashcard]:
        """Return the next card in sequential order.

        Returns:
            The next Flashcard, or None if all cards have been shown.
        """
        if self._current_index >= len(self._cards):
            return None
        card = self._cards[self._current_index]
        self._current_index += 1
        return card

    def record_result(self, card: Flashcard, correct: bool) -> None:
        """Record the result (no-op for sequential mode).

        Sequential mode does not adjust ordering based on results.

        Args:
            card: The flashcard that was answered.
            correct: Whether the answer was correct.
        """
        pass

    def has_more_cards(self) -> bool:
        """Check if there are remaining cards in the sequence.

        Returns:
            True if the current index has not reached the end.
        """
        return self._current_index < len(self._cards)

    def reset(self) -> None:
        """Reset the index to the beginning of the sequence."""
        self._current_index = 0


class RandomStrategy(QuizStrategy):
    """Presents flashcards in a shuffled random order.

    The deck is shuffled at initialization, and each card is presented
    exactly once per session in the randomized order.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """Initialize the random strategy.

        Args:
            seed: Optional random seed for reproducible shuffling (useful
                for testing). If None, shuffling is non-deterministic.
        """
        self._cards: List[Flashcard] = []
        self._current_index: int = 0
        self._seed: Optional[int] = seed

    def initialize(self, cards: List[Flashcard]) -> None:
        """Shuffle the card list and reset the index.

        Args:
            cards: The list of flashcards to shuffle.
        """
        self._cards = list(cards)
        if self._seed is not None:
            random.seed(self._seed)
        random.shuffle(self._cards)
        self._current_index = 0

    def select_next_card(self) -> Optional[Flashcard]:
        """Return the next card in the shuffled order.

        Returns:
            The next Flashcard, or None if all cards have been shown.
        """
        if self._current_index >= len(self._cards):
            return None
        card = self._cards[self._current_index]
        self._current_index += 1
        return card

    def record_result(self, card: Flashcard, correct: bool) -> None:
        """Record the result (no-op for random mode).

        Random mode does not adjust ordering based on results.

        Args:
            card: The flashcard that was answered.
            correct: Whether the answer was correct.
        """
        pass

    def has_more_cards(self) -> bool:
        """Check if there are remaining cards in the shuffled sequence.

        Returns:
            True if the current index has not reached the end.
        """
        return self._current_index < len(self._cards)

    def reset(self) -> None:
        """Reset the index and reshuffle the cards."""
        self._current_index = 0
        if self._seed is not None:
            random.seed(self._seed)
        random.shuffle(self._cards)


class AdaptiveStrategy(QuizStrategy):
    """Prioritizes flashcards the user previously got wrong.

    This strategy implements a weighted selection approach. Cards that
    were answered incorrectly are given higher priority and are presented
    more frequently. The session consists of two passes:

    1. First pass: All cards are presented once (in random order).
    2. Second pass: Only missed cards are re-presented for reinforcement.

    The adaptive behavior ensures the user focuses more time on material
    they find difficult.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """Initialize the adaptive strategy.

        Args:
            seed: Optional random seed for reproducible behavior in testing.
        """
        self._cards: List[Flashcard] = []
        self._missed_cards: List[Flashcard] = []
        self._current_queue: List[Flashcard] = []
        self._current_index: int = 0
        self._first_pass_complete: bool = False
        self._seed: Optional[int] = seed

    def initialize(self, cards: List[Flashcard]) -> None:
        """Set up the card list for the first pass.

        Cards are shuffled for the initial presentation to avoid
        predictable ordering.

        Args:
            cards: The list of flashcards to use in this session.
        """
        self._cards = list(cards)
        self._missed_cards = []
        self._first_pass_complete = False
        self._current_index = 0

        if self._seed is not None:
            random.seed(self._seed)
        self._current_queue = list(self._cards)
        random.shuffle(self._current_queue)

    def select_next_card(self) -> Optional[Flashcard]:
        """Select the next card based on adaptive logic.

        During the first pass, cards are presented in shuffled order.
        After the first pass, only missed cards are re-presented.

        Returns:
            The next Flashcard, or None if the session is complete.
        """
        if self._current_index >= len(self._current_queue):
            if not self._first_pass_complete:
                self._first_pass_complete = True
                if self._missed_cards:
                    self._current_queue = list(self._missed_cards)
                    if self._seed is not None:
                        random.seed(self._seed + 1)
                    random.shuffle(self._current_queue)
                    self._current_index = 0
                else:
                    return None
            else:
                return None

        if self._current_index >= len(self._current_queue):
            return None

        card = self._current_queue[self._current_index]
        self._current_index += 1
        return card

    def record_result(self, card: Flashcard, correct: bool) -> None:
        """Record the result to track missed cards for reinforcement.

        Cards answered incorrectly during the first pass are added to
        the missed cards list for the second pass.

        Args:
            card: The flashcard that was answered.
            correct: Whether the answer was correct.
        """
        if not correct and not self._first_pass_complete:
            if card not in self._missed_cards:
                self._missed_cards.append(card)

    def has_more_cards(self) -> bool:
        """Check if there are more cards to present.

        Returns:
            True if there are remaining cards in the current queue,
            or if the first pass is not complete and there are missed cards.
        """
        if self._current_index < len(self._current_queue):
            return True
        if not self._first_pass_complete and self._missed_cards:
            return True
        return False

    def reset(self) -> None:
        """Reset all adaptive state for a fresh session."""
        self._missed_cards = []
        self._first_pass_complete = False
        self._current_index = 0
        if self._seed is not None:
            random.seed(self._seed)
        self._current_queue = list(self._cards)
        random.shuffle(self._current_queue)


def create_strategy(mode: str, seed: Optional[int] = None) -> QuizStrategy:
    """Factory function to create a quiz strategy by name.

    This function provides a simple way to instantiate the appropriate
    strategy based on a string identifier, following the Factory pattern
    for object creation.

    Args:
        mode: The quiz mode name. Must be one of: 'sequential', 'random',
            or 'adaptive'.
        seed: Optional random seed for reproducible behavior in testing.

    Returns:
        An instance of the appropriate QuizStrategy subclass.

    Raises:
        ValueError: If the mode name is not recognized.
    """
    strategies = {
        "sequential": SequentialStrategy,
        "random": RandomStrategy,
        "adaptive": AdaptiveStrategy,
    }

    mode_lower = mode.strip().lower()
    if mode_lower not in strategies:
        valid_modes = ", ".join(sorted(strategies.keys()))
        raise ValueError(
            f"Unknown quiz mode: '{mode}'. Valid modes are: {valid_modes}."
        )

    if mode_lower == "sequential":
        return SequentialStrategy()
    else:
        return strategies[mode_lower](seed=seed)
