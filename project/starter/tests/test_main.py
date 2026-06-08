"""Tests for the main CLI entry point.

This module verifies the argument parsing and main function behavior,
including error handling for invalid files and modes.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from main import main, parse_arguments

# Sample valid deck data for testing
SAMPLE_DECK = {
    "deck_name": "Test Deck",
    "cards": [
        {
            "front": "What does API stand for?",
            "back": "Application Programming Interface",
        },
        {"front": "What does HTTP stand for?", "back": "HyperText Transfer Protocol"},
        {"front": "What does DNS stand for?", "back": "Domain Name System"},
    ],
}


@pytest.fixture
def valid_deck_file(tmp_path: Path) -> str:
    """Create a temporary valid deck file and return its path as a string."""
    deck_path = tmp_path / "flashcards.json"
    deck_path.write_text(json.dumps(SAMPLE_DECK), encoding="utf-8")
    return str(deck_path)


class TestParseArguments:
    """Tests for the parse_arguments function."""

    def test_file_argument_required(self) -> None:
        """The file argument should be required."""
        with pytest.raises(SystemExit):
            parse_arguments([])

    def test_file_argument_parsed(self) -> None:
        """The file path should be correctly parsed."""
        args = parse_arguments(["data/flashcards.json"])
        assert args.file == "data/flashcards.json"

    def test_default_mode_is_sequential(self) -> None:
        """The default mode should be 'sequential'."""
        args = parse_arguments(["data/flashcards.json"])
        assert args.mode == "sequential"

    def test_mode_random(self) -> None:
        """The --mode random flag should be parsed correctly."""
        args = parse_arguments(["data/flashcards.json", "--mode", "random"])
        assert args.mode == "random"

    def test_mode_adaptive(self) -> None:
        """The --mode adaptive flag should be parsed correctly."""
        args = parse_arguments(["data/flashcards.json", "--mode", "adaptive"])
        assert args.mode == "adaptive"

    def test_invalid_mode_rejected(self) -> None:
        """An invalid mode should cause argparse to exit with error."""
        with pytest.raises(SystemExit):
            parse_arguments(["data/flashcards.json", "--mode", "invalid"])


class TestMainFunction:
    """Tests for the main function."""

    def test_nonexistent_file_returns_error(self) -> None:
        """A non-existent file should return exit code 1."""
        result = main(["nonexistent_file.json"])
        assert result == 1

    def test_valid_file_with_mocked_input(self, valid_deck_file: str) -> None:
        """A valid file should run the quiz (mocked input for non-interactive)."""
        answers = iter(["answer"] * 20)
        with patch("builtins.input", side_effect=answers):
            result = main([valid_deck_file, "--mode", "sequential"])

        assert result == 0

    def test_valid_file_random_mode(self, valid_deck_file: str) -> None:
        """Random mode should work with a valid file."""
        answers = iter(["answer"] * 20)
        with patch("builtins.input", side_effect=answers):
            result = main([valid_deck_file, "--mode", "random"])

        assert result == 0

    def test_valid_file_adaptive_mode(self, valid_deck_file: str) -> None:
        """Adaptive mode should work with a valid file."""
        # Provide enough answers for first pass + potential second pass
        answers = iter(["answer"] * 30)
        with patch("builtins.input", side_effect=answers):
            result = main([valid_deck_file, "--mode", "adaptive"])

        assert result == 0

    def test_keyboard_interrupt_handled(self, valid_deck_file: str) -> None:
        """KeyboardInterrupt during quiz should be handled gracefully."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            result = main([valid_deck_file])

        assert result == 0
