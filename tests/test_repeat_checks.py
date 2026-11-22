"""The repeat check on small fixture sites written into tmp_path: clusters, near clusters, allow-list. No network."""

from __future__ import annotations

import dataclasses
import os
import subprocess
import sys
from pathlib import Path

import yaml

from lukio_runko.repeat_checks import check_repeats, report_json, report_threshold
from lukio_runko.subject import RepeatSettings
from lukio_runko.textsig import normalise, unit_id
from tests.helpers import FIXTURE, SUBJECT

REPO = Path(__file__).resolve().parent.parent
STAMP = "Tämä sama varoitus on jokaisella sivulla ilman mitään erityistä syytä."
SLOT = "Helpompi polku: lue ensin aiheen tiivistelmä huolellisesti ja tee sitten tehtävä {} omassa rauhassa ennen tuntia."


def page(*paragraphs: str) -> str:
    body = "".join(f"<p>{text}</p>" for text in paragraphs)
    return f'<!doctype html><html lang="fi"><head><title>t</title></head><body><main><h1>Sivu</h1>{body}</main></body></html>'


def write_site(tmp_path: Path, pages: dict[str, list[str]]) -> tuple[Path, Path]:
    """A site root (with the fixture subject.yaml) and a built site that holds these pages."""
    root = tmp_path / "root"
    site = root / "_site"
    (root / "data").mkdir(parents=True)
    (root / "subject.yaml").write_text((FIXTURE / "subject.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    for folder, paragraphs in sorted(pages.items()):
        path = site / folder / "index.html" if folder else site / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page(*paragraphs), encoding="utf-8")
    return root, site


def subject_with(**settings: object):
    return dataclasses.replace(SUBJECT, repeats=RepeatSettings(**settings))


def allow(root: Path, *entries: dict) -> None:
    (root / "data" / "allowed-repeats.yaml").write_text(yaml.safe_dump(list(entries), allow_unicode=True), encoding="utf-8")


def entry(text: str, max_groups: int = 10, reason: str = "Sama ohje joka aiheessa tarkoituksella.") -> dict:
    return {"hash": unit_id(normalise(text)), "text": text, "reason": reason, "max_groups": max_groups}


def cluster_ids(result) -> list[str]:
    return [c["id"] for c in result.report["clusters"]]


STAMP_ID = unit_id(normalise(STAMP))


def test_threshold_is_a_share_of_groups_but_never_below_three():
    settings = RepeatSettings()
    assert report_threshold(settings, 50) == 5
    assert report_threshold(settings, 30) == 3
    assert report_threshold(settings, 10) == 3
    assert report_threshold(settings, 51) == 6


def test_line_on_three_topics_is_one_cluster_and_a_warning(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [STAMP], "m/04": []})
    result = check_repeats(site, subject_with(), root)
    assert cluster_ids(result) == [STAMP_ID]
    cluster = result.report["clusters"][0]
    assert cluster["group_count"] == 3 and cluster["pages"] == ["m/01/index.html", "m/02/index.html", "m/03/index.html"]
    assert cluster["regions"] == ["main"] and cluster["tags"] == ["p"] and cluster["status"] == "new"
    [problem] = result.problems
    assert problem.warning and problem.kind == "repeat" and problem.path == "_site/m/01/index.html"
    assert "in 3 of 4 topics, 3 pages" in problem.message and STAMP in problem.message
    assert result.summary.startswith("repeats: 4 pages, 4 topics")


def test_student_and_lesson_page_count_as_one_topic(tmp_path):
    pages = {"m/01": [STAMP], "m/01/tunti": [STAMP], "m/02": [STAMP], "m/03": []}
    root, site = write_site(tmp_path, pages)
    assert cluster_ids(check_repeats(site, subject_with(), root)) == []
    root, site = write_site(tmp_path / "more", {**pages, "m/03": [STAMP]})
    [cluster] = check_repeats(site, subject_with(), root).report["clusters"]
    assert (cluster["group_count"], cluster["page_count"]) == (3, 4)


