# Restructure Product-Owner Skills for Issue Tracking System Compatibility

Restructure the product-owner plugin's skills so their output is designed to be filed in issue tracking systems like GitHub Issues and Jira. The plugin produces high-quality requirement artifacts; downstream platform plugins (Claude Code's official `github` and `atlassian` marketplace plugins) handle the actual filing. Do NOT add any API interaction or issue-filing functionality — that would duplicate what already exists.

## Architecture

```
Layer 3: PRODUCT INTELLIGENCE  (this plugin — requirements quality + structured output)
Layer 2: WORKFLOW SKILLS        (official atlassian/github plugin skills — spec-to-backlog, triage, etc.)
Layer 1: API ACCESS             (official atlassian/github MCP tools — create issue, update field, etc.)
```

The product-owner plugin owns Layer 3 only.

## Current State

```
plugins/product-owner/
├── .claude-plugin/plugin.json          # version 0.2.1
├── agents/
│   └── product-owner.md                # consultative agent, no skill references
└── skills/
    ├── create-epic/SKILL.md            # epic spec + story decomposition (conflated)
    └── write-user-story/SKILL.md       # user story + INVEST validation
```

Problems:
- Output is unstructured markdown — downstream tools must parse free-form prose to extract title, priority, labels, etc.
- `create-epic` conflates epic scoping with story decomposition in a single pass
- The agent does not reference the skills (unlike `security-engineer` which lists skills in frontmatter)
- No platform-agnostic metadata format

## Target State

```
plugins/product-owner/
├── .claude-plugin/plugin.json          # version 0.3.0
├── agents/
│   └── product-owner.md                # updated: skills frontmatter + Requirement Authoring mode
└── skills/
    ├── write-epic/SKILL.md             # renamed from create-epic, decomposition removed
    ├── write-story/SKILL.md            # renamed from write-user-story
    └── decompose-requirement/SKILL.md  # new: decomposition extracted + subtask support
```

## Implementation Steps

### Step 1: Rename and Update Existing Skills

#### 1a. Rename `create-epic` → `write-epic`

Rename the directory `plugins/product-owner/skills/create-epic/` to `plugins/product-owner/skills/write-epic/`.

Update `SKILL.md` frontmatter:

```yaml
---
name: write-epic
description: "Write an epic specification with structured metadata, problem statement, success criteria, and scope boundaries. Output includes machine-parseable YAML frontmatter compatible with GitHub Issues and Jira."
user-invokable: true
allowed-tools: Read, Grep, Glob
argument-hint: "[epic title and description]"
---
```

Update the process steps:
- **Keep steps 1-2** (Gather Context, Define the Epic) exactly as they are — these are the core value
- **Remove steps 3-4** (Break Down Into Stories, Sequence the Stories) — these move to `/decompose-requirement`
- **Add a new step 3: "Produce Structured Output"** — construct the YAML frontmatter metadata block + markdown body (see Output Format below)
- **Update step "Validate the Epic"** — remove story-related checks ("Vertically sliced", "Sequenced", "First story is actionable"). Keep: right-sized, strategically aligned, measurable, scoped

Update the Output section to specify the YAML frontmatter + markdown body format. The output should look like:

```yaml
---
type: epic
title: "Epic title here"
labels:
  - "area:relevant-area"
priority: high
size: L
status: draft
dependencies:
  - blocked_by: "Dependency title"
    reason: "Why this blocks"
acceptance_criteria:
  - "Criterion 1"
  - "Criterion 2"
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

#### 1b. Rename `write-user-story` → `write-story`

Rename the directory `plugins/product-owner/skills/write-user-story/` to `plugins/product-owner/skills/write-story/`.

Update `SKILL.md` frontmatter:

```yaml
---
name: write-story
description: "Write a well-structured user story with structured metadata, acceptance criteria, and INVEST validation. Output includes machine-parseable YAML frontmatter compatible with GitHub Issues and Jira."
user-invokable: true
allowed-tools: Read, Grep, Glob
argument-hint: "[description of the feature or requirement]"
---
```

Update the process steps:
- **Keep steps 1-3** (Gather Context, Draft the Story, Validate with INVEST) exactly as they are — INVEST validation is the core value of this skill
- **Add a new step between current steps 3 and 4: "Produce Structured Output"** — construct the YAML frontmatter block
- **Keep step 4** (Final Quality Check) as-is
- **Make "Files likely affected"** conditional in the Technical Notes template — only include when codebase context was found during step 1. Add a note: "Include only if codebase context is available from step 1."

Update the Output section. Acceptance criteria appear in BOTH the YAML metadata (as a structured list for downstream tools) and the markdown body (as a human-readable checklist with `- [ ]`). This deliberate duplication serves both audiences.

Example output:

```yaml
---
type: story
title: "Send email notification after order approval"
parent: "Order Management Workflow"
labels:
  - "area:notifications"
  - "area:orders"
priority: medium
size: M
story_points: 5
status: draft
dependencies:
  - blocked_by: "Implement order approval workflow"
    reason: "Approval event must exist before notification can trigger"
