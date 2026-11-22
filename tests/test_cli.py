"""The lukio-runko command and the site's own files over the engine's: fast, no network."""

from __future__ import annotations

from lukio_runko import __version__, cli
from lukio_runko.build import ENGINE_DIR, build_site, templates_dir
from tests.helpers import TODAY, all_codes_topic, make_root


def test_usage_lists_the_commands(capsys):
    assert cli.main([]) == 2
    out = capsys.readouterr().out
    assert all(name in out for name in ("build", "fetch-curriculum", "images", "repeats", "compare"))
    assert cli.main(["--version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_unknown_command_fails(capsys):
    assert cli.main(["nope"]) == 2
    assert "unknown command" in capsys.readouterr().err


def test_build_command_takes_root(tmp_path, monkeypatch, capsys):
    root = make_root(tmp_path)
    all_codes_topic(root)
    monkeypatch.setenv("LOO_TODAY", TODAY.isoformat())
    assert cli.main(["build", "--root", str(root)]) == 0
    assert "build: 0 errors" in capsys.readouterr().out
    assert (root / "_site" / "index.html").is_file()


def test_build_command_defaults_to_the_current_folder(tmp_path, monkeypatch, capsys):
    root = make_root(tmp_path)
    all_codes_topic(root)
    monkeypatch.setenv("LOO_TODAY", TODAY.isoformat())
    monkeypatch.chdir(root)
    assert cli.main(["build"]) == 0
    assert (root / "_site" / "index.html").is_file()


def test_engine_assets_and_templates_ship_with_the_package():
    for name in ("assets/css/site.css", "assets/css/print.css", "assets/js/polku.js", "templates/base.html"):
        assert (ENGINE_DIR / name).is_file(), name


def test_site_files_replace_engine_files(tmp_path):
    root = make_root(tmp_path)
    all_codes_topic(root)
    assert templates_dir(root) == ENGINE_DIR / "templates"
    (root / "site-src" / "css").mkdir(parents=True)
    (root / "site-src" / "css" / "site.css").write_text("/* own @SITE_NAME@ */\n", encoding="utf-8")
    (root / "site-src" / "img").mkdir()
    (root / "site-src" / "img" / "x.svg").write_text("<svg/>", encoding="utf-8")
    base = (ENGINE_DIR / "templates" / "base.html").read_text(encoding="utf-8")
    (root / "templates").mkdir()
    (root / "templates" / "base.html").write_text(base.replace("<body", "<!-- own -->\n<body", 1), encoding="utf-8")
    problems = build_site(root, root / "_site", today=TODAY)
    assert not [p for p in problems if not p.warning]
    site = root / "_site"
    assert (site / "assets" / "css" / "site.css").read_text(encoding="utf-8") == "/* own Lukion opinto-ohjaus */\n"
    assert (site / "assets" / "css" / "print.css").is_file() and (site / "assets" / "js" / "polku.js").is_file()
    assert (site / "assets" / "img" / "x.svg").is_file()
    assert "<!-- own -->" in (site / "index.html").read_text(encoding="utf-8")
