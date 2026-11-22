import re

import pytest
import yaml

from lukio_runko import build
from lukio_runko.build import build_site
from tests.helpers import SECTIONS, SUBJECT, TODAY, all_codes_topic, make_root, write_topic


def errors(problems):
    return [p for p in problems if not p.warning]


def test_build_writes_every_page_and_passes(tmp_path):
    root = make_root(tmp_path)
    all_codes_topic(root)
    out = root / "_site"
    problems = build_site(root, out, today=TODAY)
    assert errors(problems) == []
    for page in (
        "index.html",
        "op1/index.html",
        "op2/index.html",
        "op1/01-testi/index.html",
        "op1/01-testi/tunti/index.html",
        "polku/index.html",
        "tulosta/op1/index.html",
        "tulosta/op2/index.html",
        "opetussuunnitelma/index.html",
        "lahteet/index.html",
        "tietosuoja/index.html",
        "saavutettavuus/index.html",
        "assets/js/polku.js",
        "assets/css/site.css",
        "assets/css/print.css",
    ):
        assert (out / page).is_file(), page


def test_links_are_relative_only(tmp_path):
    root = make_root(tmp_path)
    all_codes_topic(root)
    build_site(root, root / "_site", today=TODAY)
    for path in (root / "_site").rglob("*.html"):
        for href in re.findall(r'(?:href|src)="([^"]*)"', path.read_text(encoding="utf-8")):
            assert not href.startswith("/"), (path, href)


def test_student_view_has_tick_hidden_without_script_and_lesson_view_has_plan(tmp_path):
    root = make_root(tmp_path)
    all_codes_topic(root)
    build_site(root, root / "_site", today=TODAY)
    student = (root / "_site/op1/01-testi/index.html").read_text(encoding="utf-8")
    lesson = (root / "_site/op1/01-testi/tunti/index.html").read_text(encoding="utf-8")
    assert "data-step-toggle" in student
    assert re.search(r"<p class=\"tick\" data-js-only hidden>", student)
    assert "Tuntisuunnitelma (75 min)" in lesson
    assert "Tuntisuunnitelma (75 min)" not in student
    assert "Opiskelijalle" in student
    assert "<h2>Opiskelijalle</h2>" in student
    assert "<h2>Opiskelijalle</h2>" not in lesson


def test_unknown_code_fails_the_build(tmp_path):
    root = make_root(tmp_path)
    write_topic(root, curriculum=["OP1.t77"])
    found = errors(build_site(root, root / "_site", today=TODAY))
    assert any("unknown curriculum code OP1.t77" in p.message and p.line > 1 for p in found)
    assert any(p.kind == "coverage" for p in found)


def test_partial_mode_makes_coverage_a_warning(tmp_path):
    root = make_root(tmp_path)
    write_topic(root)
    assert any(p.kind == "coverage" for p in errors(build_site(root, root / "_site", today=TODAY)))
    partial = build_site(root, root / "_site", partial=True, today=TODAY)
    assert not any(p.kind == "coverage" for p in errors(partial))


def test_build_copes_with_no_topics(tmp_path):
    root = make_root(tmp_path)
    problems = build_site(root, root / "_site", partial=True, today=TODAY)
    assert errors(problems) == []
    assert "Aiheita ei ole vielä julkaistu" in (root / "_site/op1/index.html").read_text(encoding="utf-8")


def test_broken_topic_is_reported_and_skipped(tmp_path):
    root = make_root(tmp_path)
    all_codes_topic(root)
    write_topic(root, "02-rikki", id="op1-02-rikki", order=2, role="nonsense")
    problems = build_site(root, root / "_site", today=TODAY)
    assert any("role" in p.message for p in errors(problems))
    assert not (root / "_site/op1/02-rikki").exists()
    assert (root / "_site/op1/01-testi").exists()


def test_missing_section_fails_with_file_name(tmp_path):
    root = make_root(tmp_path)
    all_codes_topic(root)
    sections = {k: v for k, v in SECTIONS.items() if k != "Eriyttäminen"}
    write_topic(root, "02-vajaa", id="op1-02-vajaa", order=2, sections=sections)
    found = errors(build_site(root, root / "_site", today=TODAY))
    assert any(p.path.endswith("02-vajaa.md") and "Eriyttäminen" in p.message for p in found)


def test_cli_exit_codes_and_output_listing(tmp_path, capsys):
    root = make_root(tmp_path, with_facts=False)
    all_codes_topic(root)
    assert build.main(["--root", str(root)]) == 1  # no yearly-facts file yet
    assert "yearly-facts.yaml" in capsys.readouterr().err
    assert build.main(["--root", str(root), "--partial"]) == 0


def test_refuses_to_clear_the_project_itself(tmp_path):
    root = make_root(tmp_path)
    with pytest.raises(ValueError):
        build.prepare_output(root, root, SUBJECT)


def _meta_rows(out, page):
    html = (out / page).read_text(encoding="utf-8")
    return re.findall(r"<dt>([^<]*)</dt>", html)


def test_declared_extra_field_is_shown_and_undeclared_is_not(tmp_path):
    root = make_root(tmp_path)
    write_topic(
        root, curriculum=list(yaml.safe_load((root / "data" / "curriculum.yaml").read_text(encoding="utf-8"))["codes"]), hops_part="opiskelusuunnitelma"
    )
    out = root / "_site"
    assert errors(build_site(root, out, today=TODAY)) == []
    assert "HOPS-osa" in _meta_rows(out, "op1/01-testi/index.html")
    assert "HOPS-osa" in _meta_rows(out, "op1/01-testi/tunti/index.html")
    text = (root / "subject.yaml").read_text(encoding="utf-8")
    start = text.index("  extra_fields:")
    end = text.index("# sh:")
    (root / "subject.yaml").write_text(text[:start] + text[end:], encoding="utf-8")
    assert errors(build_site(root, out, today=TODAY)) == []
    assert "HOPS-osa" not in _meta_rows(out, "op1/01-testi/index.html")


def test_card_links_show_on_the_topic_card_and_need_a_read_date(tmp_path):
    root = make_root(tmp_path)
    codes = list(yaml.safe_load((root / "data" / "curriculum.yaml").read_text(encoding="utf-8"))["codes"])
    url = "https://example.org/tarina?ch=1"
    links = [{"title": "Tarina", "url": url, "publisher": "Esimerkki", "read": TODAY.isoformat()}]
    write_topic(root, curriculum=codes, card_links=[{"label": "Visual novel", "url": url}], official_links=links)
    out = root / "_site"
    assert errors(build_site(root, out, today=TODAY)) == []
    card = (out / "op1" / "index.html").read_text(encoding="utf-8")
    assert '<a href="https://example.org/tarina?ch=1">Visual novel</a>' in card
    write_topic(root, curriculum=codes, card_links=[{"label": "Visual novel", "url": url}], official_links=[])
    assert any("card link" in p.message for p in errors(build_site(root, out, today=TODAY)))
