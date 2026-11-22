"""Text blocks of a built site, for the repeat check: every leaf block's text with its page region and tag.

The repeat check reads the built HTML, not the Markdown, because most stamped text comes from the page template and
the facts blocks, which the Markdown never shows. A block is one of BLOCK_TAGS (a paragraph, a list item, a table
cell, a heading, ...). A block inside another block owns its own text: the outer block keeps only the words outside
the inner one. `<br>` is a space. Each block records the region it is in (header, nav, main, aside or footer), so the
report can say where a repeat lives.

The parser is the standard library's HTMLParser, the same approach as site_checks.PageScan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

BLOCK_TAGS = frozenset(
    {
        "p", "li", "td", "th", "dt", "dd", "h1", "h2", "h3", "h4", "h5", "h6",
        "figcaption", "summary", "caption", "blockquote", "label", "button", "legend",
    }
)  # fmt: skip
REGION_TAGS = frozenset({"header", "nav", "main", "aside", "footer"})
SKIPPED_TAGS = frozenset({"script", "style", "template"})  # their contents are never shown as text
NO_REGION = "body"
PRINT_DIRECTORY = "tulosta"  # print pages repeat whole modules, so they would hide the real repeats


@dataclass(frozen=True)
class Block:
    """The text of one leaf block: tag, region and the text with its whitespace collapsed."""

    tag: str
    region: str
    text: str


@dataclass
class _OpenBlock:
    order: int
    tag: str
    region: str
    parts: list[str] = field(default_factory=list)


class BlockScan(HTMLParser):
    """Collects the leaf blocks of one page in document order (the order in which each block starts)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._found: list[tuple[int, Block]] = []
        self._open: list[_OpenBlock] = []
        self._regions: list[str] = []
        self._skipping = 0
        self._started = 0

    @property
    def blocks(self) -> list[Block]:
        return [block for _, block in sorted(self._found, key=lambda item: item[0])]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIPPED_TAGS:
            self._skipping += 1
        elif tag in REGION_TAGS:
            self._regions.append(tag)
        elif tag == "br":
            self._add_text(" ")
        elif tag in BLOCK_TAGS:
            region = self._regions[-1] if self._regions else NO_REGION
            self._open.append(_OpenBlock(self._started, tag, region))
            self._started += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIPPED_TAGS:
            self._skipping = max(0, self._skipping - 1)
        elif tag in REGION_TAGS and tag in self._regions:
            while self._regions.pop() != tag:
                pass
        elif tag in BLOCK_TAGS:
            self._close_block(tag)

    def handle_data(self, data: str) -> None:
        if not self._skipping:
            self._add_text(data)

    def close(self) -> None:
        super().close()
        while self._open:  # a block left open at the end of the file still counts
            self._emit(self._open.pop())

    def _add_text(self, text: str) -> None:
        if self._open:
            self._open[-1].parts.append(text)

    def _close_block(self, tag: str) -> None:
        """Close the innermost open block with this tag, and any block opened inside it that was never closed."""
        if not any(block.tag == tag for block in self._open):
            return
        while True:
            block = self._open.pop()
            self._emit(block)
            if block.tag == tag:
                return

    def _emit(self, block: _OpenBlock) -> None:
        text = " ".join("".join(block.parts).split())
        if text:
            self._found.append((block.order, Block(block.tag, block.region, text)))


def page_blocks(html_text: str) -> list[Block]:
    """The leaf blocks of one HTML page."""
    scan = BlockScan()
    scan.feed(html_text)
    scan.close()
    return scan.blocks


def site_pages(site_dir: Path) -> list[str]:
    """Every index.html of a built site except the print pages, as sorted site-relative paths."""
    pages = []
    for path in site_dir.rglob("index.html"):
        relative = path.relative_to(site_dir).as_posix()
        if relative.split("/", 1)[0] != PRINT_DIRECTORY:
            pages.append(relative)
    return sorted(pages)


def topic_group(page: str) -> str:
    """The topic a page belongs to: its folder, with a trailing /tunti removed so student and lesson page are one.

    'fi1/01-x/tunti/index.html' and 'fi1/01-x/index.html' are both 'fi1/01-x/'; the front page is '/'.
    """
    folder = page.rsplit("/", 1)[0] if "/" in page else ""
    if folder.endswith("/tunti"):
        folder = folder[: -len("/tunti")]
    elif folder == "tunti":
        folder = ""
    return folder + "/" if folder else "/"
