# Flashcard Quizzer

A production-ready CLI flashcard quiz application built using AI-assisted development practices. This project demonstrates effective collaboration with AI coding assistants while maintaining high software engineering standards, including design patterns, comprehensive testing, and clean architecture.

## Features

- **Multiple Quiz Modes**: Sequential, Random, and Adaptive (prioritizes missed cards).
- **Strategy Pattern**: Clean, extensible architecture for adding new quiz modes.
- **Robust Data Validation**: Graceful error handling for missing or malformed JSON files.
- **Session Statistics**: Tracks accuracy, correct/incorrect counts, and missed terms.
- **Case-Insensitive Matching**: Flexible answer comparison with whitespace trimming.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py data/flashcards.json --mode sequential
   ```

4. **Run tests:**
   ```bash
   pytest
   ```

## Usage

```bash
# Sequential mode (default) - cards in original order
python main.py data/flashcards.json

# Random mode - shuffled card order
python main.py data/flashcards.json --mode random

# Adaptive mode - missed cards are repeated for reinforcement
python main.py data/flashcards.json --mode adaptive
```

### Command-Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `file` | Yes | Path to the JSON file containing flashcard data |
| `--mode` | No | Quiz mode: `sequential` (default), `random`, or `adaptive` |

### Flashcard JSON Format

The application expects a JSON file with the following structure:

```json
{
    "deck_name": "My Flashcard Deck",
    "cards": [
        {"front": "What does API stand for?", "back": "Application Programming Interface"},
        {"front": "What does REST stand for?", "back": "Representational State Transfer"}
    ]
}
```

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
flashcard_quizzer/
├── models.py        # Domain models (Flashcard, Deck dataclasses)
├── data_loader.py   # JSON loading and schema validation
├── quiz_modes.py    # Strategy Pattern (Sequential, Random, Adaptive)
├── quiz_engine.py   # Core quiz orchestration logic
└── ui.py            # Terminal I/O (Protocol + TerminalUI)
```

### Design Patterns Used

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| **Strategy** | `QuizStrategy` ABC with 3 concrete strategies | Swap quiz modes without modifying engine logic |
| **Factory** | `create_strategy()` function | Instantiate strategies by name |
| **Dependency Injection** | `QuizEngine` constructor | Decouple engine from UI and strategy |
| **Protocol** | `UIProtocol` | Enable mock-based testing without real I/O |

## Testing

The project includes a comprehensive test suite with **85 tests** achieving **94% code coverage**.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=flashcard_quizzer --cov=main --cov-report=term-missing

# Run a specific test file
pytest tests/test_quiz_modes.py -v
```

### Test Structure

| Test File | Tests | Coverage Target |
|-----------|-------|-----------------|
| `test_data_loader.py` | 23 | Data loading, validation, error handling |
| `test_quiz_modes.py` | 28 | All strategy behaviors and factory |
| `test_quiz_engine.py` | 23 | Quiz loop, stats, integration with strategies |
| `test_main.py` | 11 | CLI argument parsing and main function |

## AI Collaboration

This project was developed using AI-assisted coding practices as taught in the Udacity Vibe Engineering course. All AI interactions are documented in:

- **`ai_edit_log.md`** — Detailed log of each AI interaction, including prompts, reviews, and decisions.
- **`prompts.md`** — The specific prompts used for code generation.

### Key Principles Applied

1. **Review every line**: All AI-generated code was reviewed for correctness, style, and security.
2. **Test thoroughly**: Tests were written alongside implementation to verify behavior.
3. **Document decisions**: Every acceptance or modification of AI output is recorded.
4. **Iterate and refine**: Bugs found during testing were fixed and documented.

## Project Structure

```
starter/
├── main.py                     # CLI entry point (argparse)
├── flashcard_quizzer/          # Main application package
│   ├── __init__.py
│   ├── models.py               # Flashcard and Deck dataclasses
│   ├── data_loader.py          # JSON loading with validation
│   ├── quiz_modes.py           # Strategy Pattern implementation
│   ├── quiz_engine.py          # Core quiz orchestration
│   └── ui.py                   # Terminal UI (Protocol + implementation)
├── tests/                      # Comprehensive test suite
│   ├── __init__.py
│   ├── test_data_loader.py     # Data loading tests
│   ├── test_quiz_modes.py      # Strategy pattern tests
│   ├── test_quiz_engine.py     # Quiz engine tests (with MockUI)
│   └── test_main.py            # CLI integration tests
├── data/                       # Sample flashcard data
│   └── flashcards.json
├── docs/                       # Project documentation
│   ├── design_patterns.md
│   ├── project_rubric.md
│   └── report_template.md
├── ai_edit_log.md              # AI interaction log
├── prompts.md                  # Prompt log
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Built With

- [Python](https://www.python.org/) — Core programming language
- [pytest](https://docs.pytest.org/) — Testing framework
- [pytest-cov](https://pytest-cov.readthedocs.io/) — Coverage reporting
- [argparse](https://docs.python.org/3/library/argparse.html) — CLI argument parsing (stdlib)

## License

[License](LICENSE.txt)
