# AC Anti-Patterns Observed in This Project

## "Resolves correctly" — undefined resolution language
Seen in: product-ops metadata fix story (2026-02-26)
Pattern: "then the plugin resolves correctly under the new name"
Problem: "Resolves correctly" is internal system language. No observable behavior is named.
Fix: Name the specific command or action the persona takes and the exact output they see.

## Vague description content ACs
Seen in: product-ops metadata fix story (2026-02-26)
Pattern: "then the description reflects the full scope of product operations including agile coaching"
Problem: Does not name what specific text or content should appear. Cannot be verified without guessing.
Fix: Name the specific capability or phrase that must appear and what must not appear.

## Constraint-as-note anti-pattern
Seen in: product-ops metadata fix story (2026-02-26)
Pattern: Technical Notes contain "the `name` field must match the directory name" — a verifiable requirement buried as context.
Fix: If removing the note would change what gets built, it is a requirement. Move to AC.

## AC 3 depending on AC 1 precondition
Seen in: product-ops metadata fix story (2026-02-26)
Pattern: AC 3 assumes the plugin name was already updated (per AC 1) before it can be tested.
Fix: Add a story-level setup / precondition block. Individual ACs should not inherit state from other ACs.

## Internal consistency benefit statements
Seen in: product-ops metadata fix story (2026-02-26)
Pattern: "so that the plugin identity is consistent across directory naming, registry entries, and user-facing documentation"
Problem: Names internal system properties, not a persona-observable harm or gain.
Fix: Name what breaks for the persona today and what becomes possible after the fix.
