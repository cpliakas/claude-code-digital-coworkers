#!/usr/bin/env python3
"""
Release Plugin Script

Bumps plugin version in plugin.json and marketplace.json.

Usage:
  python3 scripts/release-plugin.py <plugin-name> <version>
  python3 scripts/release-plugin.py <plugin-name> <version> --no-commit

Version formats:
  X.Y.Z     - Full release (validate, update files, commit, tag, dev bump)
  X.Y.Z-dev - Dev-only (validate, update files; no git operations)
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
DEV_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+-dev$")


def die(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def run_git(args, check=True):
    cmd = ["git", "-C", str(REPO_ROOT)] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"git command failed: {' '.join(cmd)}", file=sys.stderr)
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    return result


def load_json(path):
    return json.loads(path.read_text())


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def next_dev_version(version):
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}-dev"


def update_files(plugin_name, version, plugin_json_path, marketplace_path):
    plugin_data = load_json(plugin_json_path)
    marketplace_data = load_json(marketplace_path)

    # Update plugin.json
    plugin_data["version"] = version
    plugin_data.pop("commit", None)

    # Update marketplace entry
    found = False
    for entry in marketplace_data.get("plugins", []):
        if entry.get("name") == plugin_name:
            entry["version"] = version
            entry.pop("commit", None)
            found = True
            break

    if not found:
        die(f"Plugin '{plugin_name}' not listed in marketplace.json")

    save_json(plugin_json_path, plugin_data)
    save_json(marketplace_path, marketplace_data)


def main():
    parser = argparse.ArgumentParser(
        description="Release a plugin to a specified version."
    )
    parser.add_argument("plugin_name", help="Plugin directory name (e.g. qa-lead)")
    parser.add_argument("version", help="Target version: X.Y.Z or X.Y.Z-dev")
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Update files only; skip git add/commit/tag (full release validations still apply)",
    )
    args = parser.parse_args()

    plugin_name = args.plugin_name
    version = args.version
    no_commit = args.no_commit

    is_release = bool(SEMVER_RE.match(version))
    is_dev = bool(DEV_VERSION_RE.match(version))

    if not is_release and not is_dev:
        die(
            f"Invalid version '{version}'. "
            "Use X.Y.Z for a release or X.Y.Z-dev for a dev bump."
        )

    # Step 2: Validate plugin exists
    plugin_json_path = (
        REPO_ROOT / "plugins" / plugin_name / ".claude-plugin" / "plugin.json"
    )
    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"

    if not plugin_json_path.exists():
        die(f"Plugin not found: {plugin_json_path}")

    if is_dev:
        # Dev-only workflow: update files, no git operations
        update_files(plugin_name, version, plugin_json_path, marketplace_path)
        print(f"Updated {plugin_name} to {version} (dev bump — no git operations).")
        return

    # Full release workflow (X.Y.Z)

    # Step 3: Dirty check on target files
    rel_plugin = str(plugin_json_path.relative_to(REPO_ROOT))
    rel_market = str(marketplace_path.relative_to(REPO_ROOT))

    status_result = run_git(["status", "--porcelain", rel_plugin, rel_market], check=False)
    if status_result.stdout.strip():
        die(
            f"Target files have uncommitted changes; commit or stash them first:\n"
            f"{status_result.stdout.rstrip()}"
        )

    # Step 4: Check if tag already exists
    tag = f"{plugin_name}-v{version}"
    tag_result = run_git(["tag", "--list", tag], check=False)
    if tag_result.stdout.strip():
        die(f"Tag '{tag}' already exists — this version has already been released.")

    # Steps 5–8: Read, update, write
    update_files(plugin_name, version, plugin_json_path, marketplace_path)
    print(f"Updated {plugin_name} to {version}.")

    if no_commit:
        print("--no-commit: files modified but not staged. Review before committing.")
        return

    # Step 9: Git add + commit release
    run_git(["add", rel_plugin, rel_market])
    release_msg = f"release({plugin_name}): bump to {version}"
    run_git(["commit", "-m", release_msg])
    print(f"Committed: {release_msg}")

    # Step 10: Create tag
    run_git(["tag", tag])
    print(f"Tagged: {tag}")

    # Steps 11–12: Compute and commit next dev version
    next_dev = next_dev_version(version)
    update_files(plugin_name, next_dev, plugin_json_path, marketplace_path)
    run_git(["add", rel_plugin, rel_market])
    dev_msg = f"chore({plugin_name}): bump to {next_dev}"
    run_git(["commit", "-m", dev_msg])
    print(f"Committed: {dev_msg}")

    print(
        f"\nRelease complete!\n"
        f"  Plugin : {plugin_name}\n"
        f"  Version: {version}\n"
        f"  Tag    : {tag}\n"
        f"  Next   : {next_dev}\n\n"
        f"To publish:\n"
        f"  git push && git push origin {tag}"
    )


if __name__ == "__main__":
    main()
