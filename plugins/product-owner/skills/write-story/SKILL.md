---
name: write-story
description: "Write a well-structured user story with structured metadata, acceptance criteria, and INVEST validation. Output includes machine-parseable YAML frontmatter compatible with GitHub Issues and Jira."
user-invokable: true
allowed-tools: Read, Grep, Glob
argument-hint: "[description of the feature or requirement]"
---

# Write Story

Write a complete, high-quality user story with structured metadata ready for GitHub Issues or Jira.

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
- **Recommended model**: [haiku | sonnet | opus] — [one-sentence rationale]
- **Dependencies**: [other stories, services, or decisions this is blocked by]
- **Constraints**: [performance requirements, compatibility, regulatory, etc.]
- **Files likely affected**: [key modules — only if codebase context is available from step 1]
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

### 4. Select Model Tier

Reason across three dimensions to select `recommended_model`:

| Dimension | Question |
|-----------|----------|
| **Complexity** | How many files are affected? Does the task require multi-step reasoning or deep domain knowledge? |
| **Latency tolerance** | Is this a quick task where fast turnaround matters, or a careful task where thoroughness is paramount? |
| **Cost** | Is the task well-scoped enough to trust a faster, cheaper model? |

**Selection rules:**

- **haiku** — XS or S size, low ambiguity, single-file or narrow-scope changes, no cross-service coordination. Override to `sonnet` if any of the following are present: multi-step reasoning, API design, cross-file impact.
- **sonnet** — M or L size, multi-step reasoning, cross-file changes, API design decisions, or ambiguous scope. Default for most stories.
- **opus** — Correctness-critical work (security, data integrity, complex algorithms), deep multi-layer debugging, or stories where Sonnet has previously struggled on similar work. Always include explicit rationale when recommending opus.

Record the chosen tier and a one-sentence rationale. Both appear in step 5 (frontmatter) and in the Technical Notes section of the story body.

### 5. Produce Structured Output

Construct the YAML frontmatter metadata block:

- `type`: always `story`
- `title`: the verb-led title from step 2
- `parent`: parent epic title, if known
- `labels`: prefix with `area:` for domain labels
- `status`: always `draft`
- `recommended_model`: `haiku`, `sonnet`, or `opus` — determined in step 4
- `dependencies`: list of `blocked_by` objects with `reason`; omit if none
- `acceptance_criteria`: the same criteria as in the body, as a structured list for downstream tools

Acceptance criteria appear in **both** the YAML metadata (structured list for downstream tools) and the markdown body (human-readable checklist with `- [ ]`). This deliberate duplication serves both audiences.

### 6. Final Quality Check

Before presenting the story, verify:

- [ ] Title starts with a verb and is under 10 words
- [ ] Role is specific (not "user" or "developer" unless that truly is the role)
- [ ] Benefit is an outcome, not a restatement of the capability
- [ ] Every acceptance criterion is independently testable without reading other criteria
- [ ] Error cases are covered — not just the happy path
- [ ] No implementation details in the story body (those belong in technical notes only)
- [ ] Technical notes describe constraints and outcomes, not methods
- [ ] `recommended_model` is present and rationale is included in Technical Notes

## Output

Print YAML frontmatter followed by the markdown body. Example:

```yaml
---
type: story
title: "Send email notification after order approval"
parent: "Order Management Workflow"
labels:
  - "area:notifications"
  - "area:orders"
status: draft
recommended_model: sonnet
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
- **Recommended model**: sonnet — multi-step async flow with cross-service integration warrants the workhorse model
```
