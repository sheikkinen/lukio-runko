"""The repeat check in the build and the read-only `lukio-runko repeats` command. Fast, no network."""

from __future__ import annotations

import json

import yaml

from lukio_runko import cli
from lukio_runko.allowed_repeats import load_allowed_repeats
from lukio_runko.build import build_site
from tests.helpers import TODAY, all_codes_topic, make_root

FOOTER_START = "Opetussuunnitelman perusteet tarkistettu"  # the template's footer line, on every page


def set_repeats(root, **settings):
    path = root / "subject.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    raw["repeats"] = settings
    path.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")


def test_build_runs_the_check_and_writes_the_report_beside_the_site(tmp_path, capsys):
    root = make_root(tmp_path)
    all_codes_topic(root)
    problems = build_site(root, root / "_site", today=TODAY)
    repeats = [p for p in problems if p.kind == "repeat"]
    assert repeats and all(p.warning for p in repeats)
    assert any(FOOTER_START in p.message for p in repeats)
    assert capsys.readouterr().out.startswith("repeats: ")
    report = json.loads((root / "repeats.json").read_text(encoding="utf-8"))
    assert report["summary"]["clusters"] == len(report["clusters"]) > 0
    assert not (root / "_site" / "repeats.json").exists()


def test_fail_on_new_fails_the_build_and_partial_downgrades_it(tmp_path):
    root = make_root(tmp_path)
    all_codes_topic(root)
    set_repeats(root, fail_on_new=True)
    assert any(p.kind == "repeat" and not p.warning for p in build_site(root, root / "_site", today=TODAY))
    partial = build_site(root, root / "_site", partial=True, today=TODAY)
    assert not any(p.kind == "repeat" and not p.warning for p in partial)


def test_repeats_command_builds_a_scratch_copy_and_leaves_the_site_alone(tmp_path, capsys):
    root = make_root(tmp_path)
    all_codes_topic(root)
    before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
    assert cli.main(["repeats", "--root", str(root)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("repeats: ") and FOOTER_START in out
    assert sorted(p.relative_to(root).as_posix() for p in root.rglob("*")) == before


def test_repeats_command_reads_an_existing_build_and_writes_json(tmp_path, capsys):
    root = make_root(tmp_path)
    all_codes_topic(root)
    build_site(root, root / "_site", today=TODAY)
    capsys.readouterr()
    target = tmp_path / "out" / "report.json"
    assert cli.main(["repeats", "--root", str(root), "--json", str(target)]) == 0
    written = json.loads(target.read_text(encoding="utf-8"))
    capsys.readouterr()
    assert cli.main(["repeats", "--root", str(root), "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == written
    assert written["parameters"]["threshold_groups"] == 3


def test_suggested_entries_become_a_valid_allow_list_once_reasons_are_filled_in(tmp_path, capsys):
    root = make_root(tmp_path)
    all_codes_topic(root)
    set_repeats(root, fail_on_new=True)
    assert cli.main(["repeats", "--root", str(root)]) == 1
    capsys.readouterr()
    cli.main(["repeats", "--root", str(root), "--suggest-allow"])
    entries = yaml.safe_load(capsys.readouterr().out)
    assert entries and all(entry["reason"] == "" for entry in entries)
    for entry in entries:
        entry["reason"] = "Sivupohjan rakenne, sama joka sivulla."
    (root / "data" / "allowed-repeats.yaml").write_text(yaml.safe_dump(entries, allow_unicode=True), encoding="utf-8")
    allowed, problems = load_allowed_repeats(root, 4)
    assert problems == [] and len(allowed) == len(entries)
    assert cli.main(["repeats", "--root", str(root)]) == 0


def test_repeats_command_refuses_a_folder_without_pages(tmp_path, capsys):
    root = make_root(tmp_path)
    (tmp_path / "empty").mkdir()
    assert cli.main(["repeats", "--root", str(root), "--site", str(tmp_path / "empty")]) == 1
    assert "holds no built pages" in capsys.readouterr().err
