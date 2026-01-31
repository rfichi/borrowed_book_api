---
name: "git-workflow-helper"
description: "Manages git branching, commits, and PRs according to project standards. Invoke when starting new tasks, saving changes, or preparing code for review."
---

# Git Workflow Helper

## 1. Branch Creation Strategy
**Trigger:** When starting a new task (feature, fix, hotfix).

**Steps:**
1. **Check Status:** Run `git status`.
2. **Handle Pending Changes:**
   - If changes exist: Run `git stash save "Pre-branch switch"`.
   - If clean: Proceed.
3. **Sync Main:**
   - `git checkout main`
   - `git pull origin main`
4. **Create Branch:**
   - Format: `<type>/<name>`
   - Types: `feature`, `fix`, `hotfix`
   - Example: `git checkout -b feature/user-auth-endpoints`
5. **Restore Changes:**
   - If changes were stashed: `git stash pop`

## 2. Pre-Commit Quality Checks
**Trigger:** Before committing changes.

**Requirements:**
- **Automation:** The project uses `pre-commit` hooks. These will run automatically on `git commit`.
- **Manual Run:** To run checks manually, use `pre-commit run --all-files`.
- **Tests:** Ideally run `pytest` for relevant modules before committing.

## 3. Commit Messages (Conventional Commits)
**Standard:** Use [Conventional Commits](https://www.conventionalcommits.org/).

**Format:** `<type>(<scope>): <description>`

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples:**
- `feat(auth): add JWT token refresh endpoint`
- `fix(users): resolve null pointer in user profile update`
- `docs(readme): update installation instructions`

## 4. Pushing & Pull Requests
**Trigger:** When the task is complete.

**Steps:**
1. **Push:** `git push -u origin <current_branch_name>`
2. **Create PR:**
   - **Template:** The project uses a PR template. Fill out the sections for Summary, Testing, and Checklist.
   - **Title:** Use the same Conventional Commit format (e.g., "feat: Add user login endpoint").
   - **Target:** `main` branch.
