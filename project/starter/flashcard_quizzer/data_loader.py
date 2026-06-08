"""Data loading and validation module for the Flashcard Quizzer.

This module handles reading flashcard data from JSON files, validating
the structure of the data, and converting it into domain model objects.
It provides graceful error handling for missing files and malformed data.
"""

import json
from pathlib import Path
from typing import List

from flashcard_quizzer.models import Deck, Flashcard


class DataLoadError(Exception):
    """Custom exception for data loading failures.

    Raised when a flashcard file cannot be loaded or contains
    invalid data that does not conform to the expected schema.
    """

    pass


def validate_card_data(card_data: dict, index: int) -> None:
    """Validate that a single card entry has the required fields.

    Args:
        card_data: A dictionary representing a single flashcard.
        index: The position of the card in the list (for error messages).

    Raises:
        DataLoadError: If the card is missing required 'front' or 'back' fields,
            or if the fields are not strings.
    """
    if not isinstance(card_data, dict):
        raise DataLoadError(
            f"Card at index {index} is not a valid object. "
            f"Expected a dictionary with 'front' and 'back' keys."
        )

    if "front" not in card_data:
        raise DataLoadError(
            f"Card at index {index} is missing the required 'front' field."
        )

    if "back" not in card_data:
        raise DataLoadError(
            f"Card at index {index} is missing the required 'back' field."
        )

    if not isinstance(card_data["front"], str) or not card_data["front"].strip():
        raise DataLoadError(
            f"Card at index {index} has an invalid 'front' field. "
            f"It must be a non-empty string."
        )

    if not isinstance(card_data["back"], str) or not card_data["back"].strip():
        raise DataLoadError(
            f"Card at index {index} has an invalid 'back' field. "
            f"It must be a non-empty string."
        )


def validate_deck_structure(data: dict) -> None:
    """Validate the top-level structure of the flashcard deck JSON.

    The expected schema is:
    {
        "deck_name": "string",
        "cards": [{"front": "string", "back": "string"}, ...]
    }

    Args:
        data: The parsed JSON data as a dictionary.

    Raises:
        DataLoadError: If the structure does not match the expected schema.
    """
    if not isinstance(data, dict):
        raise DataLoadError(
            "Invalid JSON structure. Expected a JSON object with "
            "'deck_name' and 'cards' fields."
        )

    if "deck_name" not in data:
        raise DataLoadError("Missing required field 'deck_name' in the JSON file.")

    if "cards" not in data:
        raise DataLoadError("Missing required field 'cards' in the JSON file.")

    if not isinstance(data["cards"], list):
        raise DataLoadError("The 'cards' field must be a list of flashcard objects.")

    if len(data["cards"]) == 0:
        raise DataLoadError(
            "The 'cards' list is empty. At least one flashcard is required."
        )


def load_deck_from_json(file_path: str) -> Deck:
    """Load a flashcard deck from a JSON file.

    This function reads the specified JSON file, validates its structure,
    and returns a Deck object populated with Flashcard instances.

    Args:
        file_path: The path to the JSON file containing flashcard data.

    Returns:
        A Deck object containing the loaded flashcards.

    Raises:
        DataLoadError: If the file is not found, contains invalid JSON,
            or does not conform to the expected schema.
    """
    path = Path(file_path)

    if not path.exists():
        raise DataLoadError(
            f"File not found: '{file_path}'. "
            f"Please provide a valid path to a flashcard JSON file."
        )

    if not path.is_file():
        raise DataLoadError(
            f"Path '{file_path}' is not a file. "
            f"Please provide a path to a JSON file."
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataLoadError(
            f"Invalid JSON in '{file_path}': {e}. "
            f"Please ensure the file contains valid JSON."
        )
    except PermissionError:
        raise DataLoadError(
            f"Permission denied when reading '{file_path}'. "
            f"Please check file permissions."
        )

    validate_deck_structure(data)

    cards: List[Flashcard] = []
    for index, card_data in enumerate(data["cards"]):
        validate_card_data(card_data, index)
        cards.append(Flashcard(front=card_data["front"], back=card_data["back"]))

    return Deck(name=data["deck_name"], cards=cards)
