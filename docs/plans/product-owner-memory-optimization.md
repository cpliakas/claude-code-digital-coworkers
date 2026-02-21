# Product Owner Agent — Memory Optimization

## Problem

The product-owner agent's local memory grows with every tracked story because it stores full acceptance criteria text, detailed status, and verbose completion records. This creates two problems:

1. **Memory bloat.** Each story can have 4–6 multi-sentence Given/When/Then criteria. Across a multi-phase project with dozens of stories, memory becomes dominated by issue content that duplicates what already lives in the issue tracker.

2. **Staleness.** If someone edits acceptance criteria in Jira or GitHub after the agent recorded its copy, the agent evaluates closure against outdated criteria. This is a correctness bug, not just an efficiency issue.

## Design Principle

With Jira and GitHub Issues as external systems of record, the agent's role shifts from **shadow issue tracker** (storing what issues contain) to **sequencing and decision journal** (storing only why things were ordered the way they were).

Each system stores what it's best at:

| System | Stores |
|--------|--------|
| **Issue tracker** (Jira / GitHub Issues) | Issue content, status, acceptance criteria, assignments — the "what" |
| **Agent local memory** | Sequencing rationale, phase logic, prioritization reasoning, discovered dependencies — the "why" |

## Phased Approach

### Phase 1: Memory protocol optimization — IMPLEMENTED

**Dependencies:** None. Zero new external dependencies.

Changes the agent's memory protocol to store condensed references instead of full issue content:

- **Story references** replace full AC storage — the agent records title, issue ID, and a one-line scope summary instead of verbatim acceptance criteria text
- **Work completions** are capped at 1–2 sentences with issue references and key learnings
- **AC evaluation** asks the user for current criteria from the tracker instead of reading stale copies from memory
- **Phase compression** — new guidance for condensing completed phase records into narrative summaries, removing per-story detail while preserving decision rationale

Estimated memory reduction: 40–60% for projects with active issue trackers.

### Phase 2: Opportunistic tracker reads

**Dependencies:** GitHub and/or Jira MCP tools must expose issue-read capabilities in the Claude Code session.

Adds conditional logic to the agent's consultation protocol:

- If GitHub/Jira MCP tools are available in the current session, the agent prefers querying the tracker for issue status and acceptance criteria over asking the user
- Local memory remains the fallback — the agent doesn't _require_ the tracker, but uses it when available
- No hard coupling: the product-owner plugin does not depend on any specific tracker plugin

This phase is about **opportunistic use** of tracker read capabilities, not a formal dependency. The agent's instructions would say something like: "If you have access to GitHub or Jira tools, use them to look up issue details rather than asking the user."

**Key design question:** Where does the read capability live? The product-owner plugin is about product ownership patterns; issue tracker integration is about platform connectivity. The read path should live in the GitHub/Jira plugins, not in this one. The PO agent simply uses whatever MCP tools are available.

**Trade-offs:**

- (+) Eliminates the "ask user to paste ACs" friction from Phase 1
- (+) Always gets current criteria — no staleness possible
- (−) Per-consultation context may grow (fetching issue details loads them into the context window)
- (−) Status reports become slower (API calls vs. instant memory reads)
- (−) Agent instructions become more complex (conditional branching on tool availability)

### Phase 3: Memory role redefinition

**Dependencies:** Phase 2 proven reliable across real projects.

Formally redefines local memory as "decisions and rationale only":

- The agent stops writing any issue content to memory — no titles, no scope summaries, no status
- Memory contains only: sequencing decisions with rationale, phase transition reasoning, cross-cutting dependency analysis, open questions, and phase narratives
- Issue references (IDs/URLs) are the only link between memory and the tracker
- The tracker is the sole source of truth for all issue-level data

**Trade-offs:**

- (+) Memory is maximally lean — pure institutional knowledge
- (+) Clean separation of concerns with no duplication
- (+) No staleness possible for any data class
- (−) Hard dependency on tracker availability — if the MCP server is down, the agent has no issue context at all
- (−) Loss of offline capability for cloud-hosted trackers
- (−) Phase-level reasoning may need to reconstruct context from multiple tracker queries

**Risk:** If the read path turns out to be unreliable (flaky MCP server, auth token expiry, rate limiting), the degraded experience — the agent constantly having no issue context — would be worse than Phase 1's "ask the user" approach. Do not commit to Phase 3 until Phase 2 has been exercised in real workflows.

## What Stays Local Regardless of Phase

Some memory is legitimately local and cannot move to the tracker at any phase:

- **Sequencing decisions and rationale** — why the agent advised defer/reorder. Trackers don't capture this naturally.
- **Phase transition logic** — when a phase was declared "done enough" and the reasoning behind it.
- **Cross-cutting dependencies** — blocking relationships that span multiple epics and aren't visible from any single issue.
- **Open questions** — items needing human decision before work can proceed.
- **Lessons learned** — patterns discovered during implementation that inform future estimates and sequencing.
