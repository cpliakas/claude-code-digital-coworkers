---
name: write-spike
description: "Produce a structured findings document for a topic too uncertain to story-write directly. Covers problem restatement, key questions, options considered, findings, remaining unknowns, and a story seed."
user-invokable: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
argument-hint: "[topic or question driving the investigation]"
---

# Write Spike

Produce a structured findings document that resolves enough uncertainty to let the product owner write a well-formed user story.

## Input

`$ARGUMENTS` = the topic, question, or work area that is too uncertain to story-write directly.

## Process

### 1. Gather Context

- Read the project's CLAUDE.md for architecture, domain language, and constraints
- Scan for a roadmap or backlog file if one exists (Glob for roadmap*, backlog*, TODO*)
- Identify any existing work or decisions that bear on the topic

### 2. Scope the Investigation

State clearly:

- **The driving question**: What specific question does this spike need to answer? Narrow to one well-formed question if the input is broad.
- **Why now**: What decision or story is blocked until this question is answered?
- **Out of scope**: What related questions will be explicitly deferred?

A spike that tries to answer three questions usually answers none well.

### 3. Explore the Topic

Research the topic through whatever means are available:

- Read relevant source files if the topic is code or architecture
- Search for documentation, prior art, or established patterns (WebSearch / WebFetch)
- Enumerate options or approaches with concrete trade-offs — not just "Option A vs Option B" but specific pros, cons, and constraints for this project
- Note sources and links for evidence that will be referenced in the output

### 4. Assess Story Readiness

Before producing output, evaluate:

- Can the driving question be answered with enough confidence to write a story?
- Are there remaining unknowns that would block story writing or cause the story to be poorly scoped?
- If unknowns remain, identify a concrete follow-up action for each (prototype, user interview, additional reading, architectural decision)

### 5. Produce Structured Output

Construct the YAML frontmatter metadata block:

- `type`: always `spike`
- `title`: verb-led, describes the investigation (e.g., "Investigate caching options for product search API")
- `topic`: the single driving question in one sentence
- `labels`: prefix with `area:` for domain labels
- `priority`: `critical`, `high`, `medium`, or `low`
- `status`: always `draft`
- `story_seed`: a one-sentence story starter or recommended next action — omit if findings are inconclusive

## Output

Print YAML frontmatter followed by the findings document body. Example:

```yaml
---
type: spike
title: "Investigate authentication options for mobile API"
topic: "Which auth approach (OAuth2, API key, or JWT) best fits our mobile client constraints?"
labels:
  - "area:auth"
  - "area:mobile"
priority: high
status: draft
story_seed: "Add JWT-based authentication to the mobile API client"
---

## Problem Restatement

The mobile client needs to authenticate against the API, but it is unclear which approach fits the
constraints: no server-side session storage, short-lived tokens preferred, and support for
offline-first operation.

## Key Questions Explored

- Can OAuth2 work without a browser redirect in the mobile context?
- Does JWT satisfy the offline-first requirement without a token-refresh round-trip?
- What is the operational cost of rotating API keys vs. refreshing tokens?

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| OAuth2 (authorization code) | Industry standard, revocable | Requires browser redirect; complex for native clients |
| API key | Simple to implement | Long-lived; revocation requires key rotation; poor for multi-device |
| JWT (short-lived + refresh) | Stateless, offline-capable, revocable via refresh rotation | Refresh token storage adds complexity |

## Findings

JWT with short-lived access tokens and a rotating refresh token is the best fit. It satisfies
the offline-first constraint (access token valid for 15 minutes without network), avoids
browser redirects, and allows revocation by invalidating the refresh token. The operational
overhead of a refresh endpoint is justified by the security and UX benefits.

OAuth2 was ruled out because the authorization code flow requires a browser redirect — viable
for web but disruptive in a native mobile app. API keys were ruled out due to long-lived
credentials and no per-device revocation.

## Remaining Unknowns

- **Refresh token storage on device**: Where to securely store the refresh token on iOS and
  Android is not resolved. Follow-up: evaluate Keychain (iOS) and Keystore (Android) before
  implementing.

## Story Seed

Add JWT-based authentication to the mobile API client, using short-lived access tokens and a
rotating refresh token stored in platform-native secure storage.
```
