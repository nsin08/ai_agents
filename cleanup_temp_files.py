#!/usr/bin/env python3
"""Clean up temporary files created by terminal pager overflow."""

import os
import sys
from pathlib import Path

# Files to delete (created by pager overflow during setup)
temp_files = [
    'ubprocess',
    'ult.stdout)',
    'hes, no deletions)',
    's → In Review → Done → Released)',
    'space_framework governance rules enforced by GitHub Actions. Feature branches merge to develop',
    'tatus checks for production merges',
    'tructure, sprint process, governance guides',
    'l_sharedsrcai_agents; gh pr create --base main --head develop --title release space_framework governance enforcement live --body # Release Summary',
]

root = Path(__file__).parent

print("Cleaning up temporary files from project root...")
print("-" * 60)

deleted_count = 0
for filename in temp_files:
    filepath = root / filename
    if filepath.exists():
        try:
            filepath.unlink()
            print(f"✓ Deleted: {filename}")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Failed to delete {filename}: {e}")
    else:
        print(f"⊘ Not found: {filename}")

print("-" * 60)
print(f"\nCleanup complete: {deleted_count} file(s) deleted")
print("\nNext step: Commit cleanup")
print("  git add .")
print("  git commit -m 'fix: remove temp files from root (Rule 11 compliance)'")
