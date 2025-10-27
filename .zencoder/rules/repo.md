---
description: Repository Information Overview
alwaysApply: true
---

# Vinyl Project Tracklist Extractor Information

## Summary
A desktop tool to extract tracklists from PDF cue sheets using a Vision LLM, compare them with mastered WAV durations, and review results in a Fluent-style PyQt GUI. The application follows a clean, hexagonal architecture with well-separated concerns.

## Structure
- **`app.py`**: Main entry point that assembles dependencies and launches the UI
- **`ui/`**: Presentation layer with main window, models, workers, and dialogs
- **`services/`**: Application services for analysis and export functionality
- **`core/`**: Domain logic and models with no external dependencies
- **`adapters/`**: Infrastructure adapters implementing core ports
- **`tests/`**: Comprehensive test suite with 97% coverage

## Language & Runtime
**Language**: Python
**Version**: 3.11 (recommended)
**Build System**: Standard Python setuptools
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- PyQt6 >= 6.4: GUI framework
- PyMuPDF >= 1.24: PDF processing
- pydantic >= 2.0: Data validation
- openai >= 1.30: AI integration
- pyqtgraph >= 0.13.0: Waveform visualization
- soundfile >= 0.12: Audio file processing
- python-dotenv >= 1.0.1: Environment configuration

**Development Dependencies**:
- pytest >= 8.0: Testing framework
- mypy >= 1.8: Type checking
- ruff >= 0.5: Linting
- black >= 24.0: Code formatting
- coverage >= 7.0: Test coverage

**Node.js Dependencies**:
- @fission-ai/openspec: ^0.12.0: OpenSpec tooling

## Build & Installation
```bash
# Windows (PowerShell)
py -3.11 -m venv .venv311
.\.venv311\Scripts\Activate.ps1
pip install -r requirements.txt

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Configuration
- Copy `.env.example` to `.env` and set API keys:
  - `OPENROUTER_API_KEY`: Required for LLM integration
  - Optional: `OPENROUTER_MODEL`, `OPENAI_API_KEY`, `OPENAI_MODEL`
- Settings stored in `settings.json` (ignored by Git)

## Usage
```bash
# Windows (PowerShell)
$env:QT_QPA_PLATFORM = "windows"
.\.venv\Scripts\python.exe .\app.py

# macOS/Linux
python app.py

# Headless/CI mode
QT_QPA_PLATFORM=offscreen python app.py
```

## Testing
**Framework**: pytest with pytest-qt and pytest-mock
**Test Location**: `tests/` directory
**Naming Convention**: `test_*.py` files with `test_*` functions
**Configuration**: `pytest.ini` with markers for unit, integration, gui, and slow tests
**Run Command**:
```bash
pytest -q  # Quick run
pytest -v  # Verbose output
pytest -m "not gui"  # Skip GUI tests
```

## Architecture
The project follows a hexagonal architecture pattern:
- **Domain Layer**: Core business logic in `core/` with no external dependencies
- **Application Layer**: Services in `services/` orchestrating domain operations
- **Adapter Layer**: External integrations in `adapters/` implementing core ports
- **UI Layer**: PyQt6-based presentation in `ui/` with dependency injection

## Quality Assurance
- **Type Safety**: mypy --strict passes
- **Code Quality**: ruff and black for linting and formatting
- **Test Coverage**: 97% with 55 passing tests
- **Development Workflow**: OpenSpec-driven development with conventional commits