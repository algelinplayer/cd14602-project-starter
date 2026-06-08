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
