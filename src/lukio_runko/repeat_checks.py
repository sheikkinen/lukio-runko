"""The repeat check: sentences and paragraphs that repeat across a built site's pages.

Template boilerplate, warnings and reassurances stamped on every page make a site read like a form. This check finds
them with hashing and set arithmetic only (docs/repeat-check-plan.md); nothing reads meaning and nothing is random,
so the same site always gives byte-identical output.

1. Every page's leaf blocks (html_units) become paragraph units, and each paragraph's sentences become sentence
   units. A unit's id is the SHA-256 of its normalised text (textsig). Units under `min_words` words are dropped.
2. Exact tier: a unit found in enough topic groups is a cluster. The threshold is `min_share` of the groups, never
   fewer than `min_groups`. A student page and its lesson page (…/tunti/) are one group; print pages are left out.
3. Near tier: units of `near_min_words` words or more are compared by MinHash and confirmed by exact Jaccard. A near
   cluster is listed when merging its variants reaches the threshold and covers more groups than any one variant.
4. The allow-list (allowed_repeats) silences an exact text. An allowed text found in more groups than its
   `max_groups` (grown, checked whatever the threshold), a near variant of an allowed text (drift) and an entry that
   matches nothing (stale) are reported.

Problems are warnings, or errors when `repeats.fail_on_new` is true in subject.yaml. The full report is a JSON
document with site-relative paths only. The command `lukio-runko repeats` is in repeat_report.py.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path

from lukio_runko.allowed_repeats import ALLOW_FILE, AllowedRepeat, load_allowed_repeats
from lukio_runko.html_units import PRINT_DIRECTORY, page_blocks, site_pages, topic_group
from lukio_runko.models import Problem
from lukio_runko.subject import RepeatSettings, Subject
from lukio_runko.textsig import (
    BANDS,
    BINS,
    ROWS,
    SHINGLE_SIZE,
    UnionFind,
    candidate_pairs,
    jaccard,
    minhash,
    normalise,
    shingles,
    split_sentences,
    unit_id,
    word_count,
)

KIND = "repeat"
SAMPLE_LENGTH = 120  # characters of the original text shown in a build message
SITE_PREFIX = "_site/"  # how build messages name a page, the same as site_checks


@dataclass
class Unit:
    """One distinct normalised text and everywhere it was found."""

    id: str
    text: str  # normalised
    sample: str  # the original text of its first occurrence, in sorted page order
    words: int
    kinds: set[str] = field(default_factory=set)  # paragraph, sentence
    pages: set[str] = field(default_factory=set)
    groups: set[str] = field(default_factory=set)
    tags: set[str] = field(default_factory=set)
    regions: set[str] = field(default_factory=set)
    paragraphs: set[str] = field(default_factory=set)  # ids of the paragraphs that contain it as a sentence


@dataclass
class SiteIndex:
    """Every unit of a site, by id."""

    pages: list[str]
    groups: list[str]
    min_words: int  # shorter units are not recorded
    units: dict[str, Unit] = field(default_factory=dict)
    occurrences: int = 0


@dataclass
class NearCluster:
    """Units that are nearly the same text, joined through confirmed pairs."""

    members: list[str]
    pairs: list[tuple[str, str, float]]
    pages: set[str]
    groups: set[str]

    @property
    def id(self) -> str:
        return "near-" + self.members[0]


@dataclass
class RepeatResult:
    """What the check found: build problems, the JSON report as a dict, and the one-line summary."""

    problems: list[Problem]
    report: dict
    summary: str


# --- Units ---------------------------------------------------------------------------------------------------------


def _record(index: SiteIndex, text: str, kind: str, page: str, group: str, tag: str, region: str) -> str | None:
    """Add one occurrence of a text; return its unit id, or None when it is too short to count."""
    normalised = normalise(text)
    words = word_count(normalised)
    if words < index.min_words:
        return None
    key = unit_id(normalised)
    unit = index.units.get(key)
    if unit is None:
        unit = Unit(key, normalised, text, words)
        index.units[key] = unit
    unit.kinds.add(kind)
    unit.pages.add(page)
    unit.groups.add(group)
    unit.tags.add(tag)
    unit.regions.add(region)
    index.occurrences += 1
    return key


def index_site(site_dir: Path, settings: RepeatSettings) -> SiteIndex:
    """Read every page of a built site (print pages excluded) into units."""
    pages = site_pages(site_dir)
    index = SiteIndex(pages, sorted({topic_group(page) for page in pages}), settings.min_words)
    for page in pages:
        group = topic_group(page)
        for block in page_blocks((site_dir / page).read_text(encoding="utf-8")):
            paragraph = _record(index, block.text, "paragraph", page, group, block.tag, block.region)
            sentences = split_sentences(block.text)
            if len(sentences) < 2:
                continue  # a one-sentence paragraph is already its own unit
            for sentence in sentences:
                key = _record(index, sentence, "sentence", page, group, block.tag, block.region)
                if key and paragraph and key != paragraph:
                    index.units[key].paragraphs.add(paragraph)
    return index


def report_threshold(settings: RepeatSettings, group_count: int) -> int:
    """The number of topic groups a unit must reach to be reported: min_share of them, never fewer than min_groups."""
    share = math.ceil(round(settings.min_share * group_count, 9))  # round first: 0.1 * 30 is 3.0000000000000004
    return max(settings.min_groups, share)


# --- Exact and near clusters ---------------------------------------------------------------------------------------


def _by_spread(unit: Unit) -> tuple[int, str]:
    return (-len(unit.groups), unit.id)


def exact_clusters(index: SiteIndex, threshold: int) -> list[Unit]:
    """Units found in `threshold` groups or more, widest first.

    A sentence is left out when a reported paragraph that contains it has exactly the same pages: the paragraph
    already says it.
    """
    reported = {key for key, unit in index.units.items() if len(unit.groups) >= threshold}
    clusters = []
    for key in sorted(reported):
        unit = index.units[key]
        covered = any(parent in reported and index.units[parent].pages == unit.pages for parent in unit.paragraphs)
        if "paragraph" in unit.kinds or not covered:
            clusters.append(unit)
    return sorted(clusters, key=_by_spread)


def grown_allowed_units(index: SiteIndex, allowed: dict[str, AllowedRepeat]) -> list[Unit]:
    """Allowed texts on the site found in more groups than their max_groups, widest first.

    This does not depend on the report threshold: an entry with max_groups 1 must be reported when its text reaches
    a second topic, even though two topics are not enough to make a cluster.
    """
    grown = []
    for key, entry in sorted(allowed.items()):
        unit = index.units.get(key)
        if unit is not None and len(unit.groups) > entry.max_groups:
            grown.append(unit)
    return sorted(grown, key=_by_spread)


def reported_units(index: SiteIndex, threshold: int, allowed: dict[str, AllowedRepeat]) -> list[Unit]:
    """The units listed as clusters: every exact cluster, plus every grown allowed text not already among them."""
    clusters = exact_clusters(index, threshold)
    listed = {unit.id for unit in clusters}
    extra = [unit for unit in grown_allowed_units(index, allowed) if unit.id not in listed]
    return sorted(clusters + extra, key=_by_spread)


def find_near_clusters(index: SiteIndex, settings: RepeatSettings) -> list[NearCluster]:
    """Every group of two or more units joined by pairs at Jaccard >= near_jaccard, sorted by first member id."""
    # Only units long enough for near matching get shingles; short labels would match each other by chance.
    shingle_sets = {}
    for key, unit in sorted(index.units.items()):
        if unit.words >= settings.near_min_words:
            shingle_sets[key] = shingles(unit.text)
    signatures = {key: minhash(shingle_set) for key, shingle_set in shingle_sets.items()}
    joined = UnionFind()
    confirmed = []
    for first, second in candidate_pairs(signatures):
        similarity = jaccard(shingle_sets[first], shingle_sets[second])
        if similarity >= settings.near_jaccard:  # LSH only proposes pairs; the exact Jaccard decides
            joined.union(first, second)
            confirmed.append((first, second, round(similarity, 4)))
    pairs_by_root: dict[str, list[tuple[str, str, float]]] = {}
    for pair in confirmed:
        pairs_by_root.setdefault(joined.find(pair[0]), []).append(pair)
    clusters = []
    for members in joined.clusters():
        pairs = pairs_by_root[joined.find(members[0])]
        pages = set().union(*(index.units[key].pages for key in members))
        groups = set().union(*(index.units[key].groups for key in members))
        clusters.append(NearCluster(members, pairs, pages, groups))
    return clusters


def near_adds_groups(cluster: NearCluster, index: SiteIndex, threshold: int) -> bool:
    """A near cluster is worth listing when its variants together reach the threshold and cover more than any one."""
    widest = max(len(index.units[key].groups) for key in cluster.members)
    return len(cluster.groups) >= threshold and len(cluster.groups) > widest


# --- Allow-list results --------------------------------------------------------------------------------------------


def _related(index: SiteIndex, first: str, second: str) -> bool:
    """One unit is a sentence of the other: not a rewording."""
    return first in index.units[second].paragraphs or second in index.units[first].paragraphs


def find_drift(near: list[NearCluster], index: SiteIndex, allowed: dict[str, AllowedRepeat]) -> list[dict]:
    """Near variants of allowed texts: a reworded copy of an intended repeat is not covered by its entry."""
    drift = []
    for cluster in near:
        for allowed_id in (key for key in cluster.members if key in allowed):
            for variant in cluster.members:
                if variant in allowed or _related(index, allowed_id, variant):
                    continue
                similarity = jaccard(shingles(index.units[allowed_id].text), shingles(index.units[variant].text))
                drift.append({"allowed": allowed_id, "variant": variant, "jaccard": round(similarity, 4)})
    return sorted(drift, key=lambda item: (item["allowed"], item["variant"]))


def cluster_status(unit: Unit, allowed: dict[str, AllowedRepeat]) -> str:
    entry = allowed.get(unit.id)
    if entry is None:
        return "new"
    return "grown" if len(unit.groups) > entry.max_groups else "allowed"


# --- Report and problems -------------------------------------------------------------------------------------------


def _unit_entry(unit: Unit) -> dict:
    return {
        "id": unit.id,
        "text": unit.text,
        "sample": unit.sample,
        "words": unit.words,
        "kinds": sorted(unit.kinds),
        "tags": sorted(unit.tags),
        "regions": sorted(unit.regions),
        "group_count": len(unit.groups),
        "page_count": len(unit.pages),
        "groups": sorted(unit.groups),
        "pages": sorted(unit.pages),
    }


def _cluster_entry(unit: Unit, status: str, stamped: bool) -> dict:
    return {**_unit_entry(unit), "status": status, "stamped": stamped}


def _near_entry(cluster: NearCluster, index: SiteIndex) -> dict:
    variants = sorted((index.units[key] for key in cluster.members), key=_by_spread)
    return {
        "id": cluster.id,
        "group_count": len(cluster.groups),
        "page_count": len(cluster.pages),
        "groups": sorted(cluster.groups),
        "pages": sorted(cluster.pages),
        "variants": [_unit_entry(unit) for unit in variants],
        "pairs": [{"a": first, "b": second, "jaccard": value} for first, second, value in cluster.pairs],
    }


def _short(text: str) -> str:
    return text if len(text) <= SAMPLE_LENGTH else text[: SAMPLE_LENGTH - 1] + "…"


def _cluster_problem(entry: dict, total: int, allowed: dict[str, AllowedRepeat]) -> Problem:
    where = f"in {entry['group_count']} of {total} topics, {entry['page_count']} pages"
    stamped = ", stamped" if entry["stamped"] else ""
    if entry["status"] == "grown":
        limit = allowed[entry["id"]].max_groups
        sample = _short(entry["sample"])
        message = f"allowed repeat {entry['id']} has grown to {entry['group_count']} topics (max_groups {limit}): \"{sample}\""
    else:
        message = f"repeat {entry['id']} {where}{stamped}: \"{_short(entry['sample'])}\""
    return Problem(SITE_PREFIX + entry["pages"][0], 1, message, KIND)


def build_problems(report: dict, index: SiteIndex, allowed: dict[str, AllowedRepeat], settings: RepeatSettings) -> list[Problem]:
    """One problem per new or grown cluster, drift and stale entry; warnings unless fail_on_new."""
    total = len(index.groups)
    problems = [_cluster_problem(entry, total, allowed) for entry in report["clusters"] if entry["status"] != "allowed"]
    for item in report["drift"]:
        variant = index.units[item["variant"]]
        first_page = sorted(variant.pages)[0]
        sample = _short(variant.sample)
        message = f"near variant {variant.id} of allowed repeat {item['allowed']} (Jaccard {item['jaccard']}): \"{sample}\""
        problems.append(Problem(SITE_PREFIX + first_page, 1, message, KIND))
    for item in report["stale"]:
        problems.append(Problem(ALLOW_FILE, item["line"], f"allowed repeat {item['hash']} matches no text on the site", KIND))
    return problems if settings.fail_on_new else [problem.as_warning() for problem in problems]


def _parameters(settings: RepeatSettings, threshold: int) -> dict:
    fixed = {"shingle_size": SHINGLE_SIZE, "minhash_bins": BINS, "lsh_bands": BANDS, "lsh_rows": ROWS}
    return {**asdict(settings), **fixed, "threshold_groups": threshold, "excluded": [PRINT_DIRECTORY + "/"]}


def build_report(index: SiteIndex, settings: RepeatSettings, allowed: dict[str, AllowedRepeat]) -> dict:
    """The whole result as plain data: parameters, summary, clusters, near clusters, drift and stale entries."""
    threshold = report_threshold(settings, len(index.groups))
    stamped_at = len(index.groups) * settings.stamped_share
    clusters = []
    for unit in reported_units(index, threshold, allowed):
        is_stamped = len(unit.groups) >= stamped_at
        clusters.append(_cluster_entry(unit, cluster_status(unit, allowed), is_stamped))
    near = find_near_clusters(index, settings)
    # A near cluster is listed only if its variants together reach more topics than any one variant alone.
    useful_near = [c for c in near if near_adds_groups(c, index, threshold)]
    listed_near = sorted(useful_near, key=lambda c: (-len(c.groups), c.id))
    drift = find_drift(near, index, allowed)
    # An allow-list entry that matches no text on the site any more is stale.
    stale = []
    for key, entry in sorted(allowed.items()):
        if key not in index.units:
            stale.append({"hash": entry.hash, "text": entry.text, "line": entry.line})
    statuses = [entry["status"] for entry in clusters]
    summary = {
        "pages": len(index.pages),
        "groups": len(index.groups),
        "units": len(index.units),
        "occurrences": index.occurrences,
        "clusters": len(clusters),
        "new": statuses.count("new"),
        "allowed": statuses.count("allowed"),
        "grown": statuses.count("grown"),
        "stamped": sum(1 for entry in clusters if entry["stamped"]),
        "near": len(listed_near),
        "drift": len(drift),
        "stale": len(stale),
    }
    return {
        "parameters": _parameters(settings, threshold),
        "summary": summary,
        "clusters": clusters,
        "near_clusters": [_near_entry(cluster, index) for cluster in listed_near],
        "drift": drift,
        "stale": stale,
    }


def summary_line(summary: dict) -> str:
    return (
        f"repeats: {summary['pages']} pages, {summary['groups']} topics, {summary['units']} units, "
        f"{summary['clusters']} clusters ({summary['new']} new, {summary['allowed']} allowed, {summary['grown']} grown, "
        f"{summary['stamped']} stamped), {summary['near']} near, {summary['drift']} drift, {summary['stale']} stale"
    )


def check_repeats(site_dir: Path, subject: Subject, root: Path) -> RepeatResult:
    """Run the repeat check on a built site; `root` is the site root that holds data/allowed-repeats.yaml."""
    settings = subject.repeats
    allowed, problems = load_allowed_repeats(root, settings.min_words)
    index = index_site(site_dir, settings)
    report = build_report(index, settings, allowed)
    problems += build_problems(report, index, allowed, settings)
    return RepeatResult(problems, report, summary_line(report["summary"]))


def report_json(report: dict) -> str:
    """The report as JSON text: keys sorted, lists already sorted, so two runs give the same bytes."""
    return json.dumps(report, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_json(report), encoding="utf-8", newline="\n")
