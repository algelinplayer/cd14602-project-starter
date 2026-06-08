# Step 1: Core Models & Data Ingestion - Implementation Guide

## Summary of Changes

This iteration implements the foundational data layer of the Flashcard Quizzer application: the domain models and the JSON data loading/validation system.

## Files Created

| File | Purpose |
|------|---------|
| `flashcard_quizzer/__init__.py` | Package initializer for the main application module |
| `flashcard_quizzer/models.py` | Domain models: `Flashcard` and `Deck` dataclasses |
| `flashcard_quizzer/data_loader.py` | JSON loading, schema validation, and error handling |
| `data/flashcards.json` | Sample flashcard data (10 server acronym cards) |
| `tests/__init__.py` | Package initializer for the test suite |
| `tests/test_data_loader.py` | 23 unit tests covering all data loading scenarios |
| `ai_edit_log.md` | AI interaction log (3 interactions documented) |
| `prompts.md` | Prompts used for AI code generation |

## Test Results

All 23 tests pass with **97% code coverage** on the `flashcard_quizzer` package:

```
flashcard_quizzer/__init__.py    0      0   100%
flashcard_quizzer/data_loader.py 48     2    96%
flashcard_quizzer/models.py      17     0   100%
TOTAL                            65     2    97%
```

## How to Run

```bash
cd project/starter
pip install pytest pytest-cov
python3 -m pytest tests/test_data_loader.py -v
python3 -m pytest tests/test_data_loader.py --cov=flashcard_quizzer --cov-report=term-missing
```

## Design Decisions

1. **Dataclasses over plain classes**: Cleaner syntax, automatic `__init__`, `__repr__`, and `__eq__` methods.
2. **Custom exception (`DataLoadError`)**: Provides user-friendly error messages instead of raw stack traces.
3. **Separate validation functions**: Makes the code testable and follows the Single Responsibility Principle.
4. **Case-insensitive answer checking**: Built into the `Flashcard.check_answer()` method with whitespace stripping.

## Next Step

Step 2 will implement the **Strategy Pattern** for quiz modes (Sequential, Random, Adaptive).
