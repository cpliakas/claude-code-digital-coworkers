# Definition of Done Patterns

## Missing DoD is common
Observed in: product-ops metadata fix story (2026-02-26)
Pattern: Story carries no ## Definition of Done section. Sprint-ready label is applied without a completion bar.
Rule: No story should be marked sprint-ready without either a reference to a project-level DoD or a story-specific ## Definition of Done section.

## Story-specific vs. team-level DoD distinction
Story-specific DoD items (unique to this story's work):
- Schema validation passes for affected config files
- Peer review confirmed field values are correct

Team-level standing DoD (do NOT repeat per story — belongs in project DoD doc):
- Code reviewed and approved
- No new failing tests introduced
- Branch merged to main

## Technical Notes scope duplication
Seen in: product-ops metadata fix story (2026-02-26)
Pattern: `**Scope**: XS` appears in Technical Notes body, but size is already in frontmatter.
Fix: Remove from Technical Notes. Size belongs in frontmatter only.
