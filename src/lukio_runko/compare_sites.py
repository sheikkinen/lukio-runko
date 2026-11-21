"""Compare two built sites byte for byte: lukio-runko compare tmp/golden _site

Lists every file that differs, is missing from one side, or exists only in the other. Exits 1 if any.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def files(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def compare(golden: Path, built: Path) -> list[str]:
    """One line per difference, sorted: 'differs: x', 'only in golden: x', 'only in built: x'."""
    a, b = files(golden), files(built)
    lines = [f"only in golden: {p}" for p in sorted(a - b)]
    lines += [f"only in built: {p}" for p in sorted(b - a)]
    lines += [f"differs: {p}" for p in sorted(a & b) if (golden / p).read_bytes() != (built / p).read_bytes()]
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("golden", type=Path)
    parser.add_argument("built", type=Path)
    args = parser.parse_args(argv)
    lines = compare(args.golden, args.built)
    for line in lines:
        print(line)
    print(f"compare: {len(files(args.golden))} files in golden, {len(lines)} differences")
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
