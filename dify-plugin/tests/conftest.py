import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _plugin_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """The runtime reads manifest.yaml and the YAML files relative to the plugin root."""
    monkeypatch.chdir(ROOT)
    os.environ.setdefault("INSTALL_METHOD", "local")
