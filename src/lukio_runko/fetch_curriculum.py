"""Fetch the subject's national core curriculum from the ePerusteet API.

The peruste, oppiaine and module ids, the codes and their expected counts come from subject.yaml. Writes
data/curriculum.yaml with the exact Finnish wording keyed by code: <MODULE>.t<n> and <MODULE>.s<n> for each module
and <SUBJECT>.yt<n> for the general aims, in ePerusteet order. HTML is stripped here, at the boundary; nothing
downstream sees markup.

Usage: lukio-runko fetch-curriculum [--root .] [--input saved.json] [--output data/curriculum.yaml]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import yaml

from lukio_runko.subject import Subject, load_subject

API_URL = "https://eperusteet.opintopolku.fi/eperusteet-service/api/perusteet/{peruste_id}/kaikki"
MAX_TRIES = 2

_BLOCK_END = re.compile(r"</(p|div|li|h[1-6])>|<br\s*/?>", re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")


class CurriculumError(Exception):
    """The API answer does not have the shape the contract expects."""


def clean_paragraphs(raw: str | None) -> list[str]:
    """Strip HTML; return the non-empty paragraphs with whitespace collapsed."""
    if not raw:
        return []
    text = _BLOCK_END.sub("\n", re.sub(r"\s+", " ", raw))
    text = html.unescape(_TAG.sub("", text)).replace("\xa0", " ")
    paragraphs = (re.sub(r"\s+", " ", line).strip() for line in text.split("\n"))
    return [p for p in paragraphs if p]


def clean_text(raw: str | None) -> str:
    return "\n\n".join(clean_paragraphs(raw))


def finnish(node: dict | None) -> str:
    """The Finnish text of an ePerusteet localised string."""
    if not node:
        return ""
    return clean_text(node.get("fi"))


def _last_sunday_utc(year: int, month: int) -> datetime:
    """01:00 UTC on the last Sunday of the month, when EU summer time changes."""
    day = datetime(year, month + 1, 1, 1, tzinfo=UTC) if month < 12 else datetime(year + 1, 1, 1, 1, tzinfo=UTC)
    day -= timedelta(days=1)
    return day - timedelta(days=(day.weekday() + 1) % 7)


def millis_to_date(millis: int) -> date:
    """The calendar date in Finland. Computed by hand so that no tz database is needed."""
    moment = datetime.fromtimestamp(millis / 1000, tz=UTC)
    summer = _last_sunday_utc(moment.year, 3) <= moment < _last_sunday_utc(moment.year, 10)
    return (moment + timedelta(hours=3 if summer else 2)).date()


def _find_by_id(items: list[dict], wanted: int, what: str) -> dict:
    for item in items:
        if item.get("id") == wanted:
            return item
    raise CurriculumError(f"{what} {wanted} not found in the API answer")


def _module_codes(prefix: str, module: dict) -> dict[str, dict]:
    codes: dict[str, dict] = {}
    objectives = [finnish(o) for o in module["tavoitteet"]["tavoitteet"]]
    contents = [finnish(c) for group in module["sisallot"] for c in group["sisallot"]]
    for number, text in enumerate(objectives, 1):
        codes[f"{prefix}.t{number}"] = {"kind": "tavoite", "module": prefix, "text": text}
    for number, text in enumerate(contents, 1):
        codes[f"{prefix}.s{number}"] = {"kind": "sisalto", "module": prefix, "text": text}
    return codes


def api_url(subject: Subject) -> str:
    return API_URL.format(peruste_id=subject.peruste_id)


def _sort_key(subject: Subject, code: str) -> tuple:
    groups = {subject.code: 0} | {m.code: n for n, m in enumerate(subject.modules, 1)}
    group = groups[code.split(".")[0]]
    kind = re.sub(r"\d+$", "", code.split(".")[1])
    number = int(re.search(r"\d+$", code).group())
    return (group, {"yt": 0, "t": 1, "s": 2}[kind], number)


def _check_counts(subject: Subject, codes: dict[str, dict]) -> None:
    for prefix, expected in subject.expected_counts.items():
        found = sum(1 for c in codes if re.fullmatch(re.escape(prefix) + r"\d+", c))
        if found != expected:
            raise CurriculumError(f"{prefix}: expected {expected} codes, found {found}. The curriculum changed: update docs/content-contract.md first.")


def parse_curriculum(data: dict, checked: date, spec: Subject) -> dict:
    """Turn the raw ePerusteet record into the structure of data/curriculum.yaml."""
    subject = _find_by_id(data["lops2019"]["oppiaineet"], spec.oppiaine_id, "oppiaine")
    codes: dict[str, dict] = {}
    aims_lead = ""
    number = 0
    for area in subject["tavoitteet"]["tavoitealueet"]:
        if not aims_lead:
            aims_lead = f"{finnish(area.get('nimi'))} {finnish(area.get('kohde'))}".strip()
        for aim in area["tavoitteet"]:
            number += 1
            codes[f"{spec.code}.yt{number}"] = {"kind": "yleinen_tavoite", "module": spec.code, "text": finnish(aim)}
    assessment = clean_paragraphs(((subject.get("arviointi") or {}).get("kuvaus") or {}).get("fi"))
    modules: dict[str, dict] = {}
    for prefix, module_id in ((m.code, m.id) for m in spec.modules):
        module = _find_by_id(subject["moduulit"], module_id, "module")
        codes.update(_module_codes(prefix, module))
        modules[prefix] = {
            "id": module_id,
            "name": finnish(module["nimi"]),
            "credits": module["laajuus"],
            "mandatory": bool(module["pakollinen"]),
            "objectives_lead": finnish(module["tavoitteet"].get("kohde")),
        }
    _check_counts(spec, codes)
    ordered = dict(sorted(codes.items(), key=lambda item: _sort_key(spec, item[0])))
    return {
        "source": {
            "peruste_id": spec.peruste_id,
            "diaarinumero": data["diaarinumero"],
            "name": finnish(data.get("nimi")),
            "in_force_from": millis_to_date(data["voimassaoloAlkaa"]).isoformat(),
            "last_published": millis_to_date(data["viimeisinJulkaisuAika"]).isoformat(),
            "checked": checked.isoformat(),
            "api_url": api_url(spec),
        },
        "subject": {
            "id": spec.oppiaine_id,
            "code": spec.code,
            "name": finnish(subject["nimi"]),
            "aims_lead": aims_lead,
            "assessment": assessment,
        },
        "modules": modules,
        "codes": ordered,
    }


def download(url: str, agent: str) -> dict:
    """Download the record. At most two tries; no further retries."""
    last_error: Exception | None = None
    for _ in range(MAX_TRIES):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": agent})
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
    raise CurriculumError(f"Could not read {url} in {MAX_TRIES} tries: {last_error}")


def write_curriculum(curriculum: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    header = "# Generated by lukio-runko fetch-curriculum from the ePerusteet API. Do not edit by hand.\n"
    body = yaml.safe_dump(curriculum, allow_unicode=True, sort_keys=False, width=100000)
    output.write_text(header + body, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="the site root that holds subject.yaml")
    parser.add_argument("--input", type=Path, help="parse a saved API answer instead of downloading")
    parser.add_argument("--output", type=Path, default=None, help="default <root>/data/curriculum.yaml")
    args = parser.parse_args(argv)
    args.output = args.output or args.root / "data" / "curriculum.yaml"
    try:
        spec = load_subject(args.root)
        data = json.loads(args.input.read_text(encoding="utf-8")) if args.input else download(api_url(spec), f"{spec.slug}-build")
        curriculum = parse_curriculum(data, date.today(), spec)
    except (CurriculumError, KeyError, FileNotFoundError, ValueError) as error:
        print(f"fetch_curriculum: {error}", file=sys.stderr)
        return 1
    write_curriculum(curriculum, args.output)
    print(f"wrote {args.output} ({len(curriculum['codes'])} codes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
