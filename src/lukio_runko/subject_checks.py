"""Checks that subject.yaml switches on: the exam sections of a numeric subject and the teacher's plan column.

A subject graded 4-10 (`assessment: numeric`) is a matriculation exam subject, so its topics carry
`## Koetehtävät` (exam-style tasks, each a `###` heading that states its points, e.g. `### 1. Unen merkitys (6 p)`)
and `## Mallivastaukset` (one `###` model answer per task, with the same heading, in the same order).
"""

from __future__ import annotations

import re

from lukio_runko.models import Problem, Section, Topic
from lukio_runko.subject import Subject

EXAM_SECTION = "Koetehtävät"
ANSWER_SECTION = "Mallivastaukset"
POINTS = re.compile(r"\(\s*\d+\s*p\s*\)\s*$")
_H3 = re.compile(r"^###\s+(.+?)\s*#*\s*$")
_SEPARATOR = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def h3_blocks(section: Section) -> list[tuple[str, int, str]]:
    """(heading, absolute line, text under it) for every ### heading of a section."""
    blocks: list[tuple[str, int, list[str]]] = []
    for offset, line in enumerate(section.lines):
        match = _H3.match(line)
        if match:
            blocks.append((match.group(1), section.line + 1 + offset, []))
        elif blocks:
            blocks[-1][2].append(line)
    return [(title, line, "\n".join(lines).strip()) for title, line, lines in blocks]


def check_exam_sections(topic: Topic, subject: Subject) -> list[Problem]:
    """For a numeric subject: tasks with points, and a model answer for every task (none extra)."""
    if subject.assessment != "numeric":
        return []
    exam, answers = topic.section(EXAM_SECTION), topic.section(ANSWER_SECTION)
    if exam is None or answers is None:
        return []  # check_sections reports the missing section
    problems = []
    tasks = h3_blocks(exam)
    if not tasks:
        problems.append(Problem(topic.path, exam.line, f"'{EXAM_SECTION}' has no tasks (### headings)", "exam"))
    for title, line, _ in tasks:
        if not POINTS.search(title):
            problems.append(Problem(topic.path, line, f"exam task '{title}' does not state its points, e.g. '(6 p)'", "exam"))
    model = h3_blocks(answers)
    task_titles = [t for t, _, _ in tasks]
    model_titles = [t for t, _, _ in model]
    for title in task_titles:
        if title not in model_titles:
            problems.append(Problem(topic.path, answers.line, f"exam task '{title}' has no model answer (### {title})", "exam"))
    for title, line, text in model:
        if title not in task_titles:
            problems.append(Problem(topic.path, line, f"model answer '{title}' has no exam task", "exam"))
        elif not text:
            problems.append(Problem(topic.path, line, f"model answer '{title}' is empty", "exam"))
    shared = [t for t in model_titles if t in task_titles]
    if shared != [t for t in task_titles if t in model_titles]:
        problems.append(Problem(topic.path, answers.line, "model answers are not in the order of the exam tasks", "exam"))
    return problems


def table_headers(lines: list[str], start: int) -> list[tuple[int, list[str]]]:
    """(absolute line, cells) of the header row of every Markdown table in `lines`."""
    headers = []
    for index in range(len(lines) - 1):
        line, below = lines[index].strip(), lines[index + 1].strip()
        if line.startswith("|") and _SEPARATOR.match(below) and not _SEPARATOR.match(line):
            headers.append((start + index, [c.strip() for c in line.strip("|").split("|")]))
    return headers


def check_role_column(topic: Topic, subject: Subject) -> list[Problem]:
    """Every lesson plan table has the teacher's column (teacher.role_column); a warning, not a failure."""
    spec = next((s for s in subject.sections if s.plan), None)
    plan = topic.section(spec.title) if spec else None
    if plan is None:
        return []
    return [
        Problem(topic.path, line, f"plan table has no '{subject.role_column}' column", "plan-columns", True)
        for line, cells in table_headers(plan.lines, plan.line + 1)
        if subject.role_column not in cells
    ]
