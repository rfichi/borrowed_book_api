# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-02-02
- Status: Added
- Changes:
  - Added CI/CD pipeline for automated testing with pytest and coverage.
  - Added pytest and pytest-cov dependencies to all services.
  - Configured GitHub Actions to enforce >70% test coverage.

## [0.4.4] - 2026-02-02
- Status: Optimized
- Changes:
  - Optimized Dockerfiles using multi-stage builds.
  - Updated Cloud Build pipeline to use caching and parallel builds.
  - Reduced build time and image size.

## [0.4.3] - 2026-02-02
- Status: Refactored
- Changes:
  - Removed legacy root-level `models/`, `schemas/`, and `routers/` folders.
  - Decoupled services to use their own internal dependencies.
  - Added MIT License.

## [0.2.0] - 2026-02-02
- Status: Added
- Changes:
  - Created `.trae` folder with project skills and rules.
  - Defined `git-workflow-helper` skill.
  - Defined `project-guidelines` skill.
