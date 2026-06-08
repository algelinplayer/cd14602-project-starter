# AI Edit Log

This document records the AI interactions, code reviews, and decisions made throughout the development of the Flashcard Quizzer application.

---

## Interaction 1: Core Models and Data Ingestion

**Date:** 2026-06-08

**Prompt Used:**
> "Create the core domain models for a Flashcard Quizzer CLI application. I need a `Flashcard` dataclass with `front` and `back` string fields and a `check_answer` method that performs case-insensitive comparison. I also need a `Deck` dataclass with a `name` field and a list of `Flashcard` objects, plus a `size` property and `is_empty` method. Use Python type hints on all functions and include docstrings."

**AI Response Summary:**
The AI generated `models.py` with both dataclasses. The initial output was clean and met the requirements.

**Review Findings:**
- Code follows PEP 8 style guidelines.
- All functions have type hints and docstrings.
- The `check_answer` method correctly uses `.strip().lower()` for case-insensitive comparison.
- No unnecessary dependencies or over-engineering detected.

**Decision:** ACCEPTED without modification.

---

## Interaction 2: Data Loader with Validation

**Date:** 2026-06-08

**Prompt Used:**
> "Create a `data_loader.py` module that reads flashcard data from a JSON file. The expected schema is: `{\"deck_name\": \"string\", \"cards\": [{\"front\": \"string\", \"back\": \"string\"}, ...]}`. The module must: (1) validate the JSON structure, (2) raise a custom `DataLoadError` exception with helpful messages if the file is missing, malformed, or has invalid schema, (3) never show raw stack traces to the user. Include separate validation functions for the deck structure and individual cards. Use Python type hints and docstrings."

**AI Response Summary:**
The AI generated a comprehensive `data_loader.py` with `validate_card_data`, `validate_deck_structure`, and `load_deck_from_json` functions.

**Review Findings:**
- Proper error handling with custom exception class.
- Validates file existence, JSON parsing, schema structure, and individual card fields.
- Uses `pathlib.Path` for cross-platform file handling.
- Graceful error messages that help users diagnose issues.
- No phantom dependencies; only uses standard library modules (`json`, `pathlib`).

**Issues Found and Fixed:**
- Initial version did not check for empty strings in `front`/`back` fields. Added validation to reject whitespace-only strings.
- Added `PermissionError` handling that was missing from the initial generation.

**Checklist reviewed:** PEP 8, error handling, input validation, type hints, docstrings, dependencies.
**Validation:** `pytest tests/test_data_loader.py -q` — 23 passed.

**Decision:** ACCEPTED after minor refinements (added empty string validation and permission error handling).

---

## Interaction 3: Unit Tests for Data Loading

**Date:** 2026-06-08

**Prompt Used:**
> "Write a comprehensive pytest test suite for the `data_loader.py` module. Test valid loading, file not found, invalid JSON, missing schema fields, invalid card entries, and edge cases like empty strings and non-dict cards. Use temporary files for test fixtures. Organize tests into classes by function being tested."

**AI Response Summary:**
The AI generated `test_data_loader.py` with four test classes covering all validation functions and the main loader.

**Review Findings:**
- Tests are well-organized into logical classes.
- Uses `tempfile` for creating test fixtures (no hardcoded paths).
- Covers both happy path and error scenarios.
- Test names are descriptive and follow pytest conventions.
- Properly cleans up temporary files with `try/finally` blocks.

**Decision:** ACCEPTED without modification.

---

## Interaction 4: Strategy Pattern for Quiz Modes

**Date:** 2026-06-08

**Prompt Used:**
> "Implement the Strategy Pattern for quiz modes in a `quiz_modes.py` module. Create an abstract base class `QuizStrategy` with methods: `initialize(cards)`, `select_next_card()`, `record_result(card, correct)`, `has_more_cards()`, and `reset()`. Then implement three concrete strategies: (1) `SequentialStrategy` - presents cards in order, (2) `RandomStrategy` - shuffles the deck (accept optional seed for testing), (3) `AdaptiveStrategy` - first pass shows all cards, second pass repeats only missed cards. Also create a `create_strategy(mode, seed)` factory function. Use type hints and docstrings."

**AI Response Summary:**
The AI generated a comprehensive `quiz_modes.py` with the abstract base class, three concrete strategies, and a factory function.

**Review Findings:**
- Strategy Pattern correctly implemented with proper ABC inheritance.
- All strategies implement the full interface.
- `RandomStrategy` accepts an optional seed for deterministic testing.
- `AdaptiveStrategy` correctly tracks missed cards and provides a second pass.
- Factory function handles case-insensitive mode names and raises `ValueError` for unknown modes.

