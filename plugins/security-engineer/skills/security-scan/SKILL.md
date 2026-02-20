---
name: security-scan
description: "Run a security checklist against recent code changes. Use before committing, during PR review, or when touching auth/input/network code."
user-invokable: true
context: fork
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[file path, 'staged', or 'branch' for full branch diff]"
---

# Security Scan

Scan code for security issues.

## Input

- `$ARGUMENTS` = file path, "staged" (staged changes), or "branch" (full branch diff vs main)
- If empty, defaults to staged changes

## Process

### 1. Identify Scope

- File path → scan that file
- "staged" or empty → `git diff --cached --name-only`
- "branch" → `git diff main...HEAD --name-only`

Read each file in scope.

### 2. Check Each Category

**Injection Risks**

- SQL: string concatenation in queries, raw SQL, f-strings with SQL keywords
- Command: subprocess calls with variable input or shell=True
- Path traversal: user input in file paths without validation
- XSS: unescaped user input in templates or HTML output

**Secrets and Credentials**

- Hardcoded passwords, API keys, tokens, connection strings
- Environment files or credential files being committed
- Credentials embedded in URLs or query parameters

**Authentication and Authorization**

- Missing auth checks on protected endpoints
- Insecure token storage
- Overly broad permissions or roles

**Dependencies** (if lockfile changed)

- Run `pip audit`, `npm audit`, or equivalent if available
- Flag known vulnerable versions

### 3. Report

For each finding:

- **Severity**: Critical / High / Medium / Low
- **Location**: file_path:line_number
- **Issue**: What's wrong
- **Fix**: How to fix it

If no issues found, report "Clean scan" with summary of what was checked.
