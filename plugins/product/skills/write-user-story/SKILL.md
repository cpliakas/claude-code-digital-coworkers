---
name: write-user-story
description: "Write a well-structured user story with acceptance criteria and INVEST validation. Use when formalizing requirements, breaking down epics, or drafting work items for any backlog tool."
user-invokable: true
allowed-tools: Read, Grep, Glob
argument-hint: "[description of the feature or requirement]"
---

# Write User Story

Write a complete, high-quality user story ready for any backlog tool.

## Input
`$ARGUMENTS` = description of the feature, requirement, or problem to solve.

## Process

### 1. Gather Context

- Read the project's CLAUDE.md for architecture, conventions, and domain language
- Scan for a roadmap or backlog file if one exists (Glob for roadmap*, backlog*, TODO*)
- Understand the domain well enough to write specific, testable criteria

### 2. Draft the Story

**Title**: Action-oriented, concise, starts with a verb.
- Good: "Add email notification after order approval"
- Bad: "Email improvement" or "Feature: better emails"

**Body structure**:

```
## User Story
As a [specific role — not "user"],
I want [specific capability — what the system should do],
so that [measurable benefit — why it matters to this role].

## Acceptance Criteria

Use Given/When/Then for behavioral criteria:
- [ ] Given [precondition], when [action], then [observable outcome]
- [ ] Given [precondition], when [action], then [observable outcome]

Use checkboxes for straightforward validations:
- [ ] [Specific, testable condition]

Include at minimum:
- 2-3 happy path criteria
- 1-2 error/edge cases
- 1 criterion for test coverage expectations

## Technical Notes
- **Scope**: Small / Medium / Large (relative estimate)
- **Dependencies**: [other stories, services, or decisions this is blocked by]
- **Constraints**: [performance requirements, compatibility, regulatory, etc.]
- **Files likely affected**: [key modules — only if codebase context is available]
```

### 3. Validate with INVEST

Check every story against all six criteria before finalizing:

| Criterion | Question | Common failure |
|-----------|----------|----------------|
| **Independent** | Can this be delivered without waiting on another in-progress story? | Coupled to another story's implementation |
| **Negotiable** | Does it describe the *what/why* and leave room for *how*? | Specifies UI layout, API shape, or implementation approach |
| **Valuable** | Does the benefit statement name a real outcome for the role? | "So that the code is cleaner" — that's a refactor, not a user story |
| **Estimable** | Is there enough detail to estimate effort? | Vague scope, unknown integration, missing constraints |
| **Small** | Can it be completed in a single sprint? | Epic-sized: "As a user, I want authentication" |
| **Testable** | Can every acceptance criterion be verified with a concrete test? | "Works correctly", "Handles all edge cases" |

If a criterion fails, fix the story before output. Common fixes:
- **Too large** — Split vertically by user-visible slice, not by technical layer
- **Not independent** — Merge with the dependency or extract a shared prerequisite
- **Not valuable** — Rewrite with a real user outcome, or reclassify as a technical task
- **Not testable** — Replace vague criteria with specific Given/When/Then

### 4. Final Quality Check

Before presenting the story, verify:
- [ ] Title starts with a verb and is under 10 words
- [ ] Role is specific (not "user" or "developer" unless that truly is the role)
- [ ] Benefit is an outcome, not a restatement of the capability
- [ ] Every acceptance criterion is independently testable without reading other criteria
- [ ] Error cases are covered — not just the happy path
- [ ] No implementation details in the story body (those belong in technical notes only)
- [ ] Technical notes describe constraints and outcomes, not methods
- [ ] Scope estimate is present

## Output
Print the complete user story as markdown. Include a one-line summary of what the story covers.
