# Repeat check: plan (2026-11-22, implemented the same day; see Implementation notes)

## Goal

Find sentences and paragraphs that repeat across a site's pages: template boilerplate, warnings,
disclaimers and reassurances stamped on every page. The check runs in every build and in CI. It
uses only hashing and set arithmetic. Nothing in it reads meaning: no LLM, no keyword list, no
randomness. The same input always gives byte-identical output.

It reports what repeats (exact and near-exact), on how many topics and pages, and which pages. A
site can declare intended repeats, but each declaration is pinned to one exact text, so new or
reworded boilerplate is never hidden.

## Units and normalisation

- Source: built HTML, not Markdown, since most stamped text comes from templates and facts blocks.
  Every `index.html` except `tulosta/` (print pages repeat whole modules; including them raises
  the repeated share from 45% to 63% in filosofia).
- Topic group: a page's path with a trailing `/tunti` removed, so a topic's student page and
  lesson page count as one topic. Spread is counted in groups.
- Paragraph unit: the text of one leaf block element (p, li, td, th, dt, dd, h1-h6, figcaption,
  summary, caption, blockquote, label, button, legend). Nested blocks own their own text, and
  `<br>` is a space.
- Sentence unit: a paragraph split at `.`, `!`, `?` or `…` followed by whitespace and an uppercase
  letter, digit, quote or bracket. A short abbreviation list (esim, jne, ks, yms, ...) only stops
  wrong splits. It never decides what is reported.
- Each unit records its region (header, nav, main, aside, footer) and its tag. Normalisation, in
  order: Unicode NFC; URLs removed; casefold; dates (d.m.yyyy, yyyy-mm-dd) to `<pvm>`; digit runs
  to `<n>`; every run of non-word characters to one space; trim. Markup, punctuation and case
  never matter, only the word sequence does. Units under 4 words are dropped.

## Method and fixed parameters

1. Exact tier (the gate). SHA-256 of the normalised UTF-8 text. The first 16 hex characters are
   the unit id. An inverted index maps each id to its pages and groups. A sentence cluster with
   exactly the same page set as a paragraph cluster that contains it is not listed again.
2. Near tier (report-only at first). Only units of 8 or more words. Character 5-gram shingles
   hashed with `zlib.crc32`, one-permutation MinHash with 64 bins, and LSH with 16 bands of 4
   rows. Every candidate pair is verified by exact Jaccard on the shingle sets and kept at Jaccard
   >= 0.8. Verified pairs are joined by union-find. Character grams tolerate Finnish inflection.
3. Python's `hash()`, unsorted set order and random seeds are never used. All output is sorted.

Why not vectors: TF-IDF cosine found the same families as MinHash, took 2 to 13 s per site
(MinHash 1 to 4.5 s) and its clustering shifts when a page is added. MinHash plus exact Jaccard
had recall 1.000 at 0.8. Vectors stay out unless MinHash is later shown to miss real cases.

## Thresholds

| Setting | Default | Meaning |
|---|---|---|
| `min_share` | 0.10, never fewer than 3 groups | report a unit found in this share of topic groups |
| `stamped_share` | 0.50 | "stamped": an error once the site is in error mode |
| `near_jaccard` | 0.8 | near tier threshold |
| `min_words` / `near_min_words` | 4 / 8 | unit length rules |

Each value can be overridden per site in `subject.yaml` under `repeats:`. The loader in
`subject.py` validates the keys and types. Example: filosofia has 50 groups, so the default
reports units found in 5 or more topics.

## Allow-list

Intended repeats live in the site file `data/allowed-repeats.yaml`:

```yaml
- hash: 3f9a1c0e7b2d4a55
  text: "Arvioi jokainen kohta asteikolla En vielä · Osittain · Melko hyvin · Hyvin."
  reason: Self-assessment scale, the same on every topic by design.
  max_groups: 50
```

- The match is on `hash` only. `text` is there for review and must normalise to that hash, or the
  entry is an error. A reworded line has a different hash, so it is never allowed silently.
- `text` must have at least `min_words` words once normalised, or the entry is an error: a shorter
  text is never counted, so it needs no entry and such an entry could never match.
- `reason` and `max_groups` are required. An allowed text found in more topic groups than its
  `max_groups` is reported as grown, also when it stays below the report threshold. A near-tier
  variant of an allowed text is reported as drift. An entry that matches nothing is stale.
