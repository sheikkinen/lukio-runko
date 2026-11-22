"""subject.yaml loading, and the numeric-assessment sections with a two-topic test subject."""

from __future__ import annotations

import copy

import pytest
import yaml

from lukio_runko import checks
from lukio_runko.build import build_site
from lukio_runko.subject import SubjectError, load_subject, parse_subject
from tests.helpers import FIXTURE, PLAN_75, SECTIONS, SUBJECT, TODAY, make_root, write_topic

RAW = yaml.safe_load((FIXTURE / "subject.yaml").read_text(encoding="utf-8"))

EXAM = "### 1. Ajankäyttö (6 p)\n\nPohdi viikkoasi.\n\n### 2. Lähteet (4 p)\n\nArvioi lähdettä."
ANSWER_1 = "### 1. Ajankäyttö (6 p)\n\nHyvä vastaus nimeää kolme keinoa."
ANSWER_2 = "### 2. Lähteet (4 p)\n\nHyvä vastaus vertaa kahta lähdettä."
ANSWERS = f"{ANSWER_1}\n\n{ANSWER_2}"


def numeric_raw() -> dict:
    raw = copy.deepcopy(RAW)
    raw["assessment"] = "numeric"
    return raw


def numeric_sections(exam: str = EXAM, answers: str | None = ANSWERS) -> dict[str, str]:
    """The test topic's sections with Koetehtävät and Mallivastaukset after Tehtävät."""
    sections: dict[str, str] = {}
    for title, text in SECTIONS.items():
        sections[title] = text
        if title == "Tehtävät":
            sections["Koetehtävät"] = exam
            if answers is not None:
                sections["Mallivastaukset"] = answers
    return sections


def test_repository_subject_loads():
    subject = load_subject(FIXTURE)
    assert subject.name == "Lukion opinto-ohjaus"
    assert subject.base_url.endswith("/")
    assert subject.module_codes == ("OP1", "OP2")
    assert subject.route("OP1") == "op1" and subject.route("OP") == "opetussuunnitelma"
    assert subject.assessment == "sh"
    assert "Koetehtävät" not in subject.section_titles
    assert subject.section_titles[0] == "Opiskelijalle"
    assert subject.env("TODAY") == "LOO_TODAY"
    assert subject.code_pattern.match("OP1.t3") and subject.code_pattern.match("OP.yt11")
    assert not subject.code_pattern.match("OP3.t1")
    assert subject.base_url in subject.licence_html and subject.name in subject.licence_html


def test_numeric_adds_exam_sections_in_place():
    subject = parse_subject(numeric_raw())
    titles = subject.section_titles
    assert titles[titles.index("Tehtävät") + 1 : titles.index("Tehtävät") + 3] == ("Koetehtävät", "Mallivastaukset")
    assert subject.assessment_label == "arvosana 4–10"
    assert [s.title for s in subject.view_sections("student")][:4] == ["Opiskelijalle", "Tehtävät", "Koetehtävät", "Mallivastaukset"]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda r: r.pop("site"), "site is missing"),
        (lambda r: r["site"].pop("base_url"), "site.base_url is missing"),
        (lambda r: r.update(assessment="letters"), "assessment must be sh or numeric"),
        (lambda r: r["contract"]["sections"][0].update(view="both"), "view must be student or lesson"),
        (lambda r: r["contract"]["assessment"]["numeric"]["add"][0].update(after="Ei ole"), "not a section"),
        (lambda r: r["contract"]["sections"].append(dict(r["contract"]["sections"][0])), "listed twice"),
    ],
)
def test_bad_subject_is_refused(change, message):
    raw = numeric_raw()
    change(raw)
    with pytest.raises(SubjectError, match=message):
        parse_subject(raw)


def test_missing_subject_file(tmp_path):
    with pytest.raises(FileNotFoundError, match=r"subject.yaml"):
        load_subject(tmp_path)


def test_sh_subject_refuses_exam_sections(tmp_path):
    topic = write_topic(tmp_path, sections=numeric_sections())
    found = [p.message for p in checks.check_sections(topic, SUBJECT)]
    assert "unknown section '## Koetehtävät'" in found


def test_numeric_sections_are_required(tmp_path):
    subject = parse_subject(numeric_raw())
    topic = write_topic(tmp_path)
    found = [p.message for p in checks.check_sections(topic, subject)]
    assert "missing section '## Koetehtävät'" in found and "missing section '## Mallivastaukset'" in found


def test_numeric_tasks_and_answers_are_checked(tmp_path):
    subject = parse_subject(numeric_raw())
    good = write_topic(tmp_path, "01-hyva", sections=numeric_sections())
    assert checks.check_exam_sections(good, subject) == []
    no_points = write_topic(tmp_path, "02-pisteet", sections=numeric_sections(exam=EXAM.replace(" (4 p)", ""), answers=ANSWERS.replace(" (4 p)", "")))
    assert any("does not state its points" in p.message for p in checks.check_exam_sections(no_points, subject))
    missing = write_topic(tmp_path, "03-puuttuu", sections=numeric_sections(answers=ANSWER_1))
    assert any("has no model answer" in p.message for p in checks.check_exam_sections(missing, subject))
    extra = write_topic(tmp_path, "04-ylim", sections=numeric_sections(answers=ANSWERS + "\n\n### 3. Muu (2 p)\n\nTeksti."))
    assert any("has no exam task" in p.message for p in checks.check_exam_sections(extra, subject))
    order = write_topic(tmp_path, "05-jarjestys", sections=numeric_sections(answers=f"{ANSWER_2}\n\n{ANSWER_1}"))
    assert any("not in the order" in p.message for p in checks.check_exam_sections(order, subject))
    empty = write_topic(tmp_path, "06-tyhja", sections=numeric_sections(exam="Ei tehtäviä.", answers=""))
    assert any("has no tasks" in p.message for p in checks.check_exam_sections(empty, subject))


