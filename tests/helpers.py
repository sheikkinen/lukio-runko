"""Builders for fixtures: a small topic, a fake ePerusteet answer and a fake site root."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import yaml

from lukio_runko.fetch_curriculum import parse_curriculum
from lukio_runko.loaders import load_document
from lukio_runko.models import Topic
from lukio_runko.subject import load_subject

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "site"  # a subject.yaml and static pages (from lukion-opinto-ohjaus)
TODAY = date(2026, 11, 21)
SUBJECT = load_subject(FIXTURE)
SUBJECT_ID = SUBJECT.oppiaine_id

PLAN_75 = """| Vaihe | Min | Toiminta | Ohjaajan rooli |
|---|---|---|---|
| Virittäytyminen | 5 | Alku |
| Työskentely | 60 | Tehtävä |
| Päätös | 10 | Exit |
"""
PLAN_60 = PLAN_75.replace("| 60 |", "| 45 |")
PLAN_45 = PLAN_75.replace("| 60 |", "| 30 |")

SECTIONS = {
    "Opiskelijalle": "Osaan suunnitella.",
    "Tehtävät": "### Tehtävä 1\n1. Tee jotain.",
    "Pohdinta": "Mitä mietit?",
    "Itseopiskelun askel": "Lue ja tee.",
    "Tuntisuunnitelma (75 min)": (
        "**Tavoite:** yhteinen.\n\n"
        + PLAN_75
        + "\n### Tuntisuunnitelma (60 min)\n\n"
        + PLAN_60
        + "\n### Tuntisuunnitelma (45 min)\n\n"
        + PLAN_45
        + "\n### Valmistelu\n\n- Tulosta paperit.\n"
    ),
    "Eriyttäminen": "Helpompi ja syvempi polku.",
    "Milloin opinto-ohjaajalle": "Kun on kiire.",
}


def topic_text(sections: dict[str, str] | None = None, **meta_overrides: object) -> str:
    meta = {
        "id": "op1-01-testi",
        "module": "OP1",
        "order": 1,
        "title": "Testiaihe",
        "summary": "Yksi lause.",
        "curriculum": ["OP1.t1"],
        "suggested_timing": {"year": 1, "term": "syksy"},
        "role": "core",
        "duration_options": [45, 60, 75],
        "self_study_minutes": 20,
        "prerequisites": [],
        "official_links": [
            {"title": "Sivu", "url": "https://example.org/a", "publisher": "Testaaja", "read": "2026-11-21"},
        ],
        "yearly_facts": [],
        "school_adapts": ["Aikataulu"],
        "materials": ["Paperi"],
        "accessibility": "Toimii ilman laitetta",
        "last_reviewed": "2026-11-21",
    }
    meta.update(meta_overrides)
    body = sections or SECTIONS
    parts = ["---", yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).rstrip(), "---", ""]
    for title, text in body.items():
        parts += [f"## {title}", "", text, ""]
    return "\n".join(parts)


def write_topic(root: Path, name: str = "01-testi", **kwargs: object) -> Topic:
    path = root / "content" / "topics" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(topic_text(**kwargs), encoding="utf-8")
    return load_document(path, root, Topic)


def fake_api_answer() -> dict:
    """An ePerusteet answer with the code counts the contract fixes (9/8, 10/8, 11)."""

    def text(value: str) -> dict:
        return {"fi": f"<p>{value}</p>"}

    def module(module_id: int, name: str, objectives: int, contents: int) -> dict:
        return {
            "id": module_id,
            "nimi": text(name + " "),
            "pakollinen": True,
            "laajuus": 2,
            "tavoitteet": {
                "kohde": text("Moduulin tavoitteena on, että opiskelija"),
                "tavoitteet": [text(f"{name} tavoite {n}") for n in range(1, objectives + 1)],
            },
            "sisallot": [{"kohde": None, "sisallot": [text(f"{name} sisältö {n}") for n in range(1, contents + 1)]}],
        }

    subject = {
        "id": SUBJECT_ID,
        "nimi": text("Opinto-ohjaus"),
        "arviointi": {"kuvaus": text("Ei arvosanaa.") | {"fi": "<p>Ei arvosanaa.</p>\n<p> </p>"}},
        "tavoitteet": {
            "tavoitealueet": [
                {
                    "nimi": text("Tavoitteena on, että"),
                    "kohde": text("opiskelija"),
                    "tavoitteet": [text(f"yleinen {n}") for n in range(1, 12)],
                }
            ]
        },
        "moduulit": [module(SUBJECT.modules[0].id, "Yksi", 9, 8), module(SUBJECT.modules[1].id, "Kaksi", 10, 8)],
    }
    return {
        "diaarinumero": "OPH-TEST",
        "nimi": text("Testiperusteet"),
        "voimassaoloAlkaa": 1627765200000,
        "viimeisinJulkaisuAika": 1779433019269,
        "lops2019": {"oppiaineet": [subject]},
    }


def make_root(tmp_path: Path, with_pages: bool = True, with_facts: bool = True) -> Path:
    """A site root with curriculum, subject.yaml and static pages; the templates and assets come from the engine."""
    root = tmp_path / "site-root"
    (root / "data").mkdir(parents=True)
    curriculum = parse_curriculum(fake_api_answer(), TODAY, SUBJECT)
    shutil.copy(FIXTURE / "subject.yaml", root / "subject.yaml")
    (root / "data" / "curriculum.yaml").write_text(yaml.safe_dump(curriculum, allow_unicode=True), encoding="utf-8")
    if with_facts:
        fact = {"key": "ytl_exam_dates", "rule": "Koepäivät", "url": "https://example.org/yo", "publisher": "YTL", "read": "2026-11-21"}
        (root / "data" / "yearly-facts.yaml").write_text(yaml.safe_dump([fact], allow_unicode=True), encoding="utf-8")
    if with_pages:
        shutil.copytree(FIXTURE / "content" / "pages", root / "content" / "pages")
    return root


def all_codes_topic(root: Path) -> Topic:
    """One topic that serves every code, so that the coverage check passes."""
    codes = list(yaml.safe_load((root / "data" / "curriculum.yaml").read_text(encoding="utf-8"))["codes"])
    return write_topic(root, curriculum=codes)