- Structural headings and labels of `min_words` words or more (for example "Esimerkki malliksi
  kelpaavasta vastauksesta") are allowed the same way, one entry each. Shorter labels such as
  "Malliksi kelpaava vastaus" are below `min_words` and are never reported. There is no blanket allowance by tag or region, because a boilerplate
  sentence put in a heading would be hidden.

## Outputs

- Build: one summary line (pages, groups, units, clusters, new, allowed, drift, stale) and one
  `Problem` of kind `repeat` per non-allowed cluster. The message gives the group and page counts
  and the first 120 characters, with `file` set to the first page. These are warnings by default.
- Error mode: `repeats.fail_on_new: true` in `subject.yaml` turns new clusters, stamped units,
  growth, drift and stale entries into errors, so CI fails on them.
- JSON report `repeats.json` in the build output, beside the site and not inside it. It holds the
  parameters, every cluster (id, normalised text, sample original text, tags, regions, groups,
  site-relative pages), near clusters with their variants and Jaccard values, and stale entries.
  It is sorted by groups descending, then id, and contains no absolute paths.
- CLI: `lukio-runko repeats --root X [--json FILE] [--suggest-allow]` reads an existing build
  without changing it. `--suggest-allow` prints current clusters as allow-list entries with an
  empty `reason`, for a person to fill in or reject.

## Where it runs

`build.build_site` calls `repeat_checks.check_repeats(out, subject)` right after
`checks.check_internal_links_and_headings(out)`, so it sees the final HTML. `--partial` downgrades
`repeat` to a warning (add it to `PARTIAL_KINDS`). CI already runs the build and uploads
`repeats.json` as an artifact. Code goes in `html_units.py` (the extractor, same `HTMLParser`
approach as `site_checks.PageScan`), `textsig.py` (normaliser, splitter, hashing, MinHash,
union-find) and `repeat_checks.py` (config, allow-list, problems). Each stays under 500 lines and
uses the standard library only.

## Tests (no network)

- Normalisation (NFC, casefold, URLs, dates, numbers, punctuation) and sentence splitting
  (abbreviations, `1. vuosi`).
- A small fixture site: a line stamped on 3 topics is flagged, a student/tunti pair counts as one
  group, and `tulosta/` is ignored.
- A one-word slot variant forms a near cluster; a short unit does not. Two runs with different
  `PYTHONHASHSEED` values give identical JSON; error mode turns new clusters into errors.
- Allow-list: an allowed hash is silent; a reworded copy is drift; growth past `max_groups` is
  reported; a stale entry is a warning (an error with `fail_on_new`), and a text/hash mismatch is an error.

## Rollout per site

1. Ship in warning mode. Build each site and keep its `repeats.json` as the baseline.
2. Clean up: rewrite or remove stamped prose, and move what must stay to the allow-list with a
   reason. Expect a few hundred clusters per site at first.
3. When a build has no new clusters, set `fail_on_new: true` for that site. From then on any new
   or grown repeat fails CI.
4. Add a dated section to `docs/content-guideline.md` on declaring a repeat.

## What it deliberately does not do

- No LLM, no embeddings, no meaning. A repeat is defined only by identical or near-identical
  normalised text and how far it spreads.
- No keyword or phrase list decides what counts as boilerplate. It does not find rewording beyond
  surface similarity. A reassurance written with different words is left to human review.

## Measured numbers (prototypes, 2026-11-22)

Builds with 0 errors and 0 warnings, `tulosta/` excluded. Order: opinto / terveys / filo / psyk.

- Pages 44 / 69 / 90 / 29; topic groups 26 / 39 / 50 / 18. Sentence occurrences (4+ words) 7,469 /
  15,726 / 19,252 / 5,379; unique sentences 3,768 / 9,388 / 11,190 / 3,233.
- Sentences in 2+ groups: 430 / 982 / 970 / 351 (43-49% of occurrences). In 3+ groups: 240 / 385 /
  430 / 178. In 10+ groups: 70 / 106 / 119 / 65.
- Paragraphs in 3+ groups: 166 / 252 / 323 / 123. On 80%+ of pages: 13 / 13 / 16 / 5 sentences.
- Near tier: reworded variants that exact hashing misses are 1.3-1.8% of sentence occurrences, and
  21 / 27 / 44 / 11 near clusters reach 3+ groups only through near-merging. MinHash at 0.8 had
  recall 1.000 against brute force, and only 3 of 529 clusters chained a member below 0.6.
- Runtime: exact tier 0.6 / 1.5 / 2.1 / 0.6 s; with the near tier about 1 to 4.5 s per site.
  TF-IDF vectors took 2.5 / 9.7 / 13.3 / 2.0 s.
- Examples: the footer licence line and the curriculum check date on every page; the
  curriculum-facts block on 80 of 90 filosofia pages; the exam structure on 81 filosofia pages;
  "Lukiolaisella on oikeus oppimisen tukeen" on 37 of 44 opinto-ohjaus pages; the 112 referral on
  61 terveystieto pages; the self-assessment scale on 18 / 30 / 40 pages; and slot-filled task
  wrappers ("Helpompi polku: ...", "Aika: N min Tarvitset: ...") on 16 to 29 pages.

## Implementation notes (2026-11-22)

Code: `html_units.py`, `textsig.py`, `allowed_repeats.py`, `repeat_checks.py`, and `repeat_report.py` for the
command (split off to keep each file well under 500 lines). Where the code settles a point the plan left open:

- A digit run joins the letters around it, so `OP1.s1` is the two words `op<n> s<n>`, not four.
- Shingles are hashed with `zlib.crc32`; the one MinHash permutation is `(a*h + b) mod 2^61-1` with `a` and `b`
  taken from a fixed SHA-256 digest. Empty bins borrow from the next filled bin (rotation densification).
- "Stamped" (`stamped_share`) is a label on a cluster and a count in the summary. An allowed text is never an error
  for being stamped; with `fail_on_new` every new cluster is an error anyway.
- A near cluster is listed when its variants together reach the threshold and cover more topic groups than any one
  variant. Near clusters give no build problem; drift (a near variant of an allowed text) does.
- Stale entries are warnings, errors with `fail_on_new`. A broken allow-list entry (unknown or missing key, text that
  does not normalise to its hash, a hash listed twice) is always an error (kind `repeat-allow-list`) and allows
  nothing.
- The command takes `--site DIR` and `--fresh` besides `--json [FILE]` and `--suggest-allow`.
