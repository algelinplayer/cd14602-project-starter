"""Tests for the data_loader module.

This module verifies that the data loading and validation logic correctly
handles valid JSON files, missing files, malformed JSON, and schema violations.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from flashcard_quizzer.data_loader import (
    DataLoadError,
    load_deck_from_json,
    validate_card_data,
    validate_deck_structure,
)
from flashcard_quizzer.models import Deck, Flashcard


class TestValidateCardData:
    """Tests for the validate_card_data function."""

    def test_valid_card_passes_validation(self) -> None:
        """A card with both 'front' and 'back' string fields should pass."""
        card_data = {"front": "What is Python?", "back": "A programming language"}
        # Should not raise
        validate_card_data(card_data, 0)

    def test_missing_front_field_raises_error(self) -> None:
        """A card missing the 'front' field should raise DataLoadError."""
        card_data = {"back": "A programming language"}
        with pytest.raises(DataLoadError, match="missing the required 'front' field"):
            validate_card_data(card_data, 0)

    def test_missing_back_field_raises_error(self) -> None:
        """A card missing the 'back' field should raise DataLoadError."""
        card_data = {"front": "What is Python?"}
        with pytest.raises(DataLoadError, match="missing the required 'back' field"):
            validate_card_data(card_data, 1)

    def test_non_dict_card_raises_error(self) -> None:
        """A card that is not a dictionary should raise DataLoadError."""
        with pytest.raises(DataLoadError, match="not a valid object"):
            validate_card_data("not a dict", 0)

    def test_empty_front_field_raises_error(self) -> None:
        """A card with an empty 'front' field should raise DataLoadError."""
        card_data = {"front": "   ", "back": "Answer"}
        with pytest.raises(DataLoadError, match="invalid 'front' field"):
            validate_card_data(card_data, 0)

    def test_empty_back_field_raises_error(self) -> None:
        """A card with an empty 'back' field should raise DataLoadError."""
        card_data = {"front": "Question", "back": ""}
        with pytest.raises(DataLoadError, match="invalid 'back' field"):
            validate_card_data(card_data, 0)

    def test_non_string_front_raises_error(self) -> None:
        """A card with a non-string 'front' should raise DataLoadError."""
        card_data = {"front": 123, "back": "Answer"}
        with pytest.raises(DataLoadError, match="invalid 'front' field"):
            validate_card_data(card_data, 0)


class TestValidateDeckStructure:
    """Tests for the validate_deck_structure function."""

    def test_valid_structure_passes(self) -> None:
        """A properly structured deck should pass validation."""
        data = {
            "deck_name": "Test Deck",
            "cards": [{"front": "Q", "back": "A"}],
        }
        # Should not raise
        validate_deck_structure(data)

    def test_missing_deck_name_raises_error(self) -> None:
        """Missing 'deck_name' should raise DataLoadError."""
        data = {"cards": [{"front": "Q", "back": "A"}]}
        with pytest.raises(DataLoadError, match="Missing required field 'deck_name'"):
            validate_deck_structure(data)

    def test_missing_cards_raises_error(self) -> None:
        """Missing 'cards' field should raise DataLoadError."""
        data = {"deck_name": "Test"}
        with pytest.raises(DataLoadError, match="Missing required field 'cards'"):
            validate_deck_structure(data)

    def test_cards_not_a_list_raises_error(self) -> None:
        """Non-list 'cards' field should raise DataLoadError."""
        data = {"deck_name": "Test", "cards": "not a list"}
        with pytest.raises(DataLoadError, match="must be a list"):
            validate_deck_structure(data)

    def test_empty_cards_list_raises_error(self) -> None:
        """An empty 'cards' list should raise DataLoadError."""
        data = {"deck_name": "Test", "cards": []}
        with pytest.raises(DataLoadError, match="list is empty"):
            validate_deck_structure(data)

    def test_non_dict_top_level_raises_error(self) -> None:
        """A non-dict top-level structure should raise DataLoadError."""
        with pytest.raises(DataLoadError, match="Invalid JSON structure"):
            validate_deck_structure([{"front": "Q", "back": "A"}])


class TestLoadDeckFromJson:
    """Tests for the load_deck_from_json function."""

    def _create_temp_json(self, data: dict) -> str:
        """Helper to create a temporary JSON file with given data.

        Args:
            data: The dictionary to serialize as JSON.

        Returns:
            The path to the temporary file.
        """
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump(data, tmp)
        tmp.close()
        return tmp.name

    def test_load_valid_json_file(self) -> None:
        """Loading a valid JSON file should return a populated Deck."""
        data = {
            "deck_name": "Test Deck",
            "cards": [
                {"front": "What is 2+2?", "back": "4"},
                {"front": "Capital of France?", "back": "Paris"},
            ],
        }
        path = self._create_temp_json(data)
        try:
            deck = load_deck_from_json(path)
            assert isinstance(deck, Deck)
            assert deck.name == "Test Deck"
            assert deck.size == 2
            assert deck.cards[0].front == "What is 2+2?"
            assert deck.cards[0].back == "4"
            assert deck.cards[1].front == "Capital of France?"
            assert deck.cards[1].back == "Paris"
        finally:
            os.unlink(path)

    def test_file_not_found_raises_error(self) -> None:
        """A non-existent file path should raise DataLoadError."""
        with pytest.raises(DataLoadError, match="File not found"):
            load_deck_from_json("/nonexistent/path/flashcards.json")

    def test_invalid_json_raises_error(self) -> None:
        """A file with invalid JSON should raise DataLoadError."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        tmp.write("{invalid json content")
        tmp.close()
        try:
            with pytest.raises(DataLoadError, match="Invalid JSON"):
                load_deck_from_json(tmp.name)
        finally:
            os.unlink(tmp.name)

    def test_missing_required_fields_raises_error(self) -> None:
        """A JSON file missing required fields should raise DataLoadError."""
        data = {"title": "Wrong Schema", "items": []}
        path = self._create_temp_json(data)
        try:
            with pytest.raises(DataLoadError):
                load_deck_from_json(path)
        finally:
            os.unlink(path)

    def test_invalid_card_in_deck_raises_error(self) -> None:
        """A deck with an invalid card entry should raise DataLoadError."""
        data = {
            "deck_name": "Bad Deck",
            "cards": [
                {"front": "Valid Question", "back": "Valid Answer"},
                {"front": "Missing back field"},
            ],
        }
        path = self._create_temp_json(data)
        try:
            with pytest.raises(
                DataLoadError, match="missing the required 'back' field"
            ):
                load_deck_from_json(path)
        finally:
            os.unlink(path)

    def test_load_sample_data_file(self) -> None:
        """Loading the provided sample data file should succeed."""
        sample_path = Path(__file__).parent.parent / "data" / "flashcards.json"
        if sample_path.exists():
            deck = load_deck_from_json(str(sample_path))
            assert deck.name == "Server Acronyms"
            assert deck.size == 10
            assert deck.cards[0].front == "What does API stand for?"

    def test_directory_path_raises_error(self) -> None:
        """Passing a directory path instead of a file should raise DataLoadError."""
        with pytest.raises(DataLoadError, match="not a file"):
            load_deck_from_json("/tmp")


class TestFlashcardModel:
    """Tests for the Flashcard model."""

    def test_check_answer_correct(self) -> None:
        """A correct answer (case-insensitive) should return True."""
        card = Flashcard(front="Capital of France?", back="Paris")
        assert card.check_answer("Paris") is True
        assert card.check_answer("paris") is True
        assert card.check_answer("PARIS") is True
        assert card.check_answer("  paris  ") is True

    def test_check_answer_incorrect(self) -> None:
        """An incorrect answer should return False."""
        card = Flashcard(front="Capital of France?", back="Paris")
        assert card.check_answer("London") is False
        assert card.check_answer("") is False

    def test_deck_properties(self) -> None:
        """Deck size and is_empty should reflect the card list."""
        empty_deck = Deck(name="Empty", cards=[])
        assert empty_deck.size == 0
        assert empty_deck.is_empty() is True

        card = Flashcard(front="Q", back="A")
        full_deck = Deck(name="Full", cards=[card])
        assert full_deck.size == 1
        assert full_deck.is_empty() is False
