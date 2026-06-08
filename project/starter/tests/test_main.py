"""Tests for the main CLI entry point.

This module verifies the argument parsing and main function behavior,
including error handling for invalid files and modes.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from main import main, parse_arguments


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

    def test_valid_file_with_mocked_input(self) -> None:
        """A valid file should run the quiz (mocked input for non-interactive)."""
        sample_path = str(Path(__file__).parent.parent / "data" / "flashcards.json")

        # Mock input to provide answers and avoid blocking
        answers = iter(["answer"] * 20)
        with patch("builtins.input", side_effect=answers):
            result = main([sample_path, "--mode", "sequential"])

        assert result == 0

    def test_valid_file_random_mode(self) -> None:
        """Random mode should work with a valid file."""
        sample_path = str(Path(__file__).parent.parent / "data" / "flashcards.json")

        answers = iter(["answer"] * 20)
        with patch("builtins.input", side_effect=answers):
            result = main([sample_path, "--mode", "random"])

        assert result == 0

    def test_valid_file_adaptive_mode(self) -> None:
        """Adaptive mode should work with a valid file."""
        sample_path = str(Path(__file__).parent.parent / "data" / "flashcards.json")

        # Provide enough answers for first pass + potential second pass
        answers = iter(["answer"] * 30)
        with patch("builtins.input", side_effect=answers):
            result = main([sample_path, "--mode", "adaptive"])

        assert result == 0

    def test_keyboard_interrupt_handled(self) -> None:
        """KeyboardInterrupt during quiz should be handled gracefully."""
        sample_path = str(Path(__file__).parent.parent / "data" / "flashcards.json")

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            result = main([sample_path])

        assert result == 0
