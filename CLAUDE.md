# digital-coworkers

A Claude Code plugin marketplace containing reusable agents and skills organized by domain.

## Authoring Conventions

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

### Plugins
- Each plugin has `.claude-plugin/plugin.json` at its root
- Plugin names match directory names
- Version using semver in plugin.json
- Update marketplace.json when adding new plugins or bumping versions

### Agent vs Skill Decision
- If it needs to learn and decide → agent
- If it needs to execute a procedure → skill
- Agents use skills; skills don't use agents

### README
- Keep README.md in sync with any changes to plugins, agents, or skills
- The Plugins section tables must reflect current agent/skill names and descriptions
- The Repository Structure tree must reflect the current file layout
