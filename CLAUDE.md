# digital-coworkers

A Claude Code plugin marketplace containing reusable agents and skills organized by domain.

## Authoring Conventions

### Frontmatter
- Use quoted strings for `description` — not YAML folded scalars (`>` or `|`). The Claude Code VS Code extension's frontmatter parser does not support multi-line scalar syntax.
  - Good: `description: "One line describing the agent or skill."`
  - Bad: `description: >` followed by indented continuation lines
- Skills use `user-invokable` (with **k**), not `user-invocable`

### Markdown Body
- Always add a blank line between a heading (or bold-text header like `**Triggers:**`) and the following list or paragraph. Omitting the blank line violates MD022/MD032 and can cause rendering issues.

### Agents
- One markdown file per agent in `plugins/<plugin>/agents/`
- Follow the agent definition template: frontmatter (name, description, model, memory) + body (jurisdiction, delegation, key knowledge, memory protocol)
- Descriptions must include trigger phrases AND delegation relationships
- All agents use `memory: project` — they learn per-project
- Agent names use kebab-case

### Skills
- One directory per skill in `plugins/<plugin>/skills/<skill-name>/`
- Must contain `SKILL.md` with YAML frontmatter
- Skills are opinionated procedures with clear inputs, process steps, and outputs
- Use `$ARGUMENTS` for parameterization
- Use `context: fork` for skills that produce a lot of output (keeps main context clean)
- Skills can bundle data files in subdirectories (e.g., `skills/lookup-aws-service/data/*.json`) — reference them via Glob/Read relative to the skill directory
- Prefer skills over MCP servers for knowledge lookups that don't require external dependencies — skills install with the plugin and need no extra configuration

### Plugins
- Each plugin has `.claude-plugin/plugin.json` at its root
- Plugin names match directory names
- Do NOT include a `version` field in individual `plugin.json` files — for relative-path plugins, `plugin.json` silently overrides the marketplace entry, causing version drift
- **`.claude-plugin/marketplace.json` is the single source of truth for versions**
- All plugins share the same version — bump all entries in `marketplace.json` together using semver when releasing changes to any plugin
- No git tags are required; the version field in `marketplace.json` drives update detection

### Agent vs Skill Decision
- If it needs to learn and decide → agent
- If it needs to execute a procedure → skill
- Agents use skills; skills don't use agents
- Agents reference skills with the `/` prefix (e.g., `/lookup-aws-service`) in their markdown — Claude invokes the skill autonomously when the agent's instructions call for it

### Benchmarks
- Generic harness lives in `benchmark/benchmark.py`
- Domain-specific suites live in `benchmark/suites/<agent-name>/`
- Each suite has a `suite.yaml` config file defining prompts, scoring, and dataset field mappings
- Datasets are co-located with their suite
- Results directories are gitignored
- Prompt templates use Python `.format()` syntax (`{scenario}`, `{expected_answer}`, `{response}`)
- Literal JSON braces in prompts must be doubled: `{{` and `}}`
- Tool-use support: `--tools` flag enables in-process tool execution using data from `plugins/cloud-engineering-aws/skills/lookup-aws-service/data/` (override with `--tools-data <path>`)
- The harness executes tool calls in-process (Python functions), bypassing MCP/skill transport — it only needs the JSON data files
- Tests live in `benchmark/tests/` and use pytest; run with `cd benchmark && pytest`

### Flow Diagrams

Plugin READMEs may include Mermaid flow diagrams that visualize skill authoring flows and agent delegation routing. Keep these diagrams in sync with their corresponding skill or agent behavior.

**Changes that require diagram updates:**

- Skill process steps added, removed, or reordered (e.g., a new gate or branch in a skill's step sequence)
- Agent delegation rules changed (e.g., which agent owns a review path, when one agent hands off to another)
- Authoring flow behavior changed (e.g., a new conditional branch, a new output path, a changed decision point)

**Changes that do not require diagram updates:**

- Wording fixes or copy edits to prose descriptions
- Metadata adjustments (frontmatter fields, YAML values) that don't alter flow logic
- Adding or removing examples that don't change the documented process

When writing a story that touches skill process steps, agent delegation rules, or authoring flow behavior, include a Definition of Done item: "Update the corresponding Mermaid flow diagram in the plugin README to reflect the changed behavior."

### README
- Keep README.md in sync with any changes to plugins, agents, or skills
- The Plugins section tables must reflect current agent/skill names and descriptions
- The Repository Structure tree must reflect the current file layout

## GitHub Conventions

### Issue Relationships

Use GitHub's native relationship sidebar — **not** a `Relationships` section in the issue body.

```bash
# 1. Fetch node IDs (batch multiple issues in one query)
gh api graphql -f query='{
  repository(owner: "cpliakas", name: "claude-code-digital-coworkers") {
    i1: issue(number: ISSUE_NUM_1) { id }
    i2: issue(number: ISSUE_NUM_2) { id }
  }
}'

# 2. Mark issue A as blocked by issue B
gh api graphql -f query='
mutation {
  addBlockedBy(input: {
    issueId: "<blocked-node-id>",
    blockingIssueId: "<blocker-node-id>"
  }) { clientMutationId }
}'
```

- `addBlockedBy` — marks issue A as blocked by issue B (renders as "blocked by" in the sidebar)
- `addBlocking` — inverse; marks issue A as blocking issue B
- Always set these after creating issues that have dependency relationships
