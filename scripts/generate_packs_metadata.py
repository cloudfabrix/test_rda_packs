#!/usr/bin/env python3

import os
import json
import yaml

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PACKS_METADATA = []

for pack_name in os.listdir(REPO_ROOT):
    pack_path = os.path.join(REPO_ROOT, pack_name)
    if not os.path.isdir(pack_path) or pack_name == "metadata":
        continue

    for version in os.listdir(pack_path):
        version_path = os.path.join(pack_path, version)
        if not os.path.isdir(version_path):
            continue

        manifest_path = os.path.join(version_path, "manifest.yaml")
        description_path = os.path.join(version_path, "description.md")
        tar_file = next((f for f in os.listdir(version_path) if f.endswith(".tar.gz")), None)

        if not os.path.exists(manifest_path) or not os.path.exists(description_path) or not tar_file:
            continue

        with open(manifest_path) as mf:
            manifest = yaml.safe_load(mf)

        with open(description_path) as df:
            lines = df.readlines()
            description = next((line.strip() for line in lines if line.strip().startswith("#")), "")
            desc_index = lines.index(description) + 1 if description in lines else 1
            description_text = lines[desc_index].strip() if desc_index < len(lines) else ""

        metadata = {
            "pack_name": manifest.get("name"),
            "pack_version": manifest.get("version"),
            "tar_file_name": tar_file,
            "tar_file_url": f"https://raw.githubusercontent.com/cloudfabrix/rda_packs/main/{pack_name}/{version}/{tar_file}",
            "description": description_text,
            "required_fabric_services": manifest.get("fabrix_service", []),
        }

        PACKS_METADATA.append(metadata)

# Ensure metadata directory exists
os.makedirs(os.path.join(REPO_ROOT, "metadata"), exist_ok=True)

# Write metadata
with open(os.path.join(REPO_ROOT, "metadata", "packs_metadat.json"), "w") as outfile:
    json.dump(PACKS_METADATA, outfile, indent=2)

