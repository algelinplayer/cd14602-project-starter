# AI-Assisted Development Project Report

**Student Name:** [Your Name]
**Project Title:** Flashcard Quizzer CLI Application
**Date:** 2026-06-08

## Executive Summary

The Flashcard Quizzer is a command-line application that enables users to study flashcard decks using three distinct quiz modes: Sequential, Random, and Adaptive. The application loads flashcard data from JSON files, presents questions to the user, evaluates answers case-insensitively, and provides detailed session statistics including accuracy percentage and a list of missed terms.

The project was developed using AI-assisted coding practices, following the principles taught in the Udacity Vibe Engineering with Python course. Every module was generated through carefully crafted prompts using the CREATE framework, then rigorously reviewed for correctness, adherence to PEP 8, proper type hints, and comprehensive error handling. The iterative development process resulted in a well-tested application with 85 unit tests achieving 94% code coverage.

The collaboration with AI proved most valuable in generating boilerplate code, implementing design patterns correctly, and producing comprehensive test suites. However, the engineer's role remained critical in catching subtle bugs (such as random seed behavior after reset), ensuring proper integration between modules, and making architectural decisions about separation of concerns.

## Project Overview

### Problem Statement

Students need an effective tool for self-study that goes beyond simple flashcard flipping. The application needed to support multiple study strategies, particularly an adaptive mode that helps users focus on material they find difficult, while maintaining a clean codebase that demonstrates professional software engineering practices.

### Solution Approach

The solution employs a modular architecture with clear separation of concerns. The key design decisions were:

1. **Strategy Pattern** for quiz modes, allowing new modes to be added without modifying existing code.
2. **Dependency Injection** for the quiz engine, enabling isolated unit testing through a mock UI.
3. **Protocol-based abstraction** for the UI layer, decoupling presentation from business logic.
4. **Custom exceptions** with user-friendly messages instead of raw stack traces.

The technology stack consists of Python 3.8+ with only standard library dependencies for the application itself, and pytest with pytest-cov for the test suite.

### Final Features

- [x] Load and validate flashcard decks from JSON files
- [x] Sequential quiz mode (cards in original order)
- [x] Random quiz mode (shuffled card order)
- [x] Adaptive quiz mode (missed cards repeated for reinforcement)
- [x] Case-insensitive answer matching with whitespace trimming
- [x] Session statistics (total questions, accuracy %, missed terms)
- [x] Graceful error handling for all failure modes
- [x] CLI with argparse for file and mode selection

## AI Collaboration Experience

### AI Tools Used

- [x] Claude (Manus AI assistant)

### Collaboration Workflow

The development followed a structured workflow for each module:

1. **Prompt Engineering**: Each module was specified using a detailed prompt following the CREATE framework, including context, requirements, examples, constraints, and expected output format.
2. **Code Generation**: The AI generated the initial implementation based on the prompt.
3. **Code Review**: Every generated module was reviewed against a checklist: PEP 8 compliance, type hints, docstrings, error handling, no phantom dependencies, and correct logic.
4. **Testing**: A comprehensive test suite was generated and executed to verify behavior.
5. **Refinement**: Bugs discovered during testing were fixed and documented in the AI edit log.

### Most Valuable AI Interactions

#### Example 1: Strategy Pattern Implementation

**Context:** Implementing the Strategy Pattern for quiz modes required an abstract base class and three concrete strategies with different card selection algorithms.

**AI Prompt:** A detailed specification of the QuizStrategy ABC interface and the behavior of each concrete strategy, including the adaptive two-pass algorithm.

**AI Response:** A complete `quiz_modes.py` module with proper ABC inheritance, all three strategies, and a factory function.

**Your Changes:** Fixed a subtle bug in `RandomStrategy.reset()` where the seed was not being re-applied before reshuffling, causing non-deterministic behavior.

**Outcome:** A clean, extensible Strategy Pattern implementation that passes all 28 tests.

#### Example 2: Mock-Based Testing for Quiz Engine

**Context:** The quiz engine needed to be tested without real terminal I/O, requiring a mock UI that could provide predetermined answers and record all method calls.

**AI Prompt:** Specification for a MockUI class and comprehensive test scenarios covering all correct, all incorrect, mixed answers, and adaptive mode behavior.

**AI Response:** A complete test file with 23 tests using a well-designed MockUI class.

**Your Changes:** Fixed one test that provided answers in the wrong order for the adaptive strategy (which shuffles cards), requiring understanding of the seed-based shuffle order.

**Outcome:** Full test coverage of the quiz engine logic without any dependency on terminal I/O.

#### Example 3: Data Validation with Custom Exceptions

**Context:** The data loader needed to handle multiple failure modes gracefully without exposing raw Python exceptions to the user.

**AI Prompt:** Detailed specification of the expected JSON schema, all possible error conditions, and the requirement for user-friendly error messages.

**AI Response:** A comprehensive validation system with separate functions for deck structure and individual card validation.

**Your Changes:** Added validation for empty/whitespace-only strings and PermissionError handling that were missing from the initial generation.

**Outcome:** A robust data loading system that provides helpful, actionable error messages for every failure mode.

### Challenges with AI Collaboration

The primary challenges encountered were:

1. **Subtle state bugs**: The AI generated code that appeared correct but had subtle issues with mutable state (e.g., the random seed not being reapplied after reset). These bugs only surfaced during testing.
2. **Test-data alignment**: When testing randomized strategies, the AI sometimes assumed a specific card order without verifying it against the actual shuffle result for the given seed.
3. **Over-engineering tendency**: Initial prompts sometimes resulted in overly complex solutions. Adding explicit constraints ("Do NOT use external dependencies") helped keep the code focused.

