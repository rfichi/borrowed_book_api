# AI Agent Knowledge Base

This directory contains the persistent knowledge repository for the TRAE AI assistant. It is designed to provide context, rules, and memory to the AI model to ensure reliable and consistent decision-making.

## Directory Structure

- **`decision-rules.md`**: Explicit frameworks and criteria for making architectural and implementation decisions.
- **`coding-conventions.md`**: Standards for code style, structure, and libraries (Python/FastAPI).
- **`architectural-patterns.md`**: Documentation of the microservices architecture, API Gateway, and Cloud Run patterns.
- **`context-memory.md`**: A log of key decisions, active context, and session history.
- **`validation-checklist.md`**: QA standards for validating code and deployments.
- **`scripts/`**: Utility scripts for the AI agent.
  - `context_loader.py`: Script to aggregate and load these markdown files into the AI's context window.

## Usage

The AI agent should be instructed (or configured) to run `.ai/scripts/context_loader.py` at the start of a session or when needing to refresh its understanding of the project rules.

## Maintenance

These files should be updated whenever:
- A new architectural pattern is adopted.
- A significant decision is made.
- Coding standards change.
- A new feature branch is started.
