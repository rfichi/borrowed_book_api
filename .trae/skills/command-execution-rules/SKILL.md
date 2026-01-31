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
