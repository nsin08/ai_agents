"""
Centralized path setup for backend imports.
Import this module once instead of duplicating sys.path.insert everywhere.
"""
import sys
from pathlib import Path

# Get project root
_backend_root = Path(__file__).parent.parent
_project_root = _backend_root.parent.parent

# Add paths once
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))
