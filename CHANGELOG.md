# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.4] - 2026-02-03

### Added
- Created `tests/e2e` directory with `pytest` based E2E tests (`test_user_flow.py`).
- Created `tests/unit` and `tests/integration` directories for better test organization.
- Registered `e2e` marker in `pyproject.toml`.

### Changed
- Refactored project structure: Moved existing unit tests to `tests/unit/`.
- Updated `cloudbuild.yaml` to run `pytest tests/e2e` instead of `verify_gateway.py` script.
- Updated `conftest.py` files to reflect new directory depth.

## [0.5.3] - 2026-02-02

### Added
- Integrated E2E smoke tests into Cloud Build pipeline.
- Added `demo/verify_gateway.py` execution as a post-deployment verification step.
- Configured Secret Manager integration for API Key injection in CI/CD.

## [0.5.2] - 2026-02-02

### Changed
- Updated CI/CD pipeline to trigger only on pull requests to main, removing push triggers.

## [0.5.1] - 2026-02-02
