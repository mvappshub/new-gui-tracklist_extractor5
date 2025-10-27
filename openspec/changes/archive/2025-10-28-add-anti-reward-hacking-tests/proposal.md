## Why
Current AI adapter and PDF extractor tests rely almost exclusively on happy-path mocks and never validate real wire-format payloads (messages, `response_format`, image encoding) or error handling paths. `VlmClient` (`adapters/ai/vlm.py`) has zero coverage, and helper flows in `adapters/audio/ai_helpers.py` are only verified indirectly through mocks. `extract_pdf_tracklist` lacks no-network end-to-end coverage. Domain utilities such as `StrictFilenameParser`, `TracklistParser`, and `compare_data` have limited negative tests, letting regressions slip through. GUI tests manually spin up `QApplication` instances, causing inconsistent hygiene. There are also no global test safeguards (network isolation, API key resets), no architecture/complexity guard-rails, no snapshot verification, and workers/export flows miss contract testing. Together these gaps allow “reward hacking”: implementations can drift or be naively rewritten while the test suite still passes. Tight guard-rails are required before upcoming refactors.

## What Changes
- Introduce mandatory test safeguards (F-PRE0) that block network access and clear AI API keys, alongside an initial “Pre-F-PRE0” stability commit.
- Add VlmClient contract tests (F-PRE1) covering `_to_data_url`, OpenAI payload structure (`messages`, `response_format={"type": "json_object"}`, `temperature=0.0`), empty/backtick wrapped responses, and missing API key behaviour.
- Add ai_helpers contract tests (F-PRE2) validating request assembly, JSON parsing robustness, empty inputs, malformed responses, and `merge_ai_results`.
- Add PDF extractor integration tests (F-PRE3) using mocked renderer/client to cover valid responses, empty payloads, no pages, AI exceptions, and multi-page aggregation.
- Add parser/comparison sanity tests (F-PRE4) for conflicting filename patterns, negative cases, tolerance boundaries, negative differences, malformed durations, plus doctests.
- Fix GUI test hygiene (F-PRE5) by converting `tests/test_gui_simple.py` to rely on the shared `qapp` fixture and pytest-qt event-loop helpers.
- Establish architecture & CI guard-rails (F-PRE6) via pytest-arch/import-linter layering checks, radon complexity gate, forbidden-construct greps, and snapshot tests for enums/models.
- Unify GUI tests’ event-loop handling (F-PRE7) to remove `app.exec()` usage and rely on `qtbot.waitUntil`.
- Isolate QSettings/resources (F-PRE8) with fixtures and CI verification of `_icons_rc.py`.
- Add worker/export contract and negative I/O tests (F-PRE9), and finish with a “Post-F-PRE9” stability commit.
- Author a new testing strategy spec capturing anti-reward-hacking principles and requirements across adapters, extraction, parsers, GUI, guard-rails, QSettings, and workers.

## Impact
- Adds new change under `openspec/changes/add-anti-reward-hacking-tests/`.
- Introduces new spec `openspec/changes/add-anti-reward-hacking-tests/specs/testing/spec.md`.
- Creates multiple new test modules (`tests/test_ai_contracts.py`, `tests/test_pdf_extractor_contract.py`, `tests/test_parser_sanity.py`, `tests/test_architecture.py`, `tests/test_worker_contracts.py`, snapshots, etc.) and updates existing fixtures/tests (`tests/conftest.py`, `tests/test_gui_simple.py`).
- Requires tooling updates (CI scripts, radon/import-linter configs) to enforce guard-rails.
- Temporarily increases CI runtime due to expanded coverage but significantly reduces risk of silent regressions.
