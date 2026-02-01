---
name: "git-workflow-helper"
description: "Manages git branching, commits, and PRs according to project standards. Invoke when starting new tasks, saving changes, or preparing code for review."
---

# Git Workflow Helper

## 1. Branch Creation Strategy
**Trigger:** When the user requests to create a new branch.

**Steps:**
1. **Check Status:** Run `git status`.
2. **Handle Pending Changes:**
   - If changes exist: Run `git stash -um "stashing changes for {feature_name}"`.
   - If clean: Proceed.
3. **Sync Main:**
   - `git checkout main`
   - `git pull origin main`
4. **Create Branch:**
   - Format: `<type>/<name>`
   - Types: `feature`, `fix`, `hotfix`, `chore`, `refactor`, `hotfix`
   - Example: `git checkout -b feature/user-auth-endpoints`
5. **Restore Changes:**
   - If changes were stashed: `git stash apply`

## 2. Pre-Commit Quality Checks
**Trigger:** Before committing changes.

**Requirements:**
- **Update Changelog (MANDATORY):** The Agent MUST update `CHANGELOG.md` before committing any `feat`, `fix`, or significant `chore`.
  - Use the format defined in [Section 5: Changelog Format](#5-changelog-format).
  - This is a strict rule: No changelog update = No commit.
- **Automation:** The project uses `pre-commit` hooks. These will run automatically on `git commit`.
- **Manual Run:** To run checks manually, use `pre-commit run --all-files`.
- **Tests:** Ideally run `pytest` for relevant modules before committing.
- **Troubleshooting:** If `git commit` fails, check the output for pre-commit hook errors. Fix the reported issues (e.g., formatting, linting) and try committing again.

## 3. Commit Messages (Conventional Commits)
**Trigger:** When the user requests to commit their changes.
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
**Trigger:** When the user requests to push their changes to the remote repository.

**Steps:**
1. **Push:** `git push -u origin <current_branch_name>`
2. **Create PR:**
   - **Template:** The project uses a PR template. Fill out the sections for Summary, Testing, and Checklist.
   - **Title:** Use the same Conventional Commit format (e.g., "feat: Add user login endpoint").
   - **Target:** `main` branch.

<a id="5-changelog-format"></a>
## 5. Changelog Format
**Structure:**
```markdown
- [{version}] - {date}
- Status: {status}
- Changes:
  - {change_description}
- Fixes:
  - {fix_description}
- Breaking Changes
```
