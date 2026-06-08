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
