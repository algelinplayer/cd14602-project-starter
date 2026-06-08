"""Flashcard Quizzer - CLI Entry Point.

This module serves as the main entry point for the Flashcard Quizzer
application. It uses argparse to parse command-line arguments for
selecting the flashcard data file and quiz mode, then orchestrates
the quiz session by wiring together the data loader, strategy, UI,
and quiz engine components.

Usage:
    python main.py data/flashcards.json --mode sequential
    python main.py data/flashcards.json --mode random
    python main.py data/flashcards.json --mode adaptive
"""

import argparse
import sys

from flashcard_quizzer.data_loader import DataLoadError, load_deck_from_json
from flashcard_quizzer.quiz_engine import QuizEngine
from flashcard_quizzer.quiz_modes import create_strategy
from flashcard_quizzer.ui import TerminalUI


def parse_arguments(args: list = None) -> argparse.Namespace:
    """Parse command-line arguments for the Flashcard Quizzer.

    Args:
        args: Optional list of arguments to parse. If None, uses sys.argv.

    Returns:
        A Namespace object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="flashcard-quizzer",
        description="A CLI flashcard quiz application with multiple study modes.",
        epilog="Example: python main.py data/flashcards.json --mode adaptive",
    )

    parser.add_argument(
        "file",
        type=str,
        help="Path to the JSON file containing flashcard data.",
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["sequential", "random", "adaptive"],
        default="sequential",
        help="Quiz mode: 'sequential' (default), 'random', or 'adaptive'.",
    )

    return parser.parse_args(args)


def main(args: list = None) -> int:
    """Main function that runs the Flashcard Quizzer application.

    This function coordinates the full application lifecycle:
    1. Parse CLI arguments.
    2. Load and validate the flashcard deck from JSON.
    3. Create the appropriate quiz strategy.
    4. Initialize the UI and quiz engine.
    5. Run the quiz session.

    Args:
        args: Optional list of arguments (for testing). If None, uses sys.argv.

    Returns:
        Exit code: 0 for success, 1 for errors.
    """
    parsed_args = parse_arguments(args)

    # Load the flashcard deck
    try:
        deck = load_deck_from_json(parsed_args.file)
    except DataLoadError as e:
        print(f"\n  ERROR: {e}", file=sys.stderr)
        return 1

    # Create the quiz strategy
    try:
        strategy = create_strategy(parsed_args.mode)
    except ValueError as e:
        print(f"\n  ERROR: {e}", file=sys.stderr)
        return 1

    # Initialize UI and engine
    ui = TerminalUI()
    engine = QuizEngine(deck=deck, strategy=strategy, ui=ui)

    # Run the quiz
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\n\n  Quiz interrupted. Goodbye!")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