**Issues Found and Fixed:**
- The `RandomStrategy.reset()` method had a subtle bug: it was reshuffling from the already-shuffled state, causing non-deterministic behavior even with a seed after reset. Fixed by ensuring the seed is re-applied before shuffling.
- A test (`test_reset_reshuffles`) was making an incorrect assumption about deterministic replay. Rewrote it as `test_reset_allows_full_replay` to verify the correct behavior (all cards available again after reset).

**Checklist reviewed:** PEP 8, design pattern correctness, type hints, docstrings, deterministic testing.
**Validation:** `pytest tests/test_quiz_modes.py -q` — 28 passed.

**Decision:** ACCEPTED after fixing the reset/seed interaction bug.

---

## Interaction 5: Unit Tests for Quiz Modes

**Date:** 2026-06-08

**Prompt Used:**
> "Write a comprehensive pytest test suite for the quiz_modes module. Test all three strategies (Sequential, Random, Adaptive) and the factory function. For Sequential: test ordering, exhaustion, reset, empty list. For Random: test all cards presented once, different order from sequential, reproducibility with seed, exhaustion. For Adaptive: test first pass presents all cards, no second pass if all correct, missed cards repeated, total presentations count. For the factory: test all valid modes, case insensitivity, invalid mode error."

**AI Response Summary:**
The AI generated `test_quiz_modes.py` with four test classes and 28 test methods.

**Review Findings:**
- Comprehensive coverage of all strategy behaviors.
- Uses seed parameter for deterministic testing of random strategies.
- Tests both happy paths and edge cases (empty lists, exhaustion).
- Well-organized with descriptive test names.

**Decision:** ACCEPTED after one test fix (described above in Interaction 4).

---

## Interaction 6: Terminal UI Module

**Date:** 2026-06-08

**Prompt Used:**
> "Create a `ui.py` module that handles all terminal interaction for the Flashcard Quizzer. Define a `UIProtocol` using Python's `typing.Protocol` to decouple the UI from the engine (for testability). Then implement a `TerminalUI` class with methods: `display_welcome`, `display_card`, `get_answer`, `display_correct`, `display_incorrect`, `display_stats`, `display_message`, `display_error`. Use clean formatting with separators. Handle EOFError and KeyboardInterrupt in get_answer."

**AI Response Summary:**
The AI generated `ui.py` with a Protocol class and a concrete TerminalUI implementation.

**Review Findings:**
- Clean separation using Protocol for dependency inversion.
- All methods have type hints and docstrings.
- Graceful handling of EOFError/KeyboardInterrupt in get_answer.
- Consistent formatting with separator constants.
- Stats display includes accuracy percentage and missed terms list.

**Decision:** ACCEPTED without modification.

---

## Interaction 7: Quiz Engine (Core Logic)

**Date:** 2026-06-08

**Prompt Used:**
> "Create a `quiz_engine.py` module that orchestrates a quiz session. It should: (1) Accept a Deck, a QuizStrategy, and a UIProtocol as dependencies. (2) Define a `SessionStats` dataclass tracking total_questions, correct_count, and missed_terms with computed accuracy property. (3) Implement a `QuizEngine` class with a `run()` method that initializes the strategy, runs the question-answer loop, and displays results. (4) Track missed terms without duplicates. Use type hints and docstrings."

**AI Response Summary:**
The AI generated `quiz_engine.py` with SessionStats and QuizEngine classes.

**Review Findings:**
- Clean dependency injection pattern (deck, strategy, ui passed to constructor).
- SessionStats correctly computes accuracy and handles division by zero.
- The quiz loop correctly delegates card selection to the strategy.
- Missed terms are tracked without duplicates using `not in` check.
- Mode name is automatically derived from the strategy class name.

**Decision:** ACCEPTED without modification.

---

## Interaction 8: Unit Tests for Quiz Engine

**Date:** 2026-06-08

**Prompt Used:**
> "Write a pytest test suite for the quiz_engine module. Create a MockUI class that records all method calls and returns predetermined answers. Test scenarios: all correct, all incorrect, mixed answers, case-insensitive matching, adaptive mode with repeats, empty answers, whitespace handling, mode name detection, and no duplicate missed terms. Use SequentialStrategy for predictable ordering in most tests."

**AI Response Summary:**
The AI generated `test_quiz_engine.py` with a MockUI class and 23 test methods across 7 test classes.

**Review Findings:**
- MockUI correctly implements the UIProtocol interface for testing.
- Tests cover all major scenarios including edge cases.
- Uses SequentialStrategy for predictable card ordering in most tests.
- Adaptive strategy tests correctly account for shuffled card order.

**Issues Found and Fixed:**
- One test (`test_no_repeat_if_all_correct`) provided answers in the wrong order for the AdaptiveStrategy with seed=42. The adaptive mode shuffles cards, so with seed=42 the order is Q2, Q1 (not Q1, Q2). Fixed by providing answers matching the shuffled order.

**Decision:** ACCEPTED after fixing the answer order in one adaptive test.