## Software Engineering Practices

### Code Quality Measures

- [x] Type hints on all functions and methods
- [x] Comprehensive docstrings (module, class, and function level)
- [x] Custom exception classes with descriptive messages
- [x] Error handling that never exposes raw stack traces
- [x] Consistent code formatting following PEP 8

### Testing Strategy

The testing approach combined unit testing with integration testing:

- **Unit tests** verify individual functions and classes in isolation (data validation, strategy logic, stats computation).
- **Integration tests** verify the interaction between components (quiz engine with strategies, main function with all modules).
- **Mock-based testing** enables testing the quiz engine without real terminal I/O.
- **Test coverage**: 94% across the flashcard_quizzer package and main module.

### Design Patterns Used

- **Strategy Pattern** (`quiz_modes.py`): Encapsulates quiz mode algorithms behind a common interface, enabling runtime mode selection without conditional logic in the engine.
- **Factory Pattern** (`create_strategy()` function): Provides a clean API for instantiating strategies by name, centralizing creation logic.
- **Dependency Injection** (`QuizEngine` constructor): Accepts its dependencies (deck, strategy, UI) as constructor parameters, enabling flexible composition and testability.
- **Protocol** (`UIProtocol`): Defines a structural typing contract for the UI layer, allowing any compatible object (including mocks) to serve as the UI.

### Code Structure and Organization

The code is organized into a single package (`flashcard_quizzer`) with five modules, each with a single responsibility:

| Module | Responsibility |
|--------|---------------|
| `models.py` | Domain data structures (Flashcard, Deck) |
| `data_loader.py` | File I/O and data validation |
| `quiz_modes.py` | Card selection algorithms (Strategy Pattern) |
| `quiz_engine.py` | Session orchestration and state management |
| `ui.py` | User interaction (display and input) |

## Code Quality Analysis

### Metrics

| Metric | Value |
|--------|-------|
| Application lines of code | 1,029 |
| Test lines of code | 1,343 |
| Total test count | 85 |
| Test coverage | 94% |
| Classes | 11 |
| Functions/methods | 72 |
| External dependencies | 0 (application), 2 (testing: pytest, pytest-cov) |

### Self-Assessment

- **Code Readability:** 5 — Consistent naming, comprehensive docstrings, and clear module separation make the code easy to follow.
- **Code Maintainability:** 5 — The Strategy Pattern and dependency injection make it trivial to add new quiz modes or swap UI implementations.
- **Test Quality:** 5 — 85 tests covering unit, integration, and edge cases with a MockUI for isolated testing.
- **Documentation:** 5 — Every module, class, and function has docstrings. AI interactions are fully documented.

## Learning Outcomes

### Technical Skills Developed

- Implementing the Strategy Pattern in Python using ABC and concrete subclasses.
- Using Python's `typing.Protocol` for structural subtyping and dependency inversion.
- Writing testable code through dependency injection and mock objects.
- Building CLI applications with argparse.

### AI Collaboration Skills

- Crafting precise, constraint-rich prompts that minimize ambiguity.
- Reviewing AI output critically, especially for subtle state management bugs.
- Using seeds and deterministic parameters to make randomized code testable.
- Documenting the AI collaboration process for reproducibility.

### Software Engineering Insights

- Design patterns are not just theoretical — they directly improve testability and extensibility.
- Separation of concerns (UI from logic) is essential for automated testing.
- Custom exceptions with helpful messages dramatically improve the user experience.
- Test-driven iteration catches bugs that code review alone might miss.

## Reflection

### What Worked Well

The CREATE framework for prompting produced consistently high-quality initial code. The iterative approach (generate, review, test, fix) caught all bugs before they could reach production. The Strategy Pattern proved its value when the adaptive mode was added — no changes to the engine were needed.

### What Could Be Improved

- The adaptive strategy could be more sophisticated (e.g., spaced repetition with decay).
- The UI could support color output for terminals that support ANSI codes.
- A configuration file could allow users to customize quiz behavior.

### Future Enhancements

- Add a spaced repetition algorithm (SM-2) as a fourth strategy.
- Support multiple file formats (CSV, YAML) in addition to JSON.
- Add a "hint" feature that reveals partial answers.
- Implement persistent progress tracking across sessions.
- Add a web-based UI as an alternative to the terminal.

## Conclusion

This project demonstrated that AI-assisted development is most effective when the engineer maintains a strong understanding of software architecture and testing practices. The AI excels at generating well-structured code from precise specifications, but the engineer's role in reviewing, testing, and fixing subtle bugs remains irreplaceable. The combination of the CREATE framework for prompting, rigorous code review, and comprehensive testing produced a production-quality application in a fraction of the time that manual coding alone would require.

## Appendices

### Appendix A: AI Interaction Log

See `ai_edit_log.md` for the complete log of 8 AI interactions, including prompts, reviews, and decisions.

### Appendix B: Code Statistics

```
Test Results: 85 passed
Coverage:     94% (flashcard_quizzer + main)

Per-module coverage:
  models.py        100%
  data_loader.py    96%
  quiz_modes.py     94%
  quiz_engine.py   100%
  ui.py             92%
  main.py           79%
```

### Appendix C: Additional Resources

- Udacity Vibe Engineering with Python Course (nd770)
- "Design Patterns: Elements of Reusable Object-Oriented Software" (Gang of Four)
- Python `typing.Protocol` documentation (PEP 544)
- pytest documentation (https://docs.pytest.org/)
