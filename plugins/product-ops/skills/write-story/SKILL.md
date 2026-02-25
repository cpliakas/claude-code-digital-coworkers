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

**Readiness assessment:**

- If the story has hard blockers on unstarted work (entire epics or phases that have not begun), classify readiness as `backlog` and skip to the Backlog-Tier Output section at the end of this skill
- If dependencies are complete or actively in-progress, classify readiness as `sprint-ready` and continue the full process below

Detailed specification should happen at pull time, not envisioning time. Stories deep in the backlog will change as the project evolves — investing in full acceptance criteria and technical notes for work that is months away produces waste. A lightweight backlog entry captures intent and scope; the full story gets written when the team is ready to start.

### 2. Draft the Story

> **Gate:** If readiness is `backlog`, skip to the **Backlog-Tier Output** section.

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
- **Scope**: XS / S / M / L / XL (relative size estimate)
- **Recommended model**: [haiku | sonnet | opus] — [one-sentence rationale]
- **Dependencies**: [other stories, services, or decisions this is blocked by]
- **Constraints**: [performance requirements, compatibility, regulatory, etc.]
- **Files likely affected**: [key modules — only if codebase context is available from step 1]
```

**What to avoid in acceptance criteria:**

Acceptance criteria must describe behavior observable by the persona, not internal system mechanics. Given/When/Then steps use domain language, not protocol or implementation language.

| Bad (implementation detail) | Good (domain behavior) |
|-----------------------------|------------------------|
| "then the API returns HTTP 201" | "then the order appears in the customer's order history" |
| "then the response body contains `{ status: 'ok' }`" | "then a confirmation message is displayed" |
| "when `createUser()` is called" | "when the visitor submits the registration form" |
| "then a row is inserted into the `notifications` table" | "then the customer receives a notification within 60 seconds" |

**Hard rule:** If an acceptance criterion references implementation artifacts (HTTP status codes, JSON shapes, file paths, function signatures, database columns), rewrite it in domain language and move the implementation detail to Technical Notes.

**Definition of Done guidance:**

Stories reference a project-level Definition of Done rather than repeating completion standards inline. Emit a `## Definition of Done` section ONLY when the story has requirements beyond the project standard.

Examples of story-specific DoD items (include only when applicable):

- An ADR is required for the architectural decision introduced by this story
- The runbook must be validated in staging before the story is accepted
- A load test must demonstrate the endpoint handles 500 req/s at p99 < 200ms

When present, place the `## Definition of Done` section after Technical Notes in the story body.

### 3. Validate with INVEST

Check every story against all six criteria before finalizing:

| Criterion | Question | Common failure |
|-----------|----------|----------------|
| **Independent** | Can this be delivered without waiting on another in-progress story? | Coupled to another story's implementation |
| **Negotiable** | Does it describe the *what/why* and leave room for *how*? | Specifies UI layout, API shape, or implementation approach |
| **Valuable** | Does the benefit statement name a real outcome for the role? | "So that the code is cleaner" — that's a refactor, not a user story |
| **Estimable** | Is there enough detail to estimate effort? | Vague scope, unknown integration, missing constraints |
| **Small** | Can it be completed in a single PR? | Epic-sized scope, AC grouped under sub-headings, more than 7-8 acceptance criteria |
| **Testable** | Can every acceptance criterion be verified with a concrete test? | "Works correctly", "Handles all edge cases" |

If a criterion fails, fix the story before output. Common fixes:

- **Too large** — Detection signals: AC grouped under sub-headings, more than 7-8 criteria, implementation spanning multiple PRs. Split vertically by user-visible slice, not by technical layer. Use `/decompose-requirement` when any signal fires
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
- `size`: `XS`, `S`, `M`, `L`, or `XL`
- `status`: always `draft`
- `readiness`: `backlog` or `sprint-ready` — determined in step 1
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
- [ ] No implementation details in acceptance criteria — check for HTTP status codes, JSON shapes, file paths, function signatures, and database columns; rewrite any offenders in domain language and move detail to Technical Notes
- [ ] Technical notes describe constraints and outcomes, not methods
- [ ] Scope size is present
- [ ] `recommended_model` is present and rationale is included in Technical Notes

### 7. Peer Review

Run `/refine-story` on the draft story. Review the feedback and apply all failing items: rewrite implementation-bound ACs, add missing DoD, fix INVEST failures, reclassify horizontal work. Produce the final revised story followed by a `## Change Summary` section listing what was changed and why (one bullet per change). If no changes were needed, omit the Change Summary.

## Output

For **sprint-ready** stories, the markdown body MUST follow this exact section order with `##` headings:

1. `## User Story`
2. `## Acceptance Criteria`
3. `## Technical Notes`
4. `## Definition of Done` *(optional — only when story-specific DoD items exist beyond the project standard)*
5. `## Change Summary` *(optional — present only when Step 7 peer review resulted in revisions; one bullet per change with rationale)*

Additional rules:

- **Acceptance criteria**: the text of each criterion MUST be identical in the YAML `acceptance_criteria` list and the `- [ ]` checkboxes in the markdown body. Do not paraphrase.
- **Technical Notes format**: every item uses `**Label**: value` as a bullet — no prose paragraphs, no heading variations.
- **Optional fields** (`dependencies`, `Files likely affected`): omit entirely if empty. Never include blank bullets, "None", or placeholder text.

For **backlog** stories, see the Backlog-Tier Output section below — only `## User Story` is required.

Print YAML frontmatter followed by the markdown body. Example:

```yaml
---
type: story
title: "Send email notification after order approval"
parent: "Order Management Workflow"
labels:
  - "area:notifications"
  - "area:orders"
size: M
status: draft
readiness: sprint-ready
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

### Backlog-Tier Output

Use this format when readiness is `backlog` — the story has hard blockers on unstarted work and full specification would be premature.

**Skip:** acceptance criteria, technical notes, model recommendation, INVEST validation.

```yaml
---
type: story
title: "Add webhook delivery for billing events"
parent: "Billing Integration"
labels:
  - "area:billing"
  - "area:integrations"
size: M
status: draft
readiness: backlog
dependencies:
  - blocked_by: "Implement billing event pipeline"
    reason: "Billing events must be emitted before webhooks can deliver them"
---

## User Story

As an **integration partner**,
I want to receive webhook notifications when billing events occur,
so that I can keep my systems in sync without polling.

**Scope:** Covers webhook registration, delivery with retries, and a delivery log. Does not cover webhook signature verification (separate story).

**Why backlog:** The billing event pipeline (parent epic) has not started; detailed AC will be specified when this story is pulled into a sprint.
```
