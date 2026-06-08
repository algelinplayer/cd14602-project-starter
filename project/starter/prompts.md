# Prompt Log

This file documents the specific prompts used to guide AI code generation for the Flashcard Quizzer project.

---

## Prompt 1: Core Domain Models

```
Create the core domain models for a Flashcard Quizzer CLI application. I need:
1. A `Flashcard` dataclass with `front` and `back` string fields and a `check_answer` 
   method that performs case-insensitive comparison (strip whitespace too).
2. A `Deck` dataclass with a `name` field and a list of `Flashcard` objects, plus a 
   `size` property and `is_empty` method.

Requirements:
- Use Python dataclasses
- All functions must have Python Type Hints
- Include comprehensive docstrings
- Follow PEP 8 style guidelines
```

---

## Prompt 2: Data Loader Module

```
Create a `data_loader.py` module for loading flashcard data from JSON files.

Expected JSON schema:
{
    "deck_name": "string",
    "cards": [{"front": "string", "back": "string"}, ...]
}

Requirements:
- Define a custom `DataLoadError` exception class
- Create a `validate_card_data(card_data, index)` function that checks individual cards
- Create a `validate_deck_structure(data)` function that checks the top-level schema
- Create a `load_deck_from_json(file_path)` function as the main entry point
- Handle: FileNotFoundError, JSONDecodeError, PermissionError
- Never expose raw stack traces; always provide helpful error messages
- Validate that 'front' and 'back' are non-empty strings
- Use pathlib.Path for file operations
- All functions must have type hints and docstrings
- Do NOT use any external dependencies beyond the standard library
```

---

## Prompt 3: Unit Tests for Data Loader

```
Write a comprehensive pytest test suite for the data_loader module.

Test the following scenarios:
- validate_card_data: valid card, missing front, missing back, non-dict input, 
  empty strings, non-string types
- validate_deck_structure: valid structure, missing deck_name, missing cards, 
  cards not a list, empty cards list, non-dict top level
- load_deck_from_json: valid file, file not found, invalid JSON, missing fields, 
  invalid card in deck, directory path instead of file

Requirements:
- Use pytest with classes to organize tests by function
- Use tempfile for creating test fixtures (no hardcoded paths)
- Clean up temporary files after tests
- Use descriptive test names
- Include type hints on test methods
```

---

## Prompt 4: Strategy Pattern for Quiz Modes

```
Implement the Strategy Pattern for quiz modes in a `quiz_modes.py` module.

Architecture:
1. Abstract Base Class `QuizStrategy` with methods:
   - initialize(cards: List[Flashcard]) -> None
   - select_next_card() -> Optional[Flashcard]
   - record_result(card: Flashcard, correct: bool) -> None
   - has_more_cards() -> bool
   - reset() -> None

2. Concrete Strategies:
   - SequentialStrategy: presents cards in original order (index 0 to N-1)
   - RandomStrategy: shuffles deck, presents each card once. Accept optional 
     `seed` parameter for reproducible testing.
   - AdaptiveStrategy: Two passes. First pass shows all cards (shuffled). 
     Second pass repeats only cards answered incorrectly. Accept optional `seed`.

3. Factory function `create_strategy(mode: str, seed: Optional[int]) -> QuizStrategy`
   that creates the appropriate strategy by name (case-insensitive).

Requirements:
- Use Python ABC for the abstract base class
- All functions must have type hints and comprehensive docstrings
- Follow PEP 8 style guidelines
- Do NOT use external dependencies (only standard library: abc, random)
- Raise ValueError for unknown mode names with helpful message
```

---

## Prompt 5: Unit Tests for Quiz Modes

```
Write a comprehensive pytest test suite for the quiz_modes module.

Test classes needed:
1. TestSequentialStrategy:
   - Cards presented in order
   - Returns None when exhausted
   - Reset restarts from beginning
   - record_result is no-op
   - Empty card list handled
   - Does not mutate original list

2. TestRandomStrategy:
   - All cards presented exactly once
   - Order differs from sequential
   - Reproducible with same seed
   - Returns None when exhausted
   - Reset allows full replay
   - record_result is no-op

3. TestAdaptiveStrategy:
   - First pass presents all cards
   - No second pass if all correct
   - Missed cards repeated in second pass
   - Second pass only contains missed cards
   - Total presentations = N + missed count
   - Reset clears missed cards
   - has_more_cards during transition

4. TestCreateStrategy:
   - Creates each strategy type
   - Case insensitive
   - Strips whitespace
   - Invalid mode raises ValueError
   - Seed parameter works
   - All strategies implement QuizStrategy interface

Requirements:
- Use pytest with classes
- Use seed parameter for deterministic testing
- Descriptive test names with type hints
```

