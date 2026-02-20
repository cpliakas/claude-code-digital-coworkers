# Claude Code Digital Coworkers

> **Hypothesis**: Humans can elevate from individual contributor to manager of virtual teams by delegating to AI specialists that learn on the job.

A Claude Code plugin marketplace of reusable **digital coworkers** — specialist agents and skills that can be installed across projects. Each coworker brings generic domain expertise while accumulating project-specific memory on the job.

## About This Project

This is a personal learning project. Building agents, wiring them together, and watching where they break is how I develop intuition for what works and what doesn't. The agents here are opinionated to a specific stack and working style — they aren't designed for broad adoption.

If you're looking for well-maintained, general-purpose collections of Claude Code agents and skills, these are better starting points:

- [wshobson/agents](https://github.com/wshobson/agents) — curated agent library
- [affaan-m/everything-claude-code](https://github.com/AffaanM/everything-claude-code) — comprehensive Claude Code resource collection
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — community-maintained subagent catalog

## What Makes This Different

### Team structure, not isolated specialists

Most agent collections are flat lists — each agent is independent and self-contained. Here, agents are organized as a team with explicit roles, hierarchy, and delegation chains defined in their markdown files.

The `cloud-infra` plugin illustrates this. `devops-lead` sets tool-agnostic principles (deployment strategies, observability requirements, IaC standards). `aws-solutions-architect` translates those principles into AWS-specific architecture decisions, consulting `devops-lead` to validate that its recommendations serve broader DevOps patterns. `cloudformation-specialist` implements what the architect specifies, consulting upstream when unsure whether a design choice (e.g., nested vs. separate stacks) is correct. Each agent's `Delegation` section names who it delegates to and who it consults, so the chain is explicit and inspectable.

Across plugins, the same pattern holds at different levels: `product-owner` advises on sequencing and priorities but never implements — it's a consultative agent that checks proposed work against the roadmap. `qa-lead` owns the full test lifecycle and consults `security-engineer` for security-related tests. `security-engineer` doesn't delegate at all — it's a leaf node consulted by others during review cycles.

### Benchmark harness for measurable agent quality

Agent definitions are easy to write and hard to evaluate. The benchmark harness (`benchmark/benchmark.py`) provides a structured way to test whether an agent's knowledge and reasoning actually hold up.

The approach is config-driven. Each benchmark is a **suite** — a `suite.yaml` that defines prompt templates, scoring criteria, and dataset field mappings, plus a dataset of question-answer pairs. The harness sends each scenario to the agent, then passes the agent's response to a separate LLM judge for scoring. No harness code changes are needed to add a new suite — you write a config file and a dataset.

Two scoring modes exist today. **Binary** mode checks correctness: did the agent recommend the right AWS services for the scenario? **Dimensional** mode scores across multiple quality axes (answer accuracy, cost surfacing, specificity, pillar coverage, risk classification, structured format) on a 1-5 scale, with aggregate statistics and weakness keyword analysis.

The current suite tests `aws-solutions-architect` against 494 SAA-C03 exam scenarios. The intention is to make this generic — a suite of benchmarks any agent can take — so there is a real validation loop rather than undifferentiated agent definitions. See [`benchmark/README.md`](benchmark/README.md) for the full CLI reference and how to create new suites.

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

## Benchmarking

A generic test harness for evaluating agent quality against domain-specific datasets. Each benchmark is a **suite** — a config file plus a dataset, no harness code changes needed.

```bash
cd benchmark
pip install -r requirements.txt

# Dry run (no API calls)
python3 benchmark.py suites/aws-solutions-architect --dry-run --sample 3

# Run direct mode on 20 random questions
python3 benchmark.py suites/aws-solutions-architect --mode direct --sample 20
```

| Suite | Agent | Questions | Description |
|-------|-------|-----------|-------------|
| `aws-solutions-architect` | `aws-solutions-architect` | 494 | SAA-C03 exam scenarios |

See [`benchmark/README.md`](benchmark/README.md) for the full CLI reference and how to create new suites.

## Repository Structure

```
claude-code-digital-coworkers/
├── README.md
├── marketplace.json
├── CLAUDE.md
├── benchmark/
│   ├── README.md
│   ├── benchmark.py
│   ├── requirements.txt
│   ├── tools/
│   │   └── parse_questions.py
│   └── suites/
│       └── aws-solutions-architect/
│           ├── suite.yaml
│           └── questions.json
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
