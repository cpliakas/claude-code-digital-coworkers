#!/usr/bin/env python3
"""
Check Plugin Version Consistency

Validates that each plugin's plugin.json version matches its marketplace.json entry.

Usage:
  python3 scripts/check-plugin-versions.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def main():
    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    marketplace_data = json.loads(marketplace_path.read_text())

    marketplace_versions = {
        p["name"]: p["version"] for p in marketplace_data.get("plugins", [])
    }

    plugin_json_paths = sorted(REPO_ROOT.glob("plugins/*/.claude-plugin/plugin.json"))

    errors = []
    for plugin_json_path in plugin_json_paths:
        plugin_data = json.loads(plugin_json_path.read_text())
        name = plugin_data.get("name")
        plugin_version = plugin_data.get("version")

        if name not in marketplace_versions:
            errors.append(f"ERROR [{name}] not listed in marketplace.json")
        elif plugin_version != marketplace_versions[name]:
            market_version = marketplace_versions[name]
            errors.append(
                f'ERROR [{name}] plugin.json version "{plugin_version}"'
                f' != marketplace.json version "{market_version}"'
            )

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Version check failed: {len(errors)} error(s)", file=sys.stderr)
        sys.exit(1)

    print(f"Version check passed: {len(plugin_json_paths)} plugin(s) OK")


if __name__ == "__main__":
    main()
