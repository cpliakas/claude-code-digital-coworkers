# Claude Code Digital Coworkers

> **Hypothesis**: Similar to how public cloud redefined what one ops engineer could manage, AI agents may redefine what one IC can take on by delegating to digital specialists that learn on the job.

A Claude Code plugin marketplace of reusable **digital coworkers**: specialist agents and skills that can be installed across projects. Each coworker brings generic domain expertise while accumulating project-specific memory on the job.

## About This Project

This is a personal learning project. Building agents, wiring them together, and watching where they break is how I develop intuition for what works and what doesn't. The agents here are opinionated to a specific stack and working style and aren't designed for broad adoption.

If you're looking for well-maintained, general-purpose collections of Claude Code agents and skills, these are better starting points:

- [wshobson/agents](https://github.com/wshobson/agents), a curated agent library
- [affaan-m/everything-claude-code](https://github.com/AffaanM/everything-claude-code), a comprehensive Claude Code resource collection
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents), a community-maintained subagent catalog

## What I'm Testing

### Team structure, not isolated specialists

Most agent collections are flat lists where each agent is independent and self-contained. Here, agents are organized as a team with explicit roles, hierarchy, and delegation chains defined in their markdown files.

The `cloud-engineering-aws` plugin illustrates this: `devops-lead` sets tool-agnostic principles, `aws-solutions-architect` translates those into AWS-specific architecture decisions, and `cloudformation-specialist` implements what the architect specifies. Each agent's `Delegation` section names who it delegates to and who it consults, so the chain is explicit and inspectable.

### Product owner as a guardrail against drift

One risk of delegating implementation to agents is losing sight of what actually matters. The `product-owner` agent is intended as a check on that: it maintains roadmap context, advises on sequencing, and pushes back when proposed work doesn't align with current priorities.

The hope is that pairing an IC with a product owner agent reduces the temptation to rabbit-hole on interesting problems at the expense of real progress. The `/write-epic`, `/write-story`, and `/decompose-requirement` skills produce structured artifacts that can land directly in GitHub Issues or Jira, keeping the backlog organized with well-refined user stories.

### Benchmark harness for measurable agent quality

Agent definitions are easy to write and hard to evaluate. The benchmark harness (`benchmark/benchmark.py`) provides a structured way to test whether an agent's knowledge and reasoning actually hold up.

Each benchmark is a **suite**: a `suite.yaml` defining prompt templates, scoring criteria, and a dataset of question-answer pairs. The harness sends each scenario to the agent, then passes the response to an LLM judge for scoring. Adding a new suite requires no harness code changes, just a config file and a dataset.

The current suite tests `aws-solutions-architect` against 494 SAA-C03 exam scenarios. See [`benchmark/README.md`](benchmark/README.md) for the full CLI reference and how to create new suites.

## Quick Start

Add the marketplace to your Claude Code project, then install the plugins you need:

```
/plugin marketplace add cpliakas/claude-code-digital-coworkers
/plugin install security-engineer@digital-coworkers
/plugin install qa-lead@digital-coworkers
/plugin install product-owner@digital-coworkers
/plugin install cloud-engineering-aws@digital-coworkers
```

## Plugins

### security-engineer

Security specialist for vulnerability detection and code security review.

| Type | Name | Description |
|------|------|-------------|
| Agent | `security-engineer` | Catches vulnerabilities before they ship (OWASP Top 10, dependency risk, secret detection) |
| Skill | `/security-scan` | Run a security checklist against staged changes, a branch diff, or a specific file |

### qa-lead

QA lead for test strategy and test lifecycle management.

| Type | Name | Description |
|------|------|-------------|
| Agent | `qa-lead` | QA lead covering test strategy, fixture design, mocking, coverage analysis, and flakiness diagnosis |

### product-owner

Product owner for roadmap planning, requirement authoring, and structured output for issue tracking.

| Type | Name | Description |
|------|------|-------------|
| Agent | `product-owner` | Roadmap keeper that advises on sequencing, priorities, and phase transitions |
| Skill | `/write-epic` | Write an epic specification with structured metadata compatible with GitHub Issues and Jira |
| Skill | `/write-story` | Write a user story with INVEST validation and structured metadata compatible with GitHub Issues and Jira |
| Skill | `/decompose-requirement` | Decompose an epic into stories, or a story into subtasks, each with structured metadata |

### cloud-engineering-aws

AWS cloud infrastructure agents covering DevOps strategy, solutions architecture, and CloudFormation implementation.

| Type | Name | Description |
|------|------|-------------|
| Agent | `devops-lead` | Infrastructure team lead for CI/CD, deployment strategies, and environment management |
| Agent | `aws-solutions-architect` | AWS Well-Architected Framework specialist for service selection, cost optimization, and security posture |
| Agent | `cloudformation-specialist` | CF template authoring covering stack lifecycle, drift detection, and nested stacks |
| Skill | `/lookup-aws-service` | Look up AWS service capability cards for service selection decisions |
| Skill | `/cf-lint` | Validate a CloudFormation template against best practices and common errors |
| Skill | `/well-architected-review` | Evaluate infrastructure changes against all 6 Well-Architected pillars |

## Architecture

### Agents vs Skills

| | Agent | Skill |
|---|---|---|
| **What** | A specialist persona with domain expertise | A repeatable procedure / SOP |
| **Memory** | Yes, learns across sessions | No, runs the same way each time |
| **Judgment** | Yes, decides *how* to approach problems | No, follows a defined process |
| **Think of it as** | An IC you hired | A runbook in a wiki |

**Rule of thumb**: If it needs to *learn and decide*, it's an agent. If it needs to *execute a procedure*, it's a skill.

### Agent Hierarchy

Agents form teams with clear delegation chains:

1. **Strategic lead** sets principles, tool-agnostic (e.g., `devops-lead`)
2. **Domain specialist** applies a specific technology (e.g., `aws-solutions-architect`)
3. **Implementation specialist** executes the solution (e.g., `cloudformation-specialist`)

### Memory

All agents use `memory: project`. The agent definition is shared via the plugin, but each project maintains its own memory in `.claude/agent-memory/`. Generic learnings stay in the agent definition; project-specific learnings stay in project memory.

## Benchmarking

A generic test harness for evaluating agent quality against domain-specific datasets. Each benchmark is a **suite** consisting of a config file and a dataset, with no harness code changes needed.

```bash
cd benchmark
pip install -r requirements.txt

# Dry run (no API calls)
python3 benchmark.py suites/aws-solutions-architect --dry-run --sample 3

# Run direct mode on 20 random questions
python3 benchmark.py suites/aws-solutions-architect --mode direct --sample 20

# Run with tool use enabled (agent can look up AWS service capabilities)
python3 benchmark.py suites/aws-solutions-architect --mode reasoning --tools --sample 20
```

| Suite | Agent | Questions | Description |
|-------|-------|-----------|-------------|
| `aws-solutions-architect` | `aws-solutions-architect` | 494 | SAA-C03 exam scenarios |

See [`benchmark/README.md`](benchmark/README.md) for the full CLI reference and how to create new suites.

## Repository Structure

```
claude-code-digital-coworkers/
├── .claude-plugin/
│   └── marketplace.json
├── README.md
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
    ├── security-engineer/
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/
    │   │   └── security-engineer.md
    │   └── skills/
    │       └── security-scan/SKILL.md
    ├── qa-lead/
    │   ├── .claude-plugin/plugin.json
    │   └── agents/
    │       └── qa-lead.md
    ├── product-owner/
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/
    │   │   └── product-owner.md
    │   └── skills/
    │       ├── write-epic/SKILL.md
    │       ├── write-story/SKILL.md
    │       └── decompose-requirement/SKILL.md
    └── cloud-engineering-aws/
        ├── .claude-plugin/plugin.json
        ├── agents/
        │   ├── devops-lead.md
        │   ├── aws-solutions-architect.md
        │   └── cloudformation-specialist.md
        └── skills/
            ├── cf-lint/SKILL.md
            ├── lookup-aws-service/
            │   ├── SKILL.md
            │   └── data/
            │       ├── compute.json
            │       ├── database.json
            │       ├── storage.json
            │       └── ... (10 category files)
            └── well-architected-review/SKILL.md
```

## License

MIT
