from pathlib import Path

from jp_tools.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.input_dir == Path("input")
    assert s.output == "kanji"
    assert s.output_dir == Path("output")


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("JP_TOOLS_OUTPUT", "custom")
    monkeypatch.setenv("JP_TOOLS_INPUT_DIR", "myinput")
    s = Settings()
    assert s.output == "custom"
    assert s.input_dir == Path("myinput")
