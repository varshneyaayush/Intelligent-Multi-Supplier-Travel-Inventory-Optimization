import sys
from pathlib import Path
import pytest

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from streamlit.testing.v1 import AppTest

TABS_TO_TEST = [
    "overview",
    "inventory",
    "upload",
    "duplicates",
    "relationships",
    "suppliers",
    "anomalies",
    "ranking",
    "quality",
    "review",
    "recommendations",
    "simulation",
    "analytics",
    "settings"
]

def test_app_initial_load():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert not at.exception, f"App crashed on load: {at.exception}"

@pytest.mark.parametrize("tab_id", TABS_TO_TEST)
def test_app_render_all_tabs(tab_id):
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert not at.exception, f"Initial run failed: {at.exception}"
    
    # Switch tab via session_state
    at.session_state["active_tab"] = tab_id
    at.run()
    assert not at.exception, f"Tab '{tab_id}' raised exception: {at.exception}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

