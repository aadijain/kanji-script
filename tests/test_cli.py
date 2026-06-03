import sys

from jp_tools.adapters.cli.main import main


def test_extract_cli_end_to_end(tmp_path, monkeypatch):
    inp = tmp_path / "in"
    inp.mkdir()
    (inp / "a.txt").write_text("東京に行った\n", encoding="utf-8")
    out = tmp_path / "out"

    # Point settings at temp paths; force freq dict absent so the run is hermetic.
    monkeypatch.setenv("JP_TOOLS_OUTPUT_DIR", str(out))
    monkeypatch.setenv("JP_TOOLS_FREQ_DICT", str(tmp_path / "missing.zip"))
    monkeypatch.setattr(sys, "argv", ["jp-tools", "extract", "--input-dir", str(inp)])

    main()

    files = list(out.glob("*.csv"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert content.startswith("word,root_form,reading,pos,freq_rank,example")
    assert "東京" in content
