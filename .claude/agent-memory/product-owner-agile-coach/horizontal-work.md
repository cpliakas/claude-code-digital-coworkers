# Horizontal Work Signals

## Configuration / Metadata-only stories
Seen in: product-ops metadata fix story (2026-02-26)
Signal: Story touches only JSON config files. Persona "observes" the change by reading a file, not by performing a workflow.
Disposition: Strong reclassification candidate as technical task unless the fix unblocks or enables a named install-time or runtime contributor workflow.
Test: Ask "what breaks for the persona today if this is not fixed?" If the answer is "nothing visible," it is a task.

## Scope boundary failures on config stories
Pattern: Config-only stories almost always fail scope boundary review. Adjacent work (directory renames, README updates, CI scripts, agent markdown files) is non-obvious and must be explicitly excluded.
Fix template: Add ## Out of Scope listing: directory rename, prose references in markdown files, README tables, CI/validation scripts, external registries.