acceptance_criteria:
  - "Given an order is approved, when the approval is saved, then an email is sent to the customer within 60 seconds"
  - "Given the customer has no email on file, when an approval triggers notification, then no email is sent and a warning is logged"
  - "Given the email service is unavailable, when a notification is triggered, then the send is retried up to 3 times"
---

## User Story

As an **online customer**,
I want to receive an email notification when my order is approved,
so that I know my order is being processed without needing to check the website.

## Acceptance Criteria

- [ ] Given an order is approved, when the approval is saved, then an email is sent within 60 seconds
- [ ] Given the customer has no email on file, then no email is sent and a warning is logged
- [ ] Given the email service is unavailable, then the send is retried up to 3 times
- [ ] Email contains: order number, items ordered, estimated delivery date

## Technical Notes

- **Dependencies**: Requires the order approval event from the order workflow service
- **Constraints**: Email must be sent asynchronously; must comply with CAN-SPAM
```

### Step 2: Create `/decompose-requirement` Skill

Create `plugins/product-owner/skills/decompose-requirement/SKILL.md`.

This skill extracts the decomposition logic from the old `create-epic` (steps 3-4: "Break Down Into Stories" and "Sequence the Stories") and extends it to also support decomposing stories into subtasks.

```yaml
---
name: decompose-requirement
description: "Decompose a requirement into well-sequenced child items with structured metadata. Takes an epic and produces stories, or takes a story and produces subtasks. Each child includes YAML frontmatter compatible with GitHub Issues and Jira."
user-invokable: true
context: fork
allowed-tools: Read, Grep, Glob
argument-hint: "[requirement title/description to decompose]"
---
```

Process steps:

1. **Gather Context** — Read the project's CLAUDE.md, scan for roadmap/backlog files, understand domain context.

2. **Parse the Input** — Determine the decomposition level:
   - If the input describes an epic-level scope → decompose into stories (5-15 children)
   - If the input describes a story-level scope → decompose into subtasks/tasks (2-8 children)
   - If ambiguous, ask the user or infer from scope signals

3. **Apply Decomposition Strategy** — Use **vertical slicing** (mandatory). Pick the best-fit strategy:
   - **Workflow steps**: One child per step in a user workflow
   - **Business rules**: One child per rule variation
   - **User roles**: One child per role's interaction with the feature
   - **CRUD**: One child per operation (when each has distinct value)
   - **Happy path first**: Core flow as child 1, then edge cases and error handling
   - Explicitly warn against horizontal slicing (e.g., "build the database layer", "build the API", "build the UI")

4. **Sequence the Children** — Order by priority:
   1. Dependencies — what must exist before other children can start?
   2. Risk — what has the most technical uncertainty? Do it early.
   3. Value — front-load children that deliver user-visible value.
   4. Learning — children that resolve unknowns enable better estimates for later ones.

5. **Produce Structured Output** — For each child:
   - YAML frontmatter block with: `type`, `title`, `parent` (set to the input requirement's title), `labels`, `priority`, `size`, `status: draft`, `dependencies`, `acceptance_criteria`
   - Brief markdown body: user story statement + 2-4 acceptance criteria
   - These are outlines, NOT full specifications. The user can run `/write-story` on individual items for full detail.

6. **Validate the Decomposition**:
   - [ ] Each child is independently deliverable
   - [ ] Each child has standalone user value (for stories) or is a clear action (for subtasks)
   - [ ] Stories fit within a single sprint; subtasks fit within a day
   - [ ] Total count is appropriate: 5-15 for epic→story, 2-8 for story→subtask
   - [ ] No horizontal slicing — every child touches the full stack where relevant
   - [ ] Dependencies are explicit and the sequence is logical
   - [ ] First child is actionable with no blockers

Output format: A summary table first, then individual child specs.

```
## Decomposition Summary

**Parent**: [input requirement title]
**Level**: epic → stories | story → subtasks
**Children**: N items

| # | Title | Type | Size | Depends On | Parallel With |
|---|-------|------|------|------------|---------------|
| 1 | Title | story | S | — | — |
| 2 | Title | story | M | #1 | — |
| 3 | Title | story | S | — | #2 |

---

## Child 1

\```
---
type: story
title: "Child title"
parent: "Parent requirement title"
labels:
  - "area:relevant"
priority: high
size: S
status: draft
dependencies: []
acceptance_criteria:
  - "Given X, when Y, then Z"
---
\```

### User Story
As a [role], I want [capability], so that [benefit].

### Acceptance Criteria
- [ ] Given X, when Y, then Z
- [ ] ...

---

## Child 2
[... same pattern ...]
```

### Step 3: Wire Agent to Skills

Update `plugins/product-owner/agents/product-owner.md`:

**3a. Add `skills:` to frontmatter** (after `memory: project`):

```yaml
skills:
  - write-epic
  - write-story
  - decompose-requirement
```

This follows the pattern in `plugins/security-engineer/agents/security-engineer.md` (line 6-7).

**3b. Add a "Requirement Authoring" response mode** after the existing "Phase Detail" mode:

