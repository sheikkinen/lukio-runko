"""subject.yaml: everything subject-specific, read once at the boundary and handed to the engine as a Subject.

The site name and address, the ePerusteet ids and codes, the module routes, the assessment type and the content
contract's sections all come from here; nothing else in the engine names a subject.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SUBJECT_FILE = "subject.yaml"
ASSESSMENTS = ("sh", "numeric")
VIEWS = ("student", "lesson")


class SubjectError(ValueError):
    """subject.yaml is missing a value or has one of the wrong shape."""


@dataclass(frozen=True)
class Module:
    code: str
    id: int
    route: str


@dataclass(frozen=True)
class SectionSpec:
    """One H2 section of the content contract."""

    title: str
    id: str
    view: str
    tick: bool = False
    plan: bool = False

    def matches(self, heading: str) -> bool:
        """The plan heading states its length ('Tuntisuunnitelma (75 min)'), so it is matched by prefix."""
        return heading.startswith(self.title) if self.plan else heading == self.title


@dataclass(frozen=True)
class ExtraField:
    """An optional front-matter field the subject declares: checked against `allowed` (if any) and shown as a meta row."""

    key: str
    label: str
    allowed: tuple[str, ...] = ()


@dataclass(frozen=True)
class Subject:
    name: str
    short_name: str
    base_url: str
    storage_key: str
    licence: str
    teacher_door: str
    teacher_label: str
    role_column: str
    peruste_id: int
    oppiaine_id: int
    code: str
    general_aims_route: str
    modules: tuple[Module, ...]
    expected_counts: dict[str, int]
    max_order: int
    assessment: str
    assessment_label: str
    sections: tuple[SectionSpec, ...]
    extra_fields: tuple[ExtraField, ...] = ()
    code_pattern: re.Pattern = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        modules = "|".join(re.escape(m.code) for m in self.modules)
        pattern = re.compile(rf"^({modules})\.(t|s)\d+$|^{re.escape(self.code)}\.yt\d+$")
        object.__setattr__(self, "code_pattern", pattern)

    @property
    def module_codes(self) -> tuple[str, ...]:
        return tuple(m.code for m in self.modules)

    def route(self, module: str) -> str:
        """The page directory of a module (OP1 -> op1), or of the general aims for the subject code."""
        if module == self.code:
            return self.general_aims_route
        for item in self.modules:
            if item.code == module:
                return item.route
        return module.lower()

    @property
    def section_titles(self) -> tuple[str, ...]:
        return tuple(s.title for s in self.sections)

    @property
    def section_ids(self) -> dict[str, str]:
        return {s.title: s.id for s in self.sections}

    def view_sections(self, view: str) -> tuple[SectionSpec, ...]:
        return tuple(s for s in self.sections if s.view == view)

    def section_spec(self, heading: str) -> SectionSpec | None:
        return next((s for s in self.sections if s.matches(heading)), None)

    def env(self, name: str) -> str:
        """The environment variable for a build setting: LOO_TODAY for short name 'loo'."""
        return f"{self.short_name.upper()}_{name}"

    @property
    def licence_html(self) -> str:
        return self.licence.format(site_name=self.name, base_url=self.base_url)

    @property
    def slug(self) -> str:
        """The last part of the base address (the repository name), used in the fetch User-Agent."""
        return self.base_url.rstrip("/").rsplit("/", 1)[-1]


def _need(raw: dict, key: str, where: str) -> object:
    if not isinstance(raw, dict) or key not in raw or raw[key] in (None, ""):
        raise SubjectError(f"{SUBJECT_FILE}: {where}{key} is missing")
    return raw[key]


def _section(raw: object, where: str) -> SectionSpec:
    if not isinstance(raw, dict):
        raise SubjectError(f"{SUBJECT_FILE}: {where} must be a mapping")
    view = str(_need(raw, "view", where))
    if view not in VIEWS:
        raise SubjectError(f"{SUBJECT_FILE}: {where}view must be student or lesson, found {view!r}")
    return SectionSpec(str(_need(raw, "title", where)), str(_need(raw, "id", where)), view, bool(raw.get("tick")), bool(raw.get("plan")))


def contract_sections(contract: dict, assessment: str) -> tuple[tuple[SectionSpec, ...], str]:
    """The sections for this assessment type (the shared list plus the type's additions) and its label."""
    sections = [_section(s, "contract.sections: ") for s in _need(contract, "sections", "contract.")]
    by_type = _need(contract, "assessment", "contract.")
    kind = _need(by_type, assessment, "contract.assessment.")
    for raw in kind.get("add") or []:
        spec = _section(raw, f"contract.assessment.{assessment}.add: ")
        after = raw.get("after")
        index = next((i for i, s in enumerate(sections) if s.title == after), None)
        if index is None:
            raise SubjectError(f"{SUBJECT_FILE}: contract.assessment.{assessment}.add: {spec.title} comes after {after!r}, which is not a section")
        sections.insert(index + 1, spec)
    titles = [s.title for s in sections]
    if len(set(titles)) != len(titles):
        raise SubjectError(f"{SUBJECT_FILE}: a contract section is listed twice")
    return tuple(sections), str(_need(kind, "label", f"contract.assessment.{assessment}."))


def parse_extra_fields(topics: object) -> tuple[ExtraField, ...]:
    """topics.extra_fields: optional list of {key, label, allowed?}; none declared means nothing is checked or shown."""
    declared = topics.get("extra_fields") if isinstance(topics, dict) else None
    if declared is None:
        return ()
    if not isinstance(declared, list):
        raise SubjectError(f"{SUBJECT_FILE}: topics.extra_fields must be a list")
    fields = []
    for item in declared:
        key, label = str(_need(item, "key", "topics.extra_fields: ")), str(_need(item, "label", "topics.extra_fields: "))
        allowed = item.get("allowed") or []
        if not isinstance(allowed, list):
            raise SubjectError(f"{SUBJECT_FILE}: topics.extra_fields: allowed of '{key}' must be a list")
        fields.append(ExtraField(key, label, tuple(str(a) for a in allowed)))
    return tuple(fields)


def parse_subject(raw: object) -> Subject:
    if not isinstance(raw, dict):
        raise SubjectError(f"{SUBJECT_FILE} must be a mapping")
    site = _need(raw, "site", "")
    teacher = _need(raw, "teacher", "")
    curriculum = _need(raw, "curriculum", "")
    assessment = str(_need(raw, "assessment", ""))
    if assessment not in ASSESSMENTS:
        raise SubjectError(f"{SUBJECT_FILE}: assessment must be sh or numeric, found {assessment!r}")
    modules = tuple(
        Module(str(_need(m, "code", "curriculum.modules: ")), int(_need(m, "id", "curriculum.modules: ")), str(_need(m, "route", "curriculum.modules: ")))
        for m in _need(curriculum, "modules", "curriculum.")
    )
    sections, label = contract_sections(_need(raw, "contract", ""), assessment)
    base_url = str(_need(site, "base_url", "site."))
    return Subject(
        name=str(_need(site, "name", "site.")),
        short_name=str(_need(site, "short_name", "site.")),
        base_url=base_url if base_url.endswith("/") else base_url + "/",
        storage_key=str(_need(site, "storage_key", "site.")),
        licence=str(_need(site, "licence", "site.")),
        teacher_door=str(_need(teacher, "door", "teacher.")),
        teacher_label=str(_need(teacher, "label", "teacher.")),
        role_column=str(_need(teacher, "role_column", "teacher.")),
        peruste_id=int(_need(curriculum, "peruste_id", "curriculum.")),
        oppiaine_id=int(_need(curriculum, "oppiaine_id", "curriculum.")),
        code=str(_need(curriculum, "code", "curriculum.")),
        general_aims_route=str(_need(curriculum, "general_aims_route", "curriculum.")),
        modules=modules,
        expected_counts={str(k): int(v) for k, v in dict(_need(curriculum, "expected_counts", "curriculum.")).items()},
        max_order=int(_need(_need(raw, "topics", ""), "max_order", "topics.")),
        assessment=assessment,
        assessment_label=label,
        sections=sections,
        extra_fields=parse_extra_fields(raw["topics"]),
    )


def load_subject(root: Path) -> Subject:
    path = root / SUBJECT_FILE
    if not path.is_file():
        raise FileNotFoundError(f"{SUBJECT_FILE} is missing in the site root")
    return parse_subject(yaml.safe_load(path.read_text(encoding="utf-8")))
