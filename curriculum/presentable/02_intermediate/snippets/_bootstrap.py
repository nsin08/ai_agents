from __future__ import annotations

import sys
from pathlib import Path


def add_repo_src_to_path() -> Path:
    """
    Add `<repo>/src` to sys.path for direct script execution.

    Snippets live at:
      curriculum/presentable/02_intermediate/snippets/<file>.py
    so the repo root is 4 levels up from this file.
    """
    repo_root = Path(__file__).resolve().parents[4]
    src_dir = repo_root / "src"
    sys.path.insert(0, str(src_dir))
    return repo_root

