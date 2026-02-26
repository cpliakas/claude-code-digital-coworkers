#!/bin/sh
# Updates the project-local Mermaid skill from WH-2099/mermaid-skill.
# Run manually when a new version is available; a nightly GitHub Action (follow-on) will automate this.
set -e
git clone --depth 1 https://github.com/WH-2099/mermaid-skill.git /tmp/mermaid-skill-update
rm -rf .claude/skills/mermaid
cp -r /tmp/mermaid-skill-update/.claude/skills/mermaid .claude/skills/
rm -rf /tmp/mermaid-skill-update
echo "Mermaid skill updated. Review SKILL.md description formatting before committing."
