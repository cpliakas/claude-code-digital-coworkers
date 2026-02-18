# Claude Code Digital Coworkers

> **Hypothesis**: Humans can elevate from individual contributor to manager of virtual teams by delegating to AI specialists that learn on the job.

A Claude Code plugin marketplace of reusable **digital coworkers** — specialist agents and skills that can be installed across projects. Each coworker brings generic domain expertise while accumulating project-specific memory on the job.

## Quick Start

Add the marketplace to your Claude Code project, then install the plugins you need:

```
/plugin marketplace add cpliakas/claude-code-digital-coworkers
/plugin install foundations@digital-coworkers
/plugin install product@digital-coworkers
/plugin install cloud-infra@digital-coworkers
```

## Plugins

### foundations

Core engineering agents and skills every project needs.

| Type | Name | Description |
|------|------|-------------|
| Agent | `security-engineer` | Catches vulnerabilities before they ship — OWASP Top 10, dependency risk, secret detection |
| Agent | `qa-lead` | QA lead — test strategy, fixture design, mocking, coverage analysis, flakiness diagnosis |
| Skill | `/security-scan` | Run a security checklist against staged changes, a branch diff, or a specific file |

### product

Product management agents and skills.

| Type | Name | Description |
|------|------|-------------|
| Agent | `product-owner` | Roadmap keeper — advises on sequencing, priorities, and phase transitions |
| Skill | `/write-user-story` | Write a well-structured user story with acceptance criteria and INVEST validation |
| Skill | `/create-epic` | Create an epic specification with scope, success criteria, and sequenced story breakdown |

### cloud-infra

Cloud infrastructure agents — DevOps strategy, AWS architecture, CloudFormation implementation.

| Type | Name | Description |
|------|------|-------------|
| Agent | `devops-lead` | Infrastructure team lead — CI/CD, deployment strategies, environment management |
| Agent | `aws-solutions-architect` | AWS Well-Architected Framework — service selection, cost optimization, security posture |
| Agent | `cloudformation-specialist` | CF template authoring — stack lifecycle, drift detection, nested stacks |
| Skill | `/cf-lint` | Validate a CloudFormation template against best practices and common errors |
| Skill | `/well-architected-review` | Evaluate infrastructure changes against all 6 Well-Architected pillars |

## Architecture

### Agents vs Skills

| | Agent | Skill |
|---|---|---|
| **What** | A specialist persona with domain expertise | A repeatable procedure / SOP |
| **Memory** | Yes — learns across sessions | No — runs the same way each time |
| **Judgment** | Yes — decides *how* to approach problems | No — follows a defined process |
| **Think of it as** | An IC you hired | A runbook in a wiki |

**Rule of thumb**: If it needs to *learn and decide*, it's an agent. If it needs to *execute a procedure*, it's a skill.

### Agent Hierarchy

Agents form teams with clear delegation chains:

1. **Strategic lead** — sets principles, tool-agnostic (e.g., `devops-lead`)
2. **Domain specialist** — applies a specific technology (e.g., `aws-solutions-architect`)
3. **Implementation specialist** — executes the solution (e.g., `cloudformation-specialist`)

### Memory

All agents use `memory: project` — the agent definition is shared via the plugin, but each project maintains its own memory in `.claude/agent-memory/`. Generic learnings stay in the agent definition; project-specific learnings stay in project memory.

## Repository Structure

```
claude-code-digital-coworkers/
├── README.md
├── marketplace.json
├── CLAUDE.md
└── plugins/
    ├── foundations/
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/
    │   │   ├── security-engineer.md
    │   │   └── qa-lead.md
    │   └── skills/
    │       └── security-scan/SKILL.md
    ├── product/
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/
    │   │   └── product-owner.md
    │   └── skills/
    │       ├── write-user-story/SKILL.md
    │       └── create-epic/SKILL.md
    └── cloud-infra/
        ├── .claude-plugin/plugin.json
        ├── agents/
        │   ├── devops-lead.md
        │   ├── aws-solutions-architect.md
        │   └── cloudformation-specialist.md
        └── skills/
            ├── cf-lint/SKILL.md
            └── well-architected-review/SKILL.md
```

## License

MIT