```markdown
### Requirement Authoring

**Triggers:** "write an epic for", "create stories for", "break down", "decompose", "formalize this requirement", "write a story for"

When asked to author requirements:

1. If the request is to scope a new feature area → use `/write-epic`
2. If the request is to formalize a single work item → use `/write-story`
3. If the request is to break down an existing requirement into children → use `/decompose-requirement`
4. After any skill output, review the result against the roadmap and advise on sequencing
```

**3c. Add skill references in existing sections:**

In the **Scope Check** section (after the evaluation questions), add:
> When a proposed feature needs formal scoping, use `/write-epic` to produce a structured epic specification with metadata suitable for filing in issue tracking systems.

In the **Story Quality Checklist** section under Key Knowledge, add:
> For full INVEST validation and structured story output, use `/write-story`. The checklist above is for quick consultative checks when a full skill invocation is not warranted.

### Step 4: Update Plugin Metadata and README

**4a. `plugins/product-owner/.claude-plugin/plugin.json`:**

```json
{
  "name": "product-owner",
  "description": "Product owner agent and skills for roadmap planning, requirement authoring, and epic/story decomposition with structured output for GitHub Issues and Jira",
  "version": "0.3.0"
}
```

**4b. `.claude-plugin/marketplace.json`:**

Update the product-owner entry:

```json
{
  "name": "product-owner",
  "source": "./plugins/product-owner",
  "description": "Product owner agent and skills for roadmap planning, requirement authoring, and epic/story decomposition with structured output for GitHub Issues and Jira",
  "version": "0.3.0"
}
```

**4c. `README.md`:**

Update the product-owner plugin table to reflect:
- `write-epic` (was `create-epic`)
- `write-story` (was `write-user-story`)
- `decompose-requirement` (new)

Update the repository structure tree to show the renamed/new directories.

## Requirement Interchange Format (RIF) Reference

### Field Specification

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | `epic`, `story`, `task`, `bug` |
| `title` | string | Yes | Concise, verb-led, under 80 chars |
| `parent` | string | No | Title of parent requirement |
| `labels` | list of strings | No | Prefixed labels: `area:`, `priority:`, `size:`, `team:` |
| `priority` | enum | Yes | `critical`, `high`, `medium`, `low` |
| `size` | enum | Yes | `XS`, `S`, `M`, `L`, `XL` |
| `story_points` | int | No | Fibonacci: 1, 2, 3, 5, 8, 13, 21 |
| `status` | string | Yes | Always `draft` when produced by a skill |
| `dependencies` | list of objects | No | Each has `blocked_by` or `blocks` (string) + `reason` (string) |
| `acceptance_criteria` | list of strings | Yes | Each criterion as a string; Given/When/Then preferred |
| `initiative` | string | No | Strategic grouping name (traceability, not hierarchy) |
| `iteration` | string | No | Target sprint/iteration name |
| `due_date` | string | No | YYYY-MM-DD format |
| `components` | list of strings | No | System components affected |

### Platform Mapping

| RIF Field | GitHub Issues | Jira |
|-----------|--------------|------|
| `type` | Issue Type (custom: Epic/Story) | Issue Type (Epic/Story/Task/Bug) |
| `title` | Issue title | Summary |
| `parent` | Sub-issue parent | Epic Link / parent issue |
| `labels` | Labels (direct mapping) | Labels (strip prefix) |
| `priority` | Projects v2 custom field | Priority field |
| `size` | Projects v2 custom field | Story Points (map XS=1, S=2, M=3, L=5, XL=8) |
| `story_points` | Projects v2 number field | Story Points field |
| `dependencies` | Issue dependencies (blocked-by/blocking) | Linked Issues (blocks/is blocked by) |
| `acceptance_criteria` | `- [ ]` checkboxes in issue body | Description section or custom field |
| `initiative` | Label `initiative:<name>` | Initiative link (Premium) or label |
| `iteration` | Projects v2 iteration field | Sprint field |
| `due_date` | Milestone due date or Projects v2 date | Due Date field |
| `components` | Labels `area:<component>` | Components field |
| Body markdown | Issue body (rendered markdown) | Description (markdown or ADF) |

## Conventions

Follow CLAUDE.md conventions:
- Frontmatter `description` uses quoted strings (not YAML folded scalars)
- Skills use `user-invokable` (with **k**, not **c**)
- Blank line between headings/bold-text headers and following lists
- Skills use `$ARGUMENTS` for parameterization
- `context: fork` for skills that produce a lot of output
- Agent names use kebab-case

## Verification

After implementation:

1. Run `/write-epic` with a sample feature — confirm output has valid YAML frontmatter + markdown body
2. Run `/write-story` with a sample requirement — confirm INVEST validation still runs and output has YAML metadata
3. Run `/decompose-requirement` on the epic output — confirm it produces sequenced children each with their own YAML blocks
4. Invoke the product-owner agent with "write an epic for X" — confirm it delegates to `/write-epic`
5. Verify YAML parses cleanly: `python3 -c "import yaml; yaml.safe_load(open('output.md').read().split('---')[1])"`
6. Spot-check platform mapping: confirm every RIF field has a clear target in both the GitHub Issues and Jira columns