def test_role_column_missing_is_a_warning(tmp_path):
    plain = PLAN_75.replace(" Ohjaajan rooli |", "").replace("|---|---|---|---|", "|---|---|---|")
    sections = {**SECTIONS, "Tuntisuunnitelma (75 min)": plain}
    topic = write_topic(tmp_path, sections=sections, duration_options=[75])
    found = checks.check_role_column(topic, SUBJECT)
    assert found and all(p.warning for p in found)
    assert checks.check_role_column(write_topic(tmp_path, "02-ok"), SUBJECT) == []


def test_numeric_two_topic_subject_builds(tmp_path):
    root = make_root(tmp_path)
    (root / "subject.yaml").write_text(yaml.safe_dump(numeric_raw(), allow_unicode=True, sort_keys=False), encoding="utf-8")
    codes = list(yaml.safe_load((root / "data" / "curriculum.yaml").read_text(encoding="utf-8"))["codes"])
    half = len(codes) // 2
    write_topic(root, "01-testi", sections=numeric_sections(), curriculum=codes[:half])
    write_topic(root, "02-toinen", sections=numeric_sections(), curriculum=codes[half:], id="op1-02-toinen", order=2)
    problems = build_site(root, root / "_site", today=TODAY)
    assert [str(p) for p in problems if not p.warning] == []
    student = (root / "_site" / "op1" / "02-toinen" / "index.html").read_text(encoding="utf-8")
    assert '<section id="koetehtavat"' in student and '<section id="mallivastaukset"' in student
    assert student.index('id="tehtavat"') < student.index('id="koetehtavat"') < student.index('id="mallivastaukset"')
    module = (root / "_site" / "op1" / "index.html").read_text(encoding="utf-8")
    assert "arvosana 4–10" in module


def test_numeric_build_fails_without_model_answers(tmp_path):
    root = make_root(tmp_path)
    (root / "subject.yaml").write_text(yaml.safe_dump(numeric_raw(), allow_unicode=True, sort_keys=False), encoding="utf-8")
    codes = list(yaml.safe_load((root / "data" / "curriculum.yaml").read_text(encoding="utf-8"))["codes"])
    write_topic(root, "01-testi", sections=numeric_sections(), curriculum=codes)
    write_topic(root, "02-toinen", sections=numeric_sections(answers=None), curriculum=codes, id="op1-02-toinen", order=2)
    errors = [p for p in build_site(root, root / "_site", today=TODAY) if not p.warning]
    assert any("missing section '## Mallivastaukset'" in p.message and "02-toinen" in p.path for p in errors)


def test_assets_get_the_subject_values(tmp_path):
    root = make_root(tmp_path)
    raw = numeric_raw()
    raw["site"].update(name="Lukion testiaine", storage_key="lta:v1")
    (root / "subject.yaml").write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False), encoding="utf-8")
    build_site(root, root / "_site", partial=True, today=TODAY)
    script = (root / "_site" / "assets" / "js" / "polku.js").read_text(encoding="utf-8")
    css = (root / "_site" / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    assert "var KEY = 'lta:v1';" in script and "@STORAGE_KEY@" not in script
    assert css.startswith("/* Lukion testiaine:")
    front = (root / "_site" / "index.html").read_text(encoding="utf-8")
    assert "– Lukion testiaine</title>" in front and ">Lukion testiaine</a></p>" in front and "Lukion testiaine, https://" in front


def test_extra_fields_are_read_and_optional():
    fields = parse_subject(copy.deepcopy(RAW)).extra_fields
    assert [f.key for f in fields] == ["hops_part"] and fields[0].label == "HOPS-osa" and len(fields[0].allowed) == 3
    raw = copy.deepcopy(RAW)
    del raw["topics"]["extra_fields"]
    assert parse_subject(raw).extra_fields == ()
    raw["topics"]["extra_fields"] = [{"key": "x"}]
    with pytest.raises(SubjectError, match="label is missing"):
        parse_subject(raw)


def test_repeat_settings_default_and_override():
    assert SUBJECT.repeats.min_share == 0.10 and SUBJECT.repeats.min_groups == 3 and not SUBJECT.repeats.fail_on_new
    raw = copy.deepcopy(RAW)
    raw["repeats"] = {"min_share": 0.2, "near_min_words": 10, "fail_on_new": True}
    settings = parse_subject(raw).repeats
    assert (settings.min_share, settings.near_min_words, settings.fail_on_new, settings.min_words) == (0.2, 10, True, 4)


@pytest.mark.parametrize(
    ("repeats", "message"),
    [
        ({"min_shar": 0.2}, "repeats.min_shar is not a known setting"),
        ({"min_share": 0}, "repeats.min_share must be a number above 0"),
        ({"near_jaccard": 1.5}, "repeats.near_jaccard must be a number above 0"),
        ({"min_words": 2.5}, "repeats.min_words must be a whole number"),
        ({"min_groups": True}, "repeats.min_groups must be a whole number"),
        ({"fail_on_new": "yes"}, "repeats.fail_on_new must be true or false"),
        (["min_share"], "repeats must be a mapping"),
    ],
)
def test_repeat_settings_are_validated(repeats, message):
    raw = copy.deepcopy(RAW)
    raw["repeats"] = repeats
    with pytest.raises(SubjectError, match=message):
        parse_subject(raw)
