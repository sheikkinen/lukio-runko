# Feedback loops: plan (2026-11-24)

## Goal

Give the lukio generation process feedback that does not depend on the operator's verdict: checks whose ground truth is the site page, a lexicon, a corpus, YTL's released exams, planted defects or content hashes. The research behind each check (sources, licences, evidence, limits) is in `docs/research/2026-11-24-feedback-loops.md`; the pilot that prompted it is in `docs/research/2026-11-24-vn-review-pilot/`. Operator, 2026-11-24: "you rely too much on me as the ground truth"; "Yes, do it" (store the research and plan here).

Checks 2, 6 and 9 touch the visual novels as well; their novel-side part goes to game-engine as a producer brief that links here. Downloads (checks 3 and 4) need the operator's yes.

## Per check

## 2. Novel ⊆ page: every name, number and service in a chapter is on its page

**Build.** One module in `tools/lukio/` beside `repeat_check.py`, with tests; the ship step fails on a new entity
not on the page and not confessed. Inflected names need check 3: Voikko cannot analyse a name it does not know
("Setan"), so the registry lists each name with an inflection model word and omorfi or a small table generates its
case forms (research: no tool reliably knows such names).

**First pilot.** Run it on the nine pilot chapters and compare its hits with the 28 must-change list: how many of
the help-line and added-service items does it find, with how many false alarms.


## 3. Finnish morphology: non-words and broken forms

**First pilot.** Run both on all nine novels and four sites; count and read the flags; size the registry needed.
Needs the operator's yes for the downloads (DLL, dictionary, models).


## 4. Calque candidates from corpus frequency

**Build.** One preprocessing step into a local SQLite table (never shipped); the check parses our text with a
dependency parser, looks up each pair, and lists pairs below a native-frequency threshold with a high
subtitles-to-newspaper ratio. Seed tests from known calques in Kielitoimiston ohjepankki ("tehdä järkeä", "ottaa
paikkaa").

## 5. Released matriculation exams as an external standard of sufficiency

**First pilot.** Three sessions of filosofia and terveystieto HVP (2024–2026), whole-course material, binary
scoring; read the raw answers before any totals.


## 6. Planted defects: measure every checker's recall

**Build.** A test fixture in `tools/lukio/tests` (game-engine) and `tests/` (lukio-runko): a mutator that applies one
defect at a known line, and a report of recall per defect type and false alarms per control, for each check
(2, 3, 4, the repeat check, trace_check, the outsider, a model reviewer). Deterministic checks become ordinary unit
tests; model reviewers get a recall figure per run, recorded with the model and prompt version.

**First pilot.** The 14 defect types × the nine pilot chapters, run through the Haiku explicit reviewer and the
deterministic checks; this alone answers "is Haiku enough" with a number.


## 9. Stale copies and changed sources

**Build.**
- (a) The site build already has every topic's main text; write a manifest of topic id → hash. The novel's trace
  records the hash of the page it was written from; the ship step compares and lists changed chapters with a diff
  of the page sections that changed. Cross-repository: read the manifest from the local site checkout.
- (b) Each `official_links` entry gets a cached copy and hash of the text it was read from. A periodic job (not the
  build: the sites make no external requests, and the build should not either) refetches, compares, and lists pages
  whose sources changed. A change means "re-read this source", not "the page is wrong".

## Order

1. **6 first, in a small form**: the defect catalogue and the mutator. Every other check needs it to report a recall
   figure instead of a feeling.
2. **2 and 3**: deterministic, cheap, and between them they cover the added services, repeated numbers and typos the
   pilot found. 3 needs downloads.
3. **9**: small code, prevents silent drift between the sites and the novels.
4. **5**: the only external measure of whether the material is enough; a periodic evaluation, not a gate.
5. **7**: once 6 exists, tune the model review with it.
6. **4**: largest data, least certain precision; last, and advisory.

What still needs the operator: whether a norm applies where no source settles it (the ledger's custom and house-style
rows), and taste. None of the seven checks above needs a verdict from the operator to produce its result.

## Implementation notes

- 2026-11-24, check 4 pilot with SemFi (`docs/research/2026-11-24-calque-pilot.md`): planted calques separate from
  native phrases where scorable, but parser mismatch with the reference makes the lists noisy; repetition ("Aivan.",
  "Oikein.") is the clearest signal.
- 2026-11-25, check 4 second pilot with a same-parser Projekti Lönnrot reference
  (`docs/research/2026-11-25-same-parser-pilot.md`): no calque detection at 2 million words; modern text shows about
  2 points more rare pairs than old native text, cause open (era, register or English influence). Recommendation:
  keep keyness as a repetition check, put the effort into check 6, seeded with 53 documented calques
  (`lukio-data/pilot2/documented.json`).
- 2026-11-25, check 6 first pilot (`docs/research/2026-11-25-planted-defects-pilot.md`): 14 defect types and 3
  controls planted in the nine pilot chapters. The explicit reviewer names about three quarters (Haiku 77%, Sonnet
  82%), always the inserted apparatus, seldom calques; trace_check catches wrong codes and unbased graded choices,
  repeat_check nothing in one chapter. Next: deterministic checks for help lines, 112, content notes and praise;
  checks 2 and 3 for services, numbers and misspellings; plant in context and repeat runs.
