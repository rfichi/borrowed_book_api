# Validation Checklist

**Version:** 1.0.0  
**Last Updated:** 2026-01-30  
**Tags:** #qa #testing #deployment

## Code Quality
- [ ] Code follows [Coding Conventions](coding-conventions.md).
- [ ] All functions have type hints.
- [ ] All public functions have docstrings.
- [ ] No hardcoded secrets.
- [ ] Imports are absolute and correct.

## Functional Testing
- [ ] Unit tests pass (`pytest`).
- [ ] API endpoints return correct status codes (200, 201, 400, 404, 401).
- [ ] Pydantic validation catches invalid inputs.

## Deployment Readiness
- [ ] `Dockerfile` builds successfully.
- [ ] `requirements.txt` is up to date.
- [ ] Environment variables are defined (but not valued) in code/config.
- [ ] `api_gateway_config.yaml` is updated for new endpoints.

## Security
- [ ] Authentication is enabled on endpoints.
- [ ] Dependencies are scanned for vulnerabilities (basic check).
- [ ] Least privilege principle applied to service accounts (if applicable).
