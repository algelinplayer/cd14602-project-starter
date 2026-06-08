# AI-Assisted Development Project Report

**Project Title:** Flashcard Quizzer CLI Application
**Date:** 2026-06-08

## Executive Summary

The Flashcard Quizzer is a command-line application that enables users to study flashcard decks using three distinct quiz modes: Sequential, Random, and Adaptive. The application loads flashcard data from JSON files, presents questions, evaluates answers case-insensitively, and provides session statistics including accuracy percentage and missed terms.

The project was developed using AI-assisted coding practices following the Udacity Vibe Engineering course. Every module was generated through carefully crafted prompts, then reviewed for correctness, PEP 8 compliance, type hints, and error handling. The iterative process resulted in a well-tested application with 100 unit tests achieving 94% code coverage.

## Project Overview

### Problem Statement

Students need an effective self-study tool that goes beyond simple flashcard flipping. The application supports multiple study strategies, particularly an adaptive mode that helps users focus on difficult material, while maintaining a clean codebase demonstrating professional software engineering practices.

### Solution Approach

The solution employs a modular architecture with clear separation of concerns:

1. **Strategy Pattern** for quiz modes, allowing new modes without modifying existing code.
2. **Dependency Injection** for the quiz engine, enabling isolated unit testing.
3. **Protocol-based abstraction** for the UI layer, decoupling presentation from logic.
4. **Custom exceptions** with user-friendly messages instead of raw stack traces.

The technology stack uses Python 3.10+ with only standard library dependencies for the application, and pytest with pytest-cov for testing.

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

Each module followed a structured workflow: (1) Prompt engineering using the CREATE framework, (2) Code generation, (3) Code review against a checklist (PEP 8, type hints, docstrings, error handling, no phantom dependencies), (4) Testing, and (5) Refinement of any bugs found.

### Most Valuable AI Interactions

#### Example 1: Strategy Pattern Implementation

**Context:** Implementing the Strategy Pattern for quiz modes required an ABC and three concrete strategies.
**AI Prompt:** Detailed specification of the QuizStrategy interface and each strategy's behavior.
**AI Response:** Complete `quiz_modes.py` with proper ABC inheritance, three strategies, and a factory function.
**Your Changes:** Fixed a bug in `RandomStrategy.reset()` where the seed was not re-applied before reshuffling.
**Outcome:** Clean Strategy Pattern passing all 28 tests.

#### Example 2: Mock-Based Testing for Quiz Engine

**Context:** The quiz engine needed testing without real terminal I/O.
**AI Prompt:** Specification for a MockUI class and comprehensive test scenarios.
**AI Response:** Complete test file with 23 tests using a MockUI class.
**Your Changes:** Fixed one test that provided answers in the wrong order for the adaptive strategy's seeded shuffle.
**Outcome:** Full test coverage of quiz engine logic without terminal dependency.

#### Example 3: Data Validation with Custom Exceptions

**Context:** The data loader needed graceful handling of multiple failure modes.
**AI Prompt:** Specification of the JSON schema, error conditions, and user-friendly messages.
**AI Response:** Comprehensive validation with separate functions for deck structure and card validation.
**Your Changes:** Added whitespace-only string validation and PermissionError handling.
**Outcome:** Robust data loading with actionable error messages for every failure mode.

### Challenges with AI Collaboration

1. **Subtle state bugs**: AI-generated code had issues with mutable state (random seed not reapplied after reset), only surfacing during testing.
2. **Test-data alignment**: AI sometimes assumed specific card orders without verifying against the actual shuffle for a given seed.
3. **Over-engineering**: Initial prompts sometimes produced overly complex solutions; explicit constraints helped.

## Technical Challenges and Solutions

### Challenge 1: Deterministic Random Strategy Testing

