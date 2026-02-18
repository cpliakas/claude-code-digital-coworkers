---
name: create-epic
description: >
  Create a GitHub Project as an epic with a description, goals, and
  initial story breakdown. Use when starting a new feature area or release.
user-invocable: true
allowed-tools: Bash, Read, Grep, Glob
argument-hint: "[epic title and description]"
---

# Create Epic

Create a GitHub Project representing an epic, with goals and initial stories.

## Input
`$ARGUMENTS` = epic title and high-level description.

## Process

### 1. Gather Context
- Read the project's CLAUDE.md and roadmap (if exists) for strategic alignment
- Check existing GitHub Projects: `gh project list`

### 2. Create the Project
Use `gh project create` with:
- **Title**: Clear, scoped (e.g., "Release 1.0.0 - Zapier Replacement")
- **Description**: 2-3 sentences on goals, scope boundary, and success criteria

### 3. Break Down Into Stories
Identify 3-7 initial stories for the epic. For each:
- Draft using the write-user-story format
- Create as GitHub issues
- Add to the project

### 4. Sequence
Order the stories by dependency — what must be done first?
Note dependencies in each story's Technical Notes section.

## Output
The project URL and a summary table of created stories with their sequence.