---

## Prompt 6: Terminal UI Module

```
Create a `ui.py` module that handles all terminal interaction for the Flashcard Quizzer.

Architecture:
1. Define a `UIProtocol` using Python's `typing.Protocol` for dependency inversion.
   Methods: display_welcome, display_card, get_answer, display_correct,
   display_incorrect, display_stats, display_message, display_error.

2. Implement a `TerminalUI` class that fulfills the protocol.
   - Use consistent separators for visual clarity
   - Handle EOFError and KeyboardInterrupt in get_answer (return empty string)
   - display_stats shows: Total Questions, Correct, Incorrect, Accuracy %, Missed Terms

Requirements:
- All methods must have type hints and docstrings
- Follow PEP 8 style guidelines
- No external dependencies
```

---

## Prompt 7: Quiz Engine (Core Logic)

```
Create a `quiz_engine.py` module that orchestrates a flashcard quiz session.

Architecture:
1. `SessionStats` dataclass:
   - total_questions: int
   - correct_count: int
   - missed_terms: List[str]
   - Properties: incorrect_count, accuracy (handles division by zero)

2. `QuizEngine` class:
   - Constructor accepts: Deck, QuizStrategy, UIProtocol (dependency injection)
   - `run()` method: initializes strategy, displays welcome, runs quiz loop,
     displays stats, returns SessionStats
   - Track missed terms without duplicates
   - Derive mode name from strategy class name

Requirements:
- Clean separation of concerns (engine does not do I/O directly)
- All functions must have type hints and docstrings
- Follow PEP 8 style guidelines
```

---

## Prompt 8: Unit Tests for Quiz Engine

```
Write a pytest test suite for the quiz_engine module.

Create a MockUI class that:
- Records all method calls for verification
- Returns predetermined answers from a list
- Implements the UIProtocol interface

Test classes needed:
1. TestSessionStats: initial state, accuracy calculation, edge cases
2. TestQuizEngineAllCorrect: 100% accuracy, welcome/stats displayed
3. TestQuizEngineAllIncorrect: 0% accuracy, missed terms tracked
4. TestQuizEngineMixedAnswers: partial accuracy, case-insensitive matching
5. TestQuizEngineWithRandomStrategy: all cards presented
6. TestQuizEngineWithAdaptiveStrategy: missed cards repeated, no repeat if all correct
7. TestQuizEngineEdgeCases: empty answers, whitespace, mode detection, no duplicate missed

Requirements:
- Use SequentialStrategy for predictable ordering in most tests
- Account for shuffled order when testing with AdaptiveStrategy/RandomStrategy
- Descriptive test names with type hints
```

---

## Prompt 9: CLI Entry Point with argparse

```
Rewrite `main.py` as the CLI entry point for the Flashcard Quizzer application.

Requirements:
1. Use argparse with:
   - Required positional argument: `file` (path to JSON flashcard data)
   - Optional argument: `--mode` (choices: sequential, random, adaptive; default: sequential)

2. `main(args=None)` function that:
   - Parses arguments (accepts optional args list for testing)
   - Loads the deck using load_deck_from_json
   - Creates the strategy using create_strategy
   - Initializes TerminalUI and QuizEngine
   - Runs the quiz
   - Returns exit codes: 0 for success, 1 for errors

3. Error handling:
   - Catch DataLoadError and display user-friendly message to stderr
   - Catch ValueError from create_strategy
   - Handle KeyboardInterrupt gracefully

4. Include module docstring with usage examples
5. All functions must have type hints and docstrings
```

---

## Prompt 10: CLI Integration Tests

```
Write pytest tests for main.py.

Test classes needed:
1. TestParseArguments:
   - File argument is required
   - File argument parsed correctly
   - Default mode is sequential
   - All modes parsed correctly (random, adaptive)
   - Invalid mode rejected (SystemExit)

2. TestMainFunction:
   - Nonexistent file returns exit code 1
   - Valid file with mocked input returns 0 (sequential mode)
   - Valid file with mocked input returns 0 (random mode)
   - Valid file with mocked input returns 0 (adaptive mode)
   - KeyboardInterrupt handled gracefully (returns 0)

Requirements:
- Use unittest.mock.patch on builtins.input to avoid blocking
- Use Path for cross-platform file path construction
- Provide enough mock answers for all cards including adaptive second pass
```
