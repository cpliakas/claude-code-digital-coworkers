# product-owner

A Claude Code plugin that brings product ownership discipline to AI-assisted development: roadmap awareness, requirement quality, and structured output designed to flow into GitHub Issues and Jira.

## What this plugin does

**This is a product owner, not a product manager.** The decisions about what to build and why are yours: product vision, market positioning, strategic feature bets. Once direction is set, the product owner takes over, sequencing the backlog, scoping requirements precisely, and ensuring work is broken down into increments the team can actually ship.

Most AI coding tools jump straight to implementation. This plugin inserts the product ownership layer that should come first: Is this scoped correctly? Is it sequenced properly? Is it broken down into work that can actually ship?

The plugin has two modes:

**Work sequencing:** The `product-owner` agent reads your roadmap and advises on ordering, prerequisites, and phase transitions. It pushes back when proposed work skips a dependency or conflicts with what's planned next. It doesn't decide what to build or why; it organizes and sequences the work within the direction you've already set.

**Requirement authoring:** Four skills (`/write-spike`, `/write-epic`, `/write-story`, `/decompose-requirement`) formalize requirements. Use `/write-spike` when a work area is too uncertain to scope directly; the other three skills take the output forward.

## Architecture

This plugin sits at the top of a three-layer stack:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3 · PRODUCT INTELLIGENCE          (this plugin)      │
│  Requirements quality, structured output, roadmap context   │
├─────────────────────────────────────────────────────────────┤
│  Layer 2 · WORKFLOW SKILLS               (official plugins) │
│  github · atlassian — spec-to-backlog, triage, bulk ops     │
├─────────────────────────────────────────────────────────────┤
│  Layer 1 · API ACCESS                    (official plugins) │
│  github · atlassian MCP tools — create issue, update field  │
└─────────────────────────────────────────────────────────────┘
```

This plugin owns Layer 3 only. It produces high-quality requirement artifacts and never calls an API or creates an issue itself. That separation keeps this plugin platform-agnostic and lets the official GitHub and Atlassian Claude Code plugins handle filing without duplication.

## How the pieces fit together

### The agent: sequencing layer

The `product-owner` agent is a consultative peer, not an implementer. It maintains a roadmap in project memory and uses it to evaluate every significant work request before coding begins.

Invoke it before starting non-trivial work:

> "Should we build the notification system now, or does the event pipeline need to come first?"

Invoke it after completing significant work:

> "We finished the order approval flow. What's next?"

When the conversation turns to authoring requirements, the agent delegates to the skills below.

### The skills: authoring layer

The four skills form a natural progression from broad to specific:

```
Uncertain work area
    │
    ▼
/write-spike ─────────── Resolve uncertainty first
    │                    Problem restatement, options, findings,
    │                    remaining unknowns, story seed
    │
    ▼
Feature idea (ready to scope)
    │
    ▼
/write-epic ──────────── Scope the initiative
    │                    Problem statement, success metrics,
    │                    in/out of scope, dependencies
    │
    ▼
/decompose-requirement ── Break it into children
    │                     Epic → stories (5–15)
    │                     Story → subtasks (2–8)
    │                     Sequenced by dependency, risk, value
    │
    ▼
/write-story ──────────── Formalize each work item
                          INVEST validation, Given/When/Then
                          acceptance criteria, technical notes
```

Each skill produces output in the **Requirement Interchange Format (RIF)**: a YAML frontmatter block containing machine-parseable metadata, followed by a human-readable markdown body. The same artifact serves both audiences.

### The output: flowing downstream

RIF output is structured so that official platform plugins can consume it without parsing free-form prose. Fields map directly to issue tracker concepts:

| RIF field | GitHub Issues | Jira |
|-----------|--------------|------|
| `title` | Issue title | Summary |
| `type` | Issue type (Epic/Story) | Issue type |
| `priority` | Projects v2 custom field | Priority field |
| `size` | Projects v2 custom field | Story Points |
| `labels` | Labels | Labels / Components |
| `acceptance_criteria` | `- [ ]` checkboxes in body | Description section |
| `dependencies` | Linked issues | Linked issues (blocks/blocked by) |
| `parent` | Sub-issue parent | Epic Link |

## A typical workflow

1. **Consult the agent** before starting a new feature area. It checks the roadmap, flags sequencing issues, and confirms this is the right next thing to work on.

2. **Run `/write-epic`** to scope the initiative. You get a structured spec with YAML metadata and a markdown body covering problem statement, success metrics, scope boundaries, and dependencies.

3. **Run `/decompose-requirement`** on the epic to break it into stories. Each story gets its own YAML block with `parent` pointing back to the epic. The output includes a sequencing table showing dependencies and parallelization opportunities.

4. **Run `/write-story`** on individual stories that need full specification. The skill runs INVEST validation and produces a complete story with Given/When/Then acceptance criteria duplicated in both the YAML metadata and the markdown body.

5. **File with your platform plugin.** Pass the RIF output to the official GitHub or Atlassian Claude Code plugin to create issues, link them, and populate fields without copy-pasting or reformatting.

6. **Close out completed work.** When you report back that work is done, the agent evaluates the reported outcomes against the story's acceptance criteria. If they are met, it says "I believe this story is complete" and asks for your confirmation. Once confirmed, it produces a closure summary with a suggested comment and any follow-up items. Pass that to the platform plugin to post the comment and close the issue.

## When to use what

| Situation | Use |
|-----------|-----|
| "Should we build X now or later?" | `product-owner` agent |
| "What's left in this phase?" | `product-owner` agent |
| "We finished Y. What's next?" | `product-owner` agent |
| "This area is too uncertain to scope or story-write" | `/write-spike` |
| "Scope out a new feature area" | `/write-epic` |
| "Break this epic into stories" | `/decompose-requirement` |
| "Break this story into subtasks" | `/decompose-requirement` |
| "Write a proper story for this requirement" | `/write-story` |

## What this plugin does not do

- Set product vision or decide what features to build
- Make market-level trade-offs; those decisions belong to you
- Call GitHub, Jira, or any external API to create, update, or close issues; those operations are delegated to the official github and atlassian Claude Code plugins
- Directly manage board state or sprint assignments; when a story's acceptance criteria are met, the agent produces a closure summary and asks for your confirmation before you delegate the update to the platform plugin
