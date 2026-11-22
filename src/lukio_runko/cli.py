"""The lukio-runko command: lukio-runko <build|fetch-curriculum|images|repeats|compare> [options]

Each subcommand takes its own options; `lukio-runko <subcommand> --help` lists them. build, fetch-curriculum,
images and repeats take --root, the site folder that holds subject.yaml (default: the current folder).
"""

from __future__ import annotations

import sys
from collections.abc import Callable

from lukio_runko import __version__


def _build(argv: list[str]) -> int:
    from lukio_runko.build import main

    return main(argv)


def _fetch(argv: list[str]) -> int:
    from lukio_runko.fetch_curriculum import main

    return main(argv)


def _images(argv: list[str]) -> int:
    from lukio_runko.images import main

    return main(argv)


def _repeats(argv: list[str]) -> int:
    from lukio_runko.repeat_report import main

    return main(argv)


def _compare(argv: list[str]) -> int:
    from lukio_runko.compare_sites import main

    return main(argv)


COMMANDS: dict[str, tuple[Callable[[list[str]], int], str]] = {
    "build": (_build, "build the site into <root>/_site and run every check"),
    "fetch-curriculum": (_fetch, "fetch the curriculum from ePerusteet into <root>/data/curriculum.yaml"),
    "images": (_images, "make the site's pictures from data/images*.yaml (needs GAME_ENGINE_DIR)"),
    "repeats": (_repeats, "report text that repeats across the built site's pages (read-only)"),
    "compare": (_compare, "compare two built sites byte for byte: compare GOLDEN BUILT"),
}


def usage() -> str:
    lines = [f"usage: lukio-runko <command> [options]   (lukio-runko {__version__})", "", "commands:"]
    lines += [f"  {name:<17} {text}" for name, (_, text) in COMMANDS.items()]
    lines += ["", "lukio-runko <command> --help shows the command's options."]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(usage())
        return 0 if args else 2
    if args[0] == "--version":
        print(f"lukio-runko {__version__}")
        return 0
    command = COMMANDS.get(args[0])
    if command is None:
        print(f"lukio-runko: unknown command {args[0]!r}\n\n{usage()}", file=sys.stderr)
        return 2
    return command[0](args[1:])