**Problem:** The RandomStrategy shuffles cards, making test assertions unpredictable.
**Solution:** Added seed support to RandomStrategy and AdaptiveStrategy, allowing reproducible shuffles in tests.
**AI Involvement:** AI generated the initial strategy; review and testing exposed the seed-reset issue.
**Lessons Learned:** Randomized behavior needs deterministic test hooks via seed parameters.

### Challenge 2: Self-Contained CLI Tests

**Problem:** CLI integration tests initially depended on a project-level `data/flashcards.json` file, creating fragile coupling.
**Solution:** Rewrote CLI tests to use pytest `tmp_path` fixtures that create their own valid deck data.
**AI Involvement:** AI generated the initial tests with file-path dependencies; review identified the fragility.
**Lessons Learned:** Tests should control their own fixtures to avoid packaging-related failures.

## Software Engineering Practices

### Code Quality Measures

- [x] Code formatting with Black (all files pass `black --check .`)
- [x] Linting with flake8 (zero violations at max-line-length=100)
- [x] Type hints on all functions and methods
- [x] Comprehensive docstrings at module, class, and function levels
- [x] Custom exception classes with descriptive messages

### Testing Strategy

Unit tests verify individual functions in isolation; integration tests verify component interaction; mock-based testing enables quiz engine testing without I/O. Coverage: 94% across all application modules.

### Design Patterns Used

- **Strategy Pattern** (`quiz_modes.py`): The primary design pattern. Encapsulates quiz mode algorithms behind a common interface, enabling runtime mode selection without conditional logic in the engine.
- Supporting techniques: Factory function (`create_strategy()`), Dependency Injection (`QuizEngine` constructor), Protocol (`UIProtocol`).

## Code Quality Analysis

### Metrics

| Metric | Value |
|--------|-------|
| Total test count | 100 |
| Test coverage | 94% |
| Linting (flake8) | 0 violations |
| Formatting (black) | All files pass |
| External runtime dependencies | 0 |

### Self-Assessment

- **Code Readability:** 5 — Consistent naming, comprehensive docstrings, clear module separation.
- **Code Maintainability:** 5 — Strategy Pattern and DI make adding new modes trivial.
- **Test Quality:** 5 — 100 tests covering unit, integration, and edge cases with self-contained fixtures.
- **Documentation:** 5 — Every module, class, and function has docstrings; AI interactions fully documented.

## Learning Outcomes

### Technical Skills Developed

- Implementing the Strategy Pattern using ABC and concrete subclasses.
- Using `typing.Protocol` for structural subtyping and dependency inversion.
- Writing testable code through dependency injection and mock objects.
- Building CLI applications with argparse.

### AI Collaboration Skills

- Crafting precise, constraint-rich prompts that minimize ambiguity.
- Reviewing AI output critically for subtle state management bugs.
- Using seeds and deterministic parameters to make randomized code testable.

## Reflection

### What Worked Well

The CREATE framework for prompting produced consistently high-quality initial code. The iterative approach (generate, review, test, fix) caught all bugs before production. The Strategy Pattern proved its value when adding the adaptive mode — no engine changes were needed.

### What Could Be Improved

- The adaptive strategy could use spaced repetition (SM-2) for better learning outcomes.
- A configuration file could allow users to customize quiz behavior.
- Tests could include property-based testing for stronger validation guarantees.

## Conclusion

This project demonstrated that AI-assisted development is most effective when the engineer maintains strong understanding of software architecture and testing. AI excels at generating well-structured code from precise specifications, but the engineer's role in reviewing, testing, and fixing subtle bugs remains irreplaceable. The combination of structured prompting, rigorous review, and comprehensive testing produced a production-quality application efficiently.

## Appendices

### Appendix A: AI Interaction Log

See `ai_edit_log.md` for the complete log of 10 AI interactions.

### Appendix B: Final Verification

```
$ black --check .
All done! 17 files would be left unchanged.

$ flake8 . --max-line-length=100
(no output — zero violations)

$ pytest tests/ --cov=flashcard_quizzer --cov=main --cov=utils -q
100 passed
TOTAL coverage: 94%
```
