"""Text signatures for the repeat check: normalising, sentence splitting, unit ids and near-duplicate search.

The repeat check (docs/repeat-check-plan.md) asks one question: which sentences and paragraphs appear, word for word
or nearly so, on many pages of a site? Everything here answers it with hashing and set arithmetic only. Nothing reads
meaning, and nothing is random: Python's own hash() changes between runs (PYTHONHASHSEED), so it is never used; the
hash functions are SHA-256 and CRC-32, and every collection is sorted before it is turned into output.

- normalise(): the word sequence of a text, so that markup, punctuation, case, dates and numbers never matter.
- split_sentences(): a paragraph cut into sentences.
- unit_id(): the first 16 hex characters of the SHA-256 of a normalised text.
- shingles(), minhash(), candidate_pairs(), jaccard(): find texts that are nearly the same (the near tier).
- UnionFind: joins the confirmed near pairs into clusters.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
import zlib
from collections.abc import Iterable

# --- Normalising ---------------------------------------------------------------------------------------------------

URL = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
INVISIBLE = re.compile("[­​‌‍⁠﻿]")  # soft hyphen and zero-width marks split no word
DATE = re.compile(r"(?<!\d)(?:\d{1,2}\.\d{1,2}\.\d{4}|\d{4}-\d{1,2}-\d{1,2})(?!\d)")
DIGITS = re.compile(r"\d+")
# A word is a run of letters and the two marks, so "OP1" is the one word "op<n>", not two.
TOKEN = re.compile(r"(?:<pvm>|<n>|\w)+")
DATE_MARK = "<pvm>"
NUMBER_MARK = "<n>"


def normalise(text: str) -> str:
    """The word sequence of a text, lower case, with dates as <pvm> and numbers as <n>.

    The steps follow the plan in order: Unicode NFC, URLs removed, casefold, dates, digit runs, and then every run of
    other characters becomes one space. Two texts that differ only in markup, punctuation, case or a number count as
    the same text.
    """
    text = unicodedata.normalize("NFC", text)
    text = INVISIBLE.sub("", text)
    text = URL.sub(" ", text)
    text = text.casefold()
    text = DATE.sub(DATE_MARK, text)
    text = DIGITS.sub(NUMBER_MARK, text)
    return " ".join(TOKEN.findall(text))


def word_count(normalised: str) -> int:
    return len(normalised.split())


def unit_id(normalised: str) -> str:
    """The id of a unit: the first 16 hex characters of the SHA-256 of its normalised UTF-8 text."""
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:16]


# --- Sentence splitting --------------------------------------------------------------------------------------------

# A possible end of a sentence: one or more end marks, any closing quotes or brackets, then whitespace.
SENTENCE_END = re.compile(r"[.!?…]+[\"'”’»)\]]*\s+")
SENTENCE_OPENERS = "\"'“”„«»‘’(["
# Finnish abbreviations that end in a full stop but do not end a sentence. The list only stops wrong splits ("esim.
# Helsinki"); it never decides what the check reports.
ABBREVIATIONS = frozenset(
    {
        "esim", "jne", "ks", "yms", "ym", "mm", "ns", "tms", "vrt", "ts", "n", "ca", "kpl", "klo", "os", "s", "ss",
        "v", "vs", "nro", "huom", "prof", "tri", "toim", "suom", "engl", "lat", "ruots", "milj", "mrd", "puh",
        "eaa", "jaa", "ekr", "jkr", "lk", "sis", "yl", "erit", "mr", "dr",
    }
)  # fmt: skip


def _starts_sentence(character: str) -> bool:
    return character.isupper() or character.isdigit() or character in SENTENCE_OPENERS


def _word_before(text: str, position: int) -> str:
    """The word that ends just before `position`, without opening quotes or brackets."""
    found = re.search(r"(\S+)$", text[:position])
    return found.group(1).lstrip(SENTENCE_OPENERS) if found else ""


def _is_false_end(text: str, mark: re.Match, next_character: str) -> bool:
    """A full stop after an abbreviation, an initial ("J. V. Snellman") or in a list of ordinals ("1. ja 2.")."""
    # Only a single full stop can be a false end; "!", "?" and an ellipsis ("..") always end a sentence.
    if not mark.group().startswith(".") or mark.group().startswith(".."):
        return False
    word = _word_before(text, mark.start())
    if word.casefold() in ABBREVIATIONS:
        return True
    if len(word) == 1 and word.isalpha() and word.isupper():
        return True
    return word.isdigit() and next_character.isdigit()


def split_sentences(paragraph: str) -> list[str]:
    """Cut a paragraph at '.', '!', '?' or '…' followed by whitespace and an uppercase letter, digit, quote or bracket."""
    sentences = []
    start = 0
    for mark in SENTENCE_END.finditer(paragraph):
        if mark.end() >= len(paragraph):
            break
        next_character = paragraph[mark.end()]
        if not _starts_sentence(next_character) or _is_false_end(paragraph, mark, next_character):
            continue
        sentences.append(paragraph[start : mark.end()].strip())
        start = mark.end()
    last = paragraph[start:].strip()
    if last:
        sentences.append(last)
    return sentences


# --- Near tier: shingles, MinHash and LSH --------------------------------------------------------------------------

SHINGLE_SIZE = 5  # character 5-grams: a Finnish case ending changes only a few of them
BINS = 64  # one-permutation MinHash with 64 bins
BANDS = 16  # LSH: 16 bands of 4 rows; two texts at Jaccard 0.8 share a band with probability about 0.9999
ROWS = BINS // BANDS
PRIME = (1 << 61) - 1  # a Mersenne prime larger than any CRC-32 value, so the permutation below is one to one
BIN_SPAN = PRIME // BINS + 1  # larger than any value inside one bin; used to mark a borrowed value's distance


def _permutation_constants() -> tuple[int, int]:
    """The fixed permutation h -> (a*h + b) mod PRIME, with a and b taken from a SHA-256 digest, not from a seed."""
    digest = hashlib.sha256(b"lukio-runko repeat check: minhash permutation").digest()
    multiplier = int.from_bytes(digest[:8], "big") % (PRIME - 1) + 1
    offset = int.from_bytes(digest[8:16], "big") % PRIME
    return multiplier, offset


MULTIPLIER, OFFSET = _permutation_constants()


def shingles(normalised: str) -> frozenset[int]:
    """The CRC-32 values of the text's character 5-grams; a text shorter than that is one shingle."""
    if len(normalised) <= SHINGLE_SIZE:
        return frozenset({zlib.crc32(normalised.encode("utf-8"))})
    grams = (normalised[i : i + SHINGLE_SIZE] for i in range(len(normalised) - SHINGLE_SIZE + 1))
    return frozenset(zlib.crc32(gram.encode("utf-8")) for gram in grams)


