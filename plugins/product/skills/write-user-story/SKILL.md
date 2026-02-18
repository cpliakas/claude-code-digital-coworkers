---
name: write-user-story
description: >
  Generate a well-structured GitHub user story issue with acceptance criteria.
  Use when creating new issues, breaking down epics, or formalizing requirements.
user-invocable: true
allowed-tools: Bash, Read, Grep, Glob
argument-hint: "[description of the feature or requirement]"
---

# Write User Story

Create a GitHub issue as a well-structured user story.

## Input
`$ARGUMENTS` = description of the feature, requirement, or problem to solve.

## Process

### 1. Gather Context
- Read the project's CLAUDE.md for architecture and conventions
- Check recent issues for style: `gh issue list --limit 5`
- Identify the relevant GitHub Project (epic) if one exists

### 2. Draft the Story

**Title**: Action-oriented, concise, starts with a verb.
- Good: "Add auto-push to QBO after approval"
- Bad: "QBO improvement" or "Feature: better QBO"

**Body structure**:

```
## User Story
As a [specific role],
I want [specific capability],
so that [measurable benefit].

## Acceptance Criteria
- [ ] When [condition], then [expected result]
- [ ] Given [state], when [action], then [outcome]
- [ ] [Error case]: When [invalid input], then [graceful handling]
- [ ] Tests: [what test coverage is required]

## Technical Notes
- **Files affected**: [list key files/modules]
- **Dependencies**: [other issues, external services]
- **Design decisions**: [constraints or choices to document]
```

### 3. Quality Check
Each acceptance criterion must be:
- **Independently testable** — verifiable without additional context
- **Specific** — not "works correctly" but "returns 200 with JSON body containing..."
- **Complete** — happy path (2-3), error cases (1-2), and test coverage (1)

### 4. Create the Issue
Use `gh issue create` with the drafted content.
Apply labels if the project uses them.
Link to the relevant GitHub Project if applicable.

## Output
The issue URL and a one-line summary.
