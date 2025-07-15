#!/usr/bin/env python3

import os
import sys
import subprocess
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def fail(message):
    print(f"❌ ERROR: {message}")
    sys.exit(1)

def get_all_manifest_files():
    manifests = []
    for root, dirs, files in os.walk(REPO_ROOT):
        for f in files:
            if f == "manifest.yaml":
                rel_path = os.path.relpath(os.path.join(root, f), REPO_ROOT)
                manifests.append(rel_path)
    return manifests

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

    expected_dir = os.path.normpath(os.path.join(name, version))
    actual_dir = os.path.normpath(os.path.dirname(manifest_rel_path))

    if expected_dir != actual_dir:
        fail(f"Manifest is in wrong path: expected '{expected_dir}/manifest.yaml', but found '{manifest_rel_path}'")

    abs_dir = os.path.join(REPO_ROOT, actual_dir)
    if not any(f.endswith(".tar.gz") for f in os.listdir(abs_dir)):
        fail(f".tar.gz file is missing in directory: {actual_dir}")

    print(f"✅ Validated: {manifest_rel_path}")

def main():
    manifest_files = get_all_manifest_files()
    if not manifest_files:
        fail("No manifest.yaml files found in the repository.")

    for manifest in manifest_files:
        validate_manifest_path(manifest)

if __name__ == "__main__":
    main()

