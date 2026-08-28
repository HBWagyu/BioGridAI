"""Print the generic demo farm. Streamlit seeds on first load; this is for CLI checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.services.world import new_world

if __name__ == "__main__":
    w = new_world()
    print(json.dumps(w.farm.model_dump(), indent=2)[:2000])
    print("animals", len(w.animals), "optimus", len(w.optimus), "whiplash", len(w.whiplash))
