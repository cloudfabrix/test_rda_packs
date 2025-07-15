#!/usr/bin/env python3

import os
import sys
import subprocess
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def fail(message):
    print(f"❌ ERROR: {message}")
    sys.exit(1)

def get_changed_manifest_files():
    result = subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD"], capture_output=True, text=True)
    if result.returncode != 0:
        fail("Could not determine changed files from git")
    files = result.stdout.strip().split("\n")
    return [f for f in files if f.endswith("manifest.yaml")]

def validate_manifest_path(manifest_rel_path):
    manifest_abs_path = os.path.join(REPO_ROOT, manifest_rel_path)
    if not os.path.exists(manifest_abs_path):
        fail(f"Manifest file not found: {manifest_rel_path}")

    with open(manifest_abs_path) as f:
        manifest = yaml.safe_load(f)

    name = manifest.get("name")
    version = manifest.get("version")

    if not name or not version:
        fail(f"Missing 'name' or 'version' in manifest: {manifest_rel_path}")

    # Normalize paths for comparison
    expected_dir = os.path.join(name, version)
    actual_dir = os.path.dirname(manifest_rel_path)

    if os.path.normpath(expected_dir) != os.path.normpath(actual_dir):
        fail(f"Manifest is in wrong path: expected '{expected_dir}/manifest.yaml' but found '{manifest_rel_path}'")

    # Check for .tar.gz file in same directory
    abs_dir = os.path.join(REPO_ROOT, actual_dir)
    if not any(f.endswith(".tar.gz") for f in os.listdir(abs_dir)):
        fail(f".tar.gz file is missing in directory: {actual_dir}")

    print(f"✅ Validated: {manifest_rel_path}")

def main():
    changed_manifests = get_changed_manifest_files()
    if not changed_manifests:
        print("✅ No manifest.yaml files changed.")
        return

    for manifest in changed_manifests:
        validate_manifest_path(manifest)

if __name__ == "__main__":
    main()