def minhash(shingle_set: Iterable[int]) -> tuple[int, ...]:
    """A 64-value signature: each shingle is permuted once, its bin is the value mod 64, and each bin keeps its minimum.

    A short text leaves some bins empty. An empty bin borrows the value of the next filled bin to its right (going
    round), plus a mark of the distance, so that two texts agree on a bin about as often as their shingle sets agree.
    """
    lowest: list[int | None] = [None] * BINS
    for shingle in shingle_set:
        permuted = (MULTIPLIER * shingle + OFFSET) % PRIME
        index, value = permuted % BINS, permuted // BINS
        current = lowest[index]
        if current is None or value < current:
            lowest[index] = value
    return tuple(_fill_empty_bins(lowest))


def _fill_empty_bins(lowest: list[int | None]) -> list[int]:
    filled = []
    for index in range(BINS):
        for distance in range(BINS):
            value = lowest[(index + distance) % BINS]
            if value is not None:
                filled.append(value + distance * BIN_SPAN)
                break
    return filled


def candidate_pairs(signatures: dict[str, tuple[int, ...]]) -> list[tuple[str, str]]:
    """Pairs of ids whose signatures agree on all 4 rows of at least one band, sorted."""
    buckets: dict[tuple[int, tuple[int, ...]], list[str]] = {}
    for key in sorted(signatures):
        signature = signatures[key]
        for band in range(BANDS):
            rows = signature[band * ROWS : (band + 1) * ROWS]
            buckets.setdefault((band, rows), []).append(key)
    pairs = set()
    for members in buckets.values():
        for i, first in enumerate(members):
            for second in members[i + 1 :]:
                pairs.add((first, second))  # members are in sorted order, so first < second
    return sorted(pairs)


def jaccard(first: frozenset[int], second: frozenset[int]) -> float:
    """The exact Jaccard similarity of two shingle sets: shared shingles divided by all shingles."""
    union = len(first | second)
    return len(first & second) / union if union else 1.0


# --- Clusters ------------------------------------------------------------------------------------------------------


class UnionFind:
    """Joins ids into clusters. The smaller id always becomes the root, so the result never depends on order."""

    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, key: str) -> str:
        self.parent.setdefault(key, key)
        while self.parent[key] != key:
            self.parent[key] = self.parent[self.parent[key]]  # path halving keeps the trees shallow
            key = self.parent[key]
        return key

    def union(self, first: str, second: str) -> None:
        root_a, root_b = self.find(first), self.find(second)
        if root_a != root_b:
            low, high = sorted((root_a, root_b))
            self.parent[high] = low

    def clusters(self) -> list[list[str]]:
        """Every cluster of two or more ids, each sorted, the list sorted by its first id."""
        members: dict[str, list[str]] = {}
        for key in sorted(self.parent):
            members.setdefault(self.find(key), []).append(key)
        return sorted(group for group in members.values() if len(group) > 1)
