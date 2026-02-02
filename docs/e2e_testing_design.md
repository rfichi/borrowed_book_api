# E2E Testing Design & Implementation Plan

## 1. Objective
Automate the execution of `demo/verify_gateway.py` after a successful deployment to Google Cloud Platform to verify that all microservices and the API Gateway are functioning correctly together.

## 2. Current State
- **Deployment**: Managed by `cloudbuild.yaml` (Build -> Push -> Deploy).
- **Testing**: Manual execution of `demo/verify_gateway.py`.
- **Gap**: No automated verification after deployment; risks silent failures in production.

## 3. Architecture Options

### Option A: Integrated Cloud Build Step (Recommended)
Add the E2E test as the final step in the existing `cloudbuild.yaml`.
- **Flow**: Build Images -> Push Images -> Deploy Services -> **Run E2E Tests**.
- **Pros**:
  - Immediate feedback.
  - If tests fail, the build is marked as FAILED (clear signal).
  - No complex event orchestration required.
- **Cons**: Adds execution time to the main build pipeline.

### Option B: Decoupled Pipeline (Event-Driven)
Trigger a separate Cloud Build pipeline upon completion of the deployment pipeline.
- **Flow**: Deploy Pipeline -> Pub/Sub Message -> E2E Pipeline -> Run Tests.
- **Pros**:
  - Keeps deployment pipeline fast.
  - Can run extensive/long-running test suites without blocking the deploy job.
- **Cons**:
  - More complex setup (Pub/Sub topics, Cloud Functions or Triggers).
  - "Deployment Success" in the first pipeline doesn't guarantee "Functional Success".

## 4. Recommendation
Given the current scope (a smoke test script `verify_gateway.py` taking < 10 seconds), **Option A (Integrated Step)** is superior. It ensures that a "Green" build means the system is actually working.

## 5. Implementation Plan

### Step 1: Prepare the Test Script
The current `demo/verify_gateway.py` prints output but does not return non-zero exit codes on failure. Cloud Build determines success/failure based on exit codes.
- **Action**: Refactor `demo/verify_gateway.py` to:
  - Use `sys.exit(1)` when assertions fail.
  - Use `sys.exit(0)` when all tests pass.
  - (Optional) Wrap in `pytest` for better reporting, but raw script is fine for simple smoke tests.

### Step 2: Secret Management
The script requires `API_KEY`.
- **Action**:
  - Ensure the API Key is stored in Google Secret Manager (e.g., `borrow-api-key`).
  - Configure Cloud Build to access this secret and inject it as an environment variable.

### Step 3: Update `cloudbuild.yaml`
Add a final step to the pipeline:
```yaml
  # 6. Run E2E Smoke Tests
  - name: 'python:3.10-slim'
    entrypoint: /bin/sh
    args:
      - -c
      - |
        pip install httpx
        python demo/verify_gateway.py
    secretEnv: ['API_KEY']
    id: 'e2e-tests'
    waitFor: ['deploy-users', 'deploy-books', 'deploy-borrow']
```

### Step 4: Service Account Permissions
Ensure the Cloud Build Service Account has permission to access the Secret Manager secret (`roles/secretmanager.secretAccessor`).

## 6. Next Steps
1. Refactor `demo/verify_gateway.py`.
2. Verify Secret Manager setup.
3. Update `cloudbuild.yaml`.
