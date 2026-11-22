# Repeat check: judgement (2026-11-22)

Judge of the work against `docs/repeat-check-plan.md`. The judge wrote no code and changed no file except this one.

## Verdict: accept-with-minors

The check does what the plan asks. It is deterministic, uses only the standard library plus PyYAML (already a
dependency) for the allow-list, and is tested with tmp_path fixture sites. Both items the fix round took on (growth below the threshold, and
allow-list entries shorter than min_words) are fixed and have tests. Nothing has to change before merge. The minors
below can go in a follow-up.

## Review results

| Check | Result | Must fix | Ruling |
|---|---|---|---|
| correctness | passed | none | Agreed. Grouping, thresholds, `ceil(round(...))`, hash-only matching and sentence hiding all match the plan. |
| readability | passed | none | Agreed. Long dense lines are a minor (see below), not a blocker. |
| fidelity | passed | none | Agreed. Every deviation is written in the plan's Implementation notes. |
| fidelity minor: growth below the threshold | fixed | - | `grown_allowed_units` and `reported_units` (repeat_checks.py 173-192), with tests at test_repeat_checks.py 159 and 169. |
| fidelity minor: entry shorter than min_words | fixed | - | `_text_problems` (allowed_repeats.py 53-65), with a test at line 176. Plan and README updated. |
| "stamped" is a label, not an error rule | accepted | - | Under `fail_on_new` every new cluster is already an error, so only allowed texts escape. Recorded in the notes. |
| stale is a warning (plan's Tests section says error) | accepted | - | The Implementation notes settle it: a warning, an error under `fail_on_new`. The Tests line is now out of date. |

Judge's own checks:
- `python -m pytest -q` passes 180 tests, also with `PYTHONHASHSEED=7`.
- `ruff check src tests` is clean.
- The largest file is checks.py at 412 lines; the largest new file is repeat_checks.py at 381.
- Grep finds no `hash()` and no `random`.
- The global Python 3.13 here has no `Markdown` package, so the tests ran in a scratch venv with only the declared
  dependencies and `PYTHONPATH=src`.

## Baseline per site

Command: `python -m lukio_runko repeats --root <site> --fresh`, with default settings and no allow-list, so every
cluster is new.
- Each site was run twice, with `PYTHONHASHSEED` 1 and 99. JSON and text output were byte-identical both times.
- No report holds an absolute path.
- `git status` on every site was the same before and after.

| Site | Pages | Topics | Units | Clusters | Stamped | Near | Time |
|---|---|---|---|---|---|---|---|
| lukion-opinto-ohjaus | 44 | 26 | 4,981 | 245 | 48 | 36 | 4 s |
| lukion-terveystieto | 69 | 39 | 12,198 | 204 | 51 | 58 | 10 s |
| lukion-filosofia | 90 | 50 | 14,216 | 205 | 61 | 62 | 13 s |
| lukion-psykologia | 29 | 18 | 4,027 | 170 | 60 | 44 | 3 s |

Top three stamped units per site (topics/pages):
- opinto-ohjaus: curriculum check date line (26/44); CC BY licence footer (26/44); "Lukiolaisella on oikeus oppimisen tukeen..." (19/37).
- terveystieto: curriculum check date line (39/69); licence footer (39/69); "Pisteytys on sivuston oma harjoitusohje..." (31/31).
- filosofia: licence footer (50/90); curriculum check date line (50/90); "Filosofian vastauksen arvioinnissa painavimmat kohdat..." (41/81).
- psykologia: curriculum check date line (18/29); licence footer (18/29); "Syksystä 2026 alkaen osassa 1 on yksi..." (12/23).

The counts match the implementer's table. The times differ by a second or two, which is build noise.

## Remaining items (minor, none blocking)

1. Readability. Split the dense lines into named steps:
   - repeat_checks.py lines 197, 297, 303, 310 and 326-330;
   - the `data = normalised` alias in textsig.py line 139;
   - add a one-line comment on the `".."` test in textsig.py line 88.
2. `repeats.json` is written to `<root>/` by a default build, and no site's .gitignore lists it. Add it to each site
   when that site rolls out.
3. The plan says site CI uploads `repeats.json`, but no site workflow does yet.
4. Drift needs an allowed text of `near_min_words` (8) words or more, so a reworded short allowed label is silent.
5. `candidate_pairs` is quadratic inside one LSH bucket. It is fine at today's sizes; note it, or cap it, if sites grow.
6. Plan wording to bring up to date:
   - the Tests section's "stale ... errors";
   - `--suggest-allow` lists only new clusters;
   - the removal of soft hyphens and zero-width marks (`INVISIBLE`) is not in the normalisation order.
7. The dated section on declaring a repeat in docs/content-guideline.md is due after rollout, as the plan says.

## For the operator

- Accept: the repeat check works, is tested, gives the same bytes on every run, and changes no site.
- Each site starts with about 170-245 new clusters; the licence footer and the curriculum date line are on every page.
- Before a site turns on `fail_on_new`, add `repeats.json` to its .gitignore and write its allow-list.
- The minors are readability and plan wording; do them in one small follow-up, nothing is urgent.
