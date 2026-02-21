---
name: write-epic
description: "Write an epic specification with structured metadata, problem statement, success criteria, and scope boundaries. Output includes machine-parseable YAML frontmatter compatible with GitHub Issues and Jira."
user-invokable: true
allowed-tools: Read, Grep, Glob
argument-hint: "[epic title and description]"
---

# Write Epic

Write a complete epic specification with scope, success criteria, and structured metadata output.

## Input

`$ARGUMENTS` = epic title and high-level description of the initiative.

## Process

### 1. Gather Context

- Read the project's CLAUDE.md for architecture, conventions, and strategic context
- Scan for a roadmap or backlog file if one exists (Glob for roadmap*, backlog*, TODO*)
- Identify existing work that this epic relates to or depends on

### 2. Define the Epic

**Title**: Scoped and outcome-oriented.

- Good: "User Authentication — Email and OAuth Login"
- Bad: "Auth stuff" or "Sprint 4 work"

**Epic specification body**:

```
## Problem Statement
[1-2 sentences: What problem does this solve? Who is affected? What happens if
we do nothing?]

## Desired Outcome
[1-2 sentences: What does success look like when this epic is complete?]

## Success Metrics
- [Measurable indicator 1]
- [Measurable indicator 2]

## Scope

**In scope:**
- [Capability or deliverable that IS included]

**Out of scope:**
- [Capability explicitly excluded — prevents scope creep]

**Non-goals:**
- [Things this epic intentionally does NOT try to achieve]

## Dependencies and Risks
- **Depends on**: [other epics, services, decisions, or infrastructure]
- **Blocks**: [what downstream work is waiting on this epic]
- **Risks**: [technical unknowns, external dependencies, capacity concerns]
```

### 3. Produce Structured Output

Construct the YAML frontmatter metadata block from the information gathered in steps 1-2:

- `type`: always `epic`
- `title`: the scoped, outcome-oriented title from step 2
- `labels`: prefix with `area:` for domain labels (e.g., `area:auth`, `area:payments`)
- `priority`: `critical`, `high`, `medium`, or `low` — infer from strategic context
- `size`: `XS`, `S`, `M`, `L`, or `XL` — based on scope breadth
- `status`: always `draft`
- `dependencies`: list of `blocked_by` objects with `reason`; omit if none
- `acceptance_criteria`: extract from success metrics and scope boundaries as testable criteria

### 4. Validate the Epic

Check the overall epic before finalizing:

- [ ] **Right-sized**: spans multiple sprints but delivers value each sprint
- [ ] **Strategically aligned**: connects to a clear user or business need
- [ ] **Measurable**: success metrics are specific and verifiable
- [ ] **Scoped**: in-scope and out-of-scope are explicit — no ambiguity about boundaries

## Output

Print YAML frontmatter followed by the markdown body. Example:

```yaml
---
type: epic
title: "User Authentication — Email and OAuth Login"
labels:
  - "area:auth"
priority: high
size: L
status: draft
dependencies:
  - blocked_by: "User database schema migration"
    reason: "Auth records require the users table to exist"
acceptance_criteria:
  - "Users can register and log in with email and password"
  - "Users can authenticate via Google OAuth"
  - "Failed login attempts are rate-limited after 5 attempts"
---

## Problem Statement
[...]

## Desired Outcome
[...]

## Success Metrics
[...]

## Scope

**In scope:** [...]

**Out of scope:** [...]

**Non-goals:** [...]

## Dependencies and Risks
[...]
```