---

## Interaction 9: CLI Entry Point with argparse

**Date:** 2026-06-08

**Prompt Used:**
> "Rewrite `main.py` as the CLI entry point for the Flashcard Quizzer. Use argparse with a required positional `file` argument and an optional `--mode` argument (choices: sequential, random, adaptive; default: sequential). The `main()` function should: load the deck, create the strategy, initialize TerminalUI and QuizEngine, run the quiz, and handle errors gracefully. Accept an optional `args` parameter for testing. Return exit codes (0 success, 1 error). Handle KeyboardInterrupt."

**AI Response Summary:**
The AI generated a clean `main.py` with `parse_arguments()` and `main()` functions.

**Review Findings:**
- argparse correctly configured with choices validation.
- Error handling wraps DataLoadError and ValueError with user-friendly messages.
- KeyboardInterrupt handled gracefully with a goodbye message.
- The `args` parameter enables testing without mocking sys.argv.
- Clean separation between argument parsing and application logic.

**Decision:** ACCEPTED without modification.

---

## Interaction 10: CLI Integration Tests

**Date:** 2026-06-08

**Prompt Used:**
> "Write pytest tests for main.py. Test argument parsing (required file, default mode, all modes, invalid mode rejection) and the main function (nonexistent file returns 1, valid file with mocked input returns 0 for all modes, KeyboardInterrupt handled gracefully)."

**AI Response Summary:**
The AI generated `test_main.py` with 11 tests across two classes.

**Review Findings:**
- Argument parsing tests correctly verify argparse behavior.
- Main function tests use `unittest.mock.patch` on `builtins.input` to avoid blocking.
- KeyboardInterrupt test verifies graceful exit with code 0.

**Issues Found and Fixed (Resubmission):**
- Tests originally used `Path(__file__).parent.parent / "data" / "flashcards.json"`, creating a dependency on a project-level file. Rewrote all valid-file tests to use pytest `tmp_path` fixtures that create their own deck JSON, making tests fully self-contained and robust against packaging issues.
- Removed unused `import sys`.

**Checklist reviewed:** PEP 8, test isolation, fixture management, no hardcoded paths.
**Validation:** `pytest tests/test_main.py -q` — 11 passed.

**Decision:** ACCEPTED after rewriting to use `tmp_path` fixtures for test isolation.

---

## Interaction 11: Rejected Suggestion — External Dependency for CLI Colors

**Date:** 2026-06-08

**Prompt Used:**
> "Improve the terminal UI to make correct/incorrect feedback more visually distinct."

**AI Response Summary:**
The AI suggested installing the `colorama` package and wrapping output strings with ANSI color codes via `colorama.Fore.GREEN` / `colorama.Fore.RED`.

**Review Findings:**
- The suggestion would add an external runtime dependency (`colorama`) to the project.
- The project constraints explicitly require standard-library-only application code.
- Adding `colorama` would violate the zero-runtime-dependency goal and complicate installation.
- The existing UI already uses clear text markers (`✓` and `✗`) for correct/incorrect feedback.

**Decision:** REJECTED.
**Reasoning:** The project constraints require zero external runtime dependencies. The existing Unicode markers provide sufficient visual distinction without adding package complexity.
**Alternative:** Kept the current `✓ Correct!` and `✗ Incorrect` markers, which work across all terminals without dependencies.

---

## Interaction 12: Code Quality Verification (Resubmission)

**Date:** 2026-06-08

**Prompt Used:**
> "Run black and flake8 on the entire project. Fix all formatting and linting issues. Remove unused imports."

**AI Response Summary:**
The AI ran `black .` (reformatted 10 files) and `flake8 .` (found 7 violations: unused imports in data_loader.py, test_file_handler.py, test_quiz_engine.py, test_task_manager.py, file_handler.py, and an f-string without placeholders in ui.py).

**Issues Found and Fixed:**
- Removed `import sys` from `data_loader.py` (F401 unused import).
- Removed `from pathlib import Path` from `test_file_handler.py` (F401 unused import).
- Removed `MagicMock, call, patch` and `pytest` imports from `test_quiz_engine.py` (F401 unused).
- Removed `from datetime import datetime` from `test_task_manager.py` (F401 unused).
- Removed `import os` from `utils/file_handler.py` (F401 unused).
- Changed `print(f"  FLASHCARD QUIZZER")` to `print("  FLASHCARD QUIZZER")` in `ui.py` (F541 f-string without placeholders).

**Checklist reviewed:** PEP 8, formatting (black), linting (flake8), unused imports, f-string correctness.
**Validation:**
```
$ black --check .
All done! 17 files would be left unchanged.

$ flake8 . --max-line-length=100
(no output — zero violations)
```

**Decision:** All fixes applied. Project now passes both `black --check` and `flake8` with zero issues.
