"""Report repeated text: lukio-runko repeats [--root .] [--site DIR] [--fresh] [--json [FILE]] [--suggest-allow]

Runs the repeat check (repeat_checks.py) without changing anything in the site. It reads the existing build in
<root>/_site (or --site DIR); when there is none, or with --fresh, it builds the site into a temporary folder that is
deleted afterwards. It prints a summary and the clusters. --json FILE writes the full report, and --json alone
prints it instead of the listing. --suggest-allow prints the new clusters as allow-list entries with an empty reason,
for a person to fill in or reject. Exits 1 when the check has errors (for example with repeats.fail_on_new).
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from lukio_runko.allowed_repeats import ALLOW_KIND, suggested_entries
from lukio_runko.build import build_site
from lukio_runko.html_units import site_pages
from lukio_runko.repeat_checks import RepeatResult, check_repeats, report_json, write_report
from lukio_runko.subject import load_subject

PRINT_TO_SCREEN = "-"
LINE_SAMPLE = 100  # characters of each cluster's text in the listing


def run_check(root: Path, site: Path, fresh: bool) -> RepeatResult:
    """Check an existing build, or build into a temporary folder first."""
    subject = load_subject(root)
    if site.is_dir() and not fresh:
        if not site_pages(site):
            raise ValueError(f"{site} holds no built pages (index.html); build the site or use --fresh")
        return check_repeats(site, subject, root)
    with tempfile.TemporaryDirectory(prefix="lukio-repeats-") as scratch:
        built = Path(scratch) / "_site"
        build_site(root, built, partial=True, run_repeat_check=False)
        if not built.is_dir():
            raise ValueError("the site could not be built (a required static page is missing)")
        return check_repeats(built, subject, root)


def listing(result: RepeatResult) -> list[str]:
    """The summary, one line per cluster and near cluster, then drift, stale entries and broken allow-list entries."""
    lines = [result.summary]
    for entry in result.report["clusters"]:
        label = entry["status"] + (" stamped" if entry["stamped"] else "")
        lines.append(f"{entry['group_count']:>4} topics {entry['page_count']:>4} pages  {entry['id']}  {label:<15} {entry['sample'][:LINE_SAMPLE]}")
    for entry in result.report["near_clusters"]:
        first = entry["variants"][0]
        variants = len(entry["variants"])
        lines.append(f"{entry['group_count']:>4} topics {entry['page_count']:>4} pages  {entry['id']}  {variants} variants  {first['sample'][:LINE_SAMPLE]}")
    for item in result.report["drift"]:
        lines.append(f"drift: {item['variant']} is a near variant of allowed repeat {item['allowed']} (Jaccard {item['jaccard']})")
    for item in result.report["stale"]:
        lines.append(f"stale: allowed repeat {item['hash']} (line {item['line']}) matches no text on the site")
    lines += [str(problem) for problem in result.problems if problem.kind == ALLOW_KIND]
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="the site root that holds subject.yaml (default: the current folder)")
    parser.add_argument("--site", type=Path, default=None, help="the built site to read, default <root>/_site")
    parser.add_argument("--fresh", action="store_true", help="build into a temporary folder even when a build exists")
    parser.add_argument("--json", nargs="?", const=PRINT_TO_SCREEN, default=None, metavar="FILE", help="write the JSON report to FILE, or print it")
    parser.add_argument("--suggest-allow", action="store_true", help="print the new clusters as allow-list entries")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Finnish text and JSON must not depend on the console's code page
    try:
        result = run_check(args.root, args.site or args.root / "_site", args.fresh)
    except (FileNotFoundError, ValueError) as error:
        print(f"repeats: {error}", file=sys.stderr)
        return 1
    if args.json and args.json != PRINT_TO_SCREEN:
        write_report(Path(args.json), result.report)
    if args.suggest_allow:
        sys.stdout.write(suggested_entries([c for c in result.report["clusters"] if c["status"] == "new"]))
    elif args.json == PRINT_TO_SCREEN:
        sys.stdout.write(report_json(result.report))
    else:
        print("\n".join(listing(result)))
    return 1 if any(not problem.warning for problem in result.problems) else 0


if __name__ == "__main__":
    sys.exit(main())
