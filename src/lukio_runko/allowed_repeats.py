"""The allow-list of the repeat check: data/allowed-repeats.yaml, the repeats a site keeps on purpose.

Each entry pins one exact text by its hash, so new or reworded boilerplate is never hidden:

    - hash: 3f9a1c0e7b2d4a55
      text: "Arvioi jokainen kohta asteikolla En vielä · Osittain · Melko hyvin · Hyvin."
      reason: Self-assessment scale, the same on every topic by design.
      max_groups: 50

The match is on `hash` only. `text` is there for a person to review, and it must normalise to the hash, or the entry
is an error (a reworded line has another hash). The text must also have at least `min_words` words once normalised:
shorter texts are never counted, so such an entry could never match anything. `reason` and `max_groups` are required. A broken entry is reported
as an error and allows nothing. There is no allowance by tag or region: a boilerplate sentence put in a heading would
be hidden by one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from lukio_runko.models import Problem
from lukio_runko.textsig import normalise, unit_id, word_count

ALLOW_FILE = "data/allowed-repeats.yaml"
ALLOW_KIND = "repeat-allow-list"  # problems in the file itself: always errors, also with --partial
ENTRY_KEYS = ("hash", "text", "reason", "max_groups")
HASH = re.compile(r"^[0-9a-f]{16}$")


@dataclass(frozen=True)
class AllowedRepeat:
    """One entry of the allow-list, with the line it starts on."""

    hash: str
    text: str
    reason: str
    max_groups: int
    line: int


def _entry_lines(text: str) -> list[int]:
    """The line each top-level list entry starts on, so a problem can point at its entry."""
    node = yaml.compose(text)
    if not isinstance(node, yaml.SequenceNode):
        return []
    return [item.start_mark.line + 1 for item in node.value]


def _text_problems(text: object, hash_value: object, min_words: int) -> list[str]:
    """What is wrong with an entry's text: it must be a string that normalises to the hash and is long enough."""
    if not isinstance(text, str):
        return ["text must be a string"]
    normalised = normalise(text)
    messages = []
    if unit_id(normalised) != hash_value:
        messages.append(f"text normalises to {unit_id(normalised)}, not to the hash {hash_value}")
    words = word_count(normalised)
    if words < min_words:
        # The check never records a text this short, so the entry would stay stale and could not be fixed.
        messages.append(f"text has {words} words, fewer than min_words {min_words}; so short a text is never counted and needs no entry")
    return messages


def _entry_problems(raw: object, min_words: int) -> list[str]:
    """What is wrong with one entry, as messages; an empty list means the entry is valid."""
    if not isinstance(raw, dict):
        return ["an entry must be a mapping with hash, text, reason and max_groups"]
    messages = [f"unknown key {key!r}" for key in sorted(map(str, raw)) if key not in ENTRY_KEYS]
    messages += [f"{key} is missing" for key in ENTRY_KEYS if raw.get(key) in (None, "")]
    if messages:
        return messages
    hash_value, text = raw["hash"], raw["text"]
    if not isinstance(hash_value, str) or not HASH.match(hash_value):
        messages.append(f"hash must be 16 lowercase hex characters, found {hash_value!r}")
    messages += _text_problems(text, hash_value, min_words)
    if not isinstance(raw["reason"], str) or not raw["reason"].strip():
        messages.append("reason must be a sentence saying why the repeat is intended")
    max_groups = raw["max_groups"]
    if isinstance(max_groups, bool) or not isinstance(max_groups, int) or max_groups < 1:
        messages.append(f"max_groups must be a whole number of at least 1, found {max_groups!r}")
    return messages


def load_allowed_repeats(root: Path, min_words: int) -> tuple[dict[str, AllowedRepeat], list[Problem]]:
    """The valid entries by hash, and an error for every broken entry. A site without the file allows nothing.

    `min_words` is the site's repeats.min_words: an entry whose text is shorter could never match a unit.
    """
    path = root / ALLOW_FILE
    if not path.is_file():
        return {}, []
    text = path.read_text(encoding="utf-8")
    try:
        raw = yaml.safe_load(text)
        lines = _entry_lines(text)
    except yaml.YAMLError as error:
        return {}, [Problem(ALLOW_FILE, 1, f"the file is not valid YAML: {error}", ALLOW_KIND)]
    if raw is None:
        return {}, []
    if not isinstance(raw, list):
        return {}, [Problem(ALLOW_FILE, 1, "the file must be a list of entries", ALLOW_KIND)]
    allowed: dict[str, AllowedRepeat] = {}
    problems = []
    for index, entry in enumerate(raw):
        line = lines[index] if index < len(lines) else 1
        messages = _entry_problems(entry, min_words)
        if not messages and entry["hash"] in allowed:
            messages = [f"hash {entry['hash']} is listed twice"]
        if messages:
            problems += [Problem(ALLOW_FILE, line, f"allowed repeat: {message}", ALLOW_KIND) for message in messages]
            continue
        allowed[entry["hash"]] = AllowedRepeat(entry["hash"], entry["text"], entry["reason"].strip(), entry["max_groups"], line)
    return allowed, problems


def suggested_entries(clusters: list[dict]) -> str:
    """Report clusters as allow-list entries with an empty reason, for a person to fill in or reject.

    Each entry's text is the cluster's sample, an original occurrence, so it normalises to the hash. max_groups is
    the cluster's current spread.
    """
    entries = [{"hash": c["id"], "text": c["sample"], "reason": "", "max_groups": c["group_count"]} for c in clusters]
    if not entries:
        return "# no repeats to suggest\n"
    header = "# Suggested entries for data/allowed-repeats.yaml. Fill in each reason, or delete the entry and fix the text.\n"
    return header + yaml.safe_dump(entries, allow_unicode=True, sort_keys=False, width=1000)