def test_print_pages_are_left_out(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "tulosta/m": [STAMP], "tulosta": [STAMP]})
    result = check_repeats(site, subject_with(), root)
    assert cluster_ids(result) == []
    assert result.report["summary"]["pages"] == 2


def test_sentence_with_the_same_pages_as_its_paragraph_is_not_listed_again(tmp_path):
    first, second = "Ensimmäinen toistuva lause on tässä kappaleessa.", "Toinen toistuva lause seuraa heti perässä."
    paragraph = f"{first} {second}"
    pages = {"m/01": [paragraph], "m/02": [paragraph], "m/03": [paragraph, first], "m/04": [first]}
    root, site = write_site(tmp_path, pages)
    result = check_repeats(site, subject_with(), root)
    by_text = {c["sample"]: c for c in result.report["clusters"]}
    assert set(by_text) == {paragraph, first}  # `second` has the paragraph's pages; `first` spreads further
    assert by_text[first]["group_count"] == 4 and by_text[first]["kinds"] == ["paragraph", "sentence"]


def test_short_units_are_dropped(tmp_path):
    root, site = write_site(tmp_path, {f"m/0{n}": ["Kolme sanaa vain."] for n in range(1, 5)})
    assert cluster_ids(check_repeats(site, subject_with(), root)) == []


def test_slot_variants_form_a_confirmed_near_cluster(tmp_path):
    pages = {"m/01": [SLOT.format("yksi")], "m/02": [SLOT.format("kaksi")], "m/03": [SLOT.format("kolme")], "m/04": []}
    root, site = write_site(tmp_path, pages)
    result = check_repeats(site, subject_with(), root)
    assert cluster_ids(result) == []  # no exact text reaches 3 topics
    [near] = result.report["near_clusters"]
    assert near["group_count"] == 3 and len(near["variants"]) == 3
    assert near["pairs"] and all(pair["jaccard"] >= 0.8 for pair in near["pairs"])
    assert result.problems == []  # the near tier reports, it does not warn


def test_short_slot_variants_are_not_near_clusters(tmp_path):
    pages = {f"m/0{n}": [f"Aika {word} minuuttia tänään."] for n, word in enumerate(("viisi", "kuusi", "seitsemän"), 1)}
    root, site = write_site(tmp_path, pages)
    assert check_repeats(site, subject_with(), root).report["near_clusters"] == []


def test_fail_on_new_turns_clusters_into_errors(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [STAMP]})
    [problem] = check_repeats(site, subject_with(fail_on_new=True), root).problems
    assert not problem.warning


def test_stamped_units_are_marked(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [STAMP], "m/04": [], "m/05": [], "m/06": [], "m/07": []})
    assert check_repeats(site, subject_with(), root).report["clusters"][0]["stamped"] is False  # 3 of 7 topics
    root, site = write_site(tmp_path / "b", {"m/01": [STAMP], "m/02": [STAMP], "m/03": [STAMP], "m/04": []})
    result = check_repeats(site, subject_with(), root)
    assert result.report["clusters"][0]["stamped"] is True and "stamped" in result.problems[0].message


def test_allowed_repeat_is_silent(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [STAMP]})
    allow(root, entry(STAMP, max_groups=3))
    result = check_repeats(site, subject_with(fail_on_new=True), root)
    assert result.problems == []
    assert result.report["clusters"][0]["status"] == "allowed"


def test_allowed_repeat_that_spreads_past_max_groups_is_reported(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [STAMP], "m/04": [STAMP]})
    allow(root, entry(STAMP, max_groups=3))
    [problem] = check_repeats(site, subject_with(), root).problems
    assert "has grown to 4 topics (max_groups 3)" in problem.message


def test_allowed_repeat_that_grows_while_below_the_threshold_is_reported(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [], "m/04": []})
    allow(root, entry(STAMP, max_groups=1))
    result = check_repeats(site, subject_with(), root)  # threshold 3, the text is on 2 topics
    [problem] = result.problems
    assert "has grown to 2 topics (max_groups 1)" in problem.message and problem.warning
    assert [(c["id"], c["status"]) for c in result.report["clusters"]] == [(STAMP_ID, "grown")]
    assert result.report["summary"]["grown"] == 1


