---
name: "command-execution-rules"
description: "Enforces rules for CLI commands, planning phases, and OS-specific syntax. Invoke when running commands, creating plans, or when the user skips an action."
---

# Command Execution & Planning Rules

## 1. Skipped Commands = Skipped Intent
**Rule:** If a user SKIPS a command (e.g., `mkdir`, `touch`), DO NOT attempt to achieve the result via other means (like the `Write` tool).
- **Reasoning:** A skip often indicates the user *disagrees* with the action, not just the method.
- **Action:** Stop the specific task, explain that it was skipped, and ask for clarification if needed.

## 2. Windows PowerShell Priority
**Rule:** Always assume the environment is **Windows PowerShell**.
- **Syntax:** Use `;` (semicolon) for chaining commands, NOT `&&`.
  - ✅ Correct: `cd dir; ls`
  - ❌ Incorrect: `cd dir && ls`
- **Path Separators:** Use backslashes `\` for paths in display text, but forward slashes `/` are generally acceptable in many PowerShell commands (though `\` is safer).
- **Tooling:** Prefer PowerShell-native cmdlets or cross-platform standard tools.

## 3. Planning Phase Isolation
**Rule:** When the user asks to "Plan", "Design", or "Think about" a task:
- **Strict Read-Only:** DO NOT create files, directories, or run modifying commands.
- **Output:** Provide a clear, text-based plan or explanation first.
- **Approval:** Explicitly wait for user confirmation before executing the plan (unless the user said "Plan and execute").

## 4. General Safety
- **Verification:** Always verify a file exists before trying to read or edit it.
- **Destructive Actions:** Double-check before using `rm` or `DeleteFile`.

## 5. Explicit Consent for Git Operations
**Rule:** NEVER proactively generate or execute `git commit` or `git push` commands unless the user has explicitly requested them in the current turn.
- **Trigger:** Only prompt for git operations if the user asks (e.g., "commit this", "save changes", "push to remote").
- **Behavior:**
    - If code changes are made: Verify the changes locally (tests, linting).
    - Report success: "Changes applied and verified."
    - Optional Suggestion: "Would you like me to commit these changes?" (Text only, no tool call).
- **Reasoning:** Prevents cluttering the commit history and allows the user to batch changes or review them before committing.

## 6. Atomic Git Operations
**Rule:** NEVER chain `git commit` and `git push` in the same command execution (e.g., `git commit -m "..."; git push`).
- **Process:**
  1. Execute `git add` and `git commit` first.
  2. Verify the commit succeeded (check for exit code 0 and no pre-commit hook failures).
  3. ONLY if the commit was successful, execute `git push` in a subsequent step or tool call.
- **Reasoning:** Pre-commit hooks often fail and modify files. Chaining push causes confusion or pushes partial/incorrect states.
