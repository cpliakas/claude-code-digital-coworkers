---
name: create-epic
description: "Create an epic specification with problem statement, success criteria, scope boundaries, and a sequenced story breakdown. Use when starting a new feature area, initiative, or release."
user-invokable: true
allowed-tools: Read, Grep, Glob
argument-hint: "[epic title and description]"
---

# Create Epic

Write a complete epic specification with scope, success criteria, and a sequenced
story breakdown.

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

**Epic specification structure**:

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

### 3. Break Down Into Stories

Decompose the epic into 5-15 user stories using **vertical slicing** — each
story delivers a thin, user-visible slice of functionality across all layers.

Avoid horizontal slicing (e.g., "build the database layer", "build the API",
"build the UI") — these produce stories with no standalone user value.

**Decomposition strategies** (pick the best fit):
- **Workflow steps**: One story per step in a user workflow
- **Business rules**: One story per rule variation
- **User roles**: One story per role's interaction with the feature
- **CRUD**: One story per operation (when each has distinct value)
- **Happy path first**: Core flow as story 1, then edge cases and error handling

For each story, draft using the write-user-story format:
- Title (verb-led, concise)
- User story statement (role, capability, benefit)
- 2-4 acceptance criteria
- Scope estimate (S/M/L)

### 4. Sequence the Stories

Order stories by priority, applying these criteria in order:

1. **Dependencies** — what must exist before other stories can start?
2. **Risk** — what has the most technical uncertainty? Do it early.
3. **Value** — front-load stories that deliver user-visible value.
4. **Learning** — stories that resolve unknowns enable better estimates for later stories.

Present as a numbered sequence. For each story, note:
- Why it's in this position
- What it depends on (by story number)
- Whether it can be parallelized with adjacent stories

### 5. Validate the Epic

Check the overall epic before finalizing:

- [ ] **Right-sized**: 5-15 stories; spans multiple sprints but delivers value each sprint
- [ ] **Strategically aligned**: Connects to a clear user or business need
- [ ] **Measurable**: Success metrics are specific and verifiable
- [ ] **Scoped**: In-scope and out-of-scope are explicit — no ambiguity about boundaries
- [ ] **Vertically sliced**: Every story has standalone user value
- [ ] **Sequenced**: Dependencies are identified and the order is logical
- [ ] **First story is actionable**: Team could start story 1 today with no blockers

## Output
Print the complete epic specification as markdown, including the story summary
table with sequence numbers, titles, scope estimates, and dependencies.