def test_allowed_repeat_below_the_threshold_and_within_max_groups_is_silent(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [], "m/04": []})
    allow(root, entry(STAMP, max_groups=2))
    result = check_repeats(site, subject_with(fail_on_new=True), root)
    assert result.problems == [] and result.report["clusters"] == []


def test_entry_shorter_than_min_words_is_an_error(tmp_path):
    root, site = write_site(tmp_path, {"m/01": ["Malliksi kelpaava vastaus"]})
    allow(root, entry("Malliksi kelpaava vastaus"))
    [problem] = check_repeats(site, subject_with(), root).problems
    assert problem.kind == "repeat-allow-list" and not problem.warning
    assert "text has 3 words, fewer than min_words 4" in problem.message
    assert check_repeats(site, subject_with(min_words=3), root).problems == []


def test_reworded_copy_of_an_allowed_repeat_is_drift(tmp_path):
    reworded = STAMP.replace("erityistä", "erityistään")
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [STAMP], "m/04": [reworded]})
    allow(root, entry(STAMP))
    result = check_repeats(site, subject_with(), root)
    [drift] = result.report["drift"]
    assert drift["allowed"] == STAMP_ID and drift["variant"] == unit_id(normalise(reworded)) and drift["jaccard"] >= 0.8
    [problem] = result.problems
    assert problem.path == "_site/m/04/index.html" and "near variant" in problem.message and problem.warning


def test_stale_entry_is_a_warning_and_an_error_with_fail_on_new(tmp_path):
    root, site = write_site(tmp_path, {"m/01": []})
    allow(root, entry("Tätä lausetta ei ole millään sivulla enää ollenkaan."))
    [problem] = check_repeats(site, subject_with(), root).problems
    assert problem.path == "data/allowed-repeats.yaml" and problem.line == 1 and "matches no text" in problem.message and problem.warning
    [problem] = check_repeats(site, subject_with(fail_on_new=True), root).problems
    assert not problem.warning
    assert check_repeats(site, subject_with(), root).report["stale"][0]["hash"] == unit_id(normalise("Tätä lausetta ei ole millään sivulla enää ollenkaan."))


def test_text_that_does_not_match_its_hash_is_an_error_and_allows_nothing(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [STAMP]})
    broken = {**entry(STAMP), "text": STAMP + " Lisätty lause."}
    allow(root, entry("Toinen merkintä ilman yhtään osumaa sivustolla.", reason=""), broken)
    result = check_repeats(site, subject_with(), root)
    allow_list = sorted(p.message for p in result.problems if p.kind == "repeat-allow-list")
    assert len(allow_list) == 2 and all(not p.warning for p in result.problems if p.kind == "repeat-allow-list")
    assert "reason is missing" in allow_list[0] and "not to the hash" in allow_list[1]
    assert [p.line for p in result.problems if p.kind == "repeat-allow-list"] == [1, 5]
    assert result.report["clusters"][0]["status"] == "new"


def test_report_has_site_relative_paths_only(tmp_path):
    root, site = write_site(tmp_path, {"m/01": [STAMP], "m/02": [STAMP], "m/03": [STAMP]})
    text = report_json(check_repeats(site, subject_with(), root).report)
    assert str(tmp_path) not in text and tmp_path.as_posix() not in text
    assert '"m/01/index.html"' in text


def test_two_runs_with_different_hash_seeds_give_identical_json(tmp_path):
    pages = {f"m/0{n}": [STAMP, SLOT.format(word)] for n, word in enumerate(("yksi", "kaksi", "kolme", "neljä"), 1)}
    root, _site = write_site(tmp_path, pages)  # the command reads <root>/_site
    outputs = []
    for seed in ("1", "2"):
        environment = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": os.pathsep.join([str(REPO / "src"), str(REPO)])}
        command = [sys.executable, "-m", "lukio_runko", "repeats", "--root", str(root), "--json"]
        outputs.append(subprocess.run(command, env=environment, capture_output=True, check=True).stdout)
    assert outputs[0] == outputs[1]
    assert STAMP_ID.encode() in outputs[0]
