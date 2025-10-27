import json
from pathlib import Path

import config


def test_save_config_skips_group_keys(tmp_path, monkeypatch):
    class DummyCfg:
        def __init__(self):
            self._store = {
                "analysis": json.dumps({"legacy": True}),
                "analysis/tolerance_warn": 2,
                "analysis/tolerance_fail": 5,
                "llm": json.dumps({"model": "legacy"}),
                "llm/model": "modern-model",
                "QFluentWidgets": json.dumps({"theme": "light"}),
            }

        def get_all_keys(self):
            return list(self._store.keys())

        def get(self, key):
            return self._store[key]

    dummy_cfg = DummyCfg()
    monkeypatch.setattr(config, "cfg", dummy_cfg)

    output = tmp_path / "settings.json"
    config.save_config(output)

    data = json.loads(output.read_text(encoding="utf-8"))

    assert "analysis" in data
    assert data["analysis"]["tolerance_warn"] == 2
    assert data["analysis"]["tolerance_fail"] == 5
    assert data["analysis"].get("legacy") is None

    assert "llm" in data
    assert data["llm"]["model"] == "modern-model"

    assert data["QFluentWidgets"] == dummy_cfg._store["QFluentWidgets"]
