# lukio-runko

The shared engine that builds a free, static website for one subject of the Finnish general upper secondary school
(lukio), following the national core curriculum (Lukion opetussuunnitelman perusteet 2019). Each subject has its own
repository and its own GitHub Pages site; this engine builds them all. The first site built with it is
[Lukion opinto-ohjaus](https://sheikkinen.github.io/lukion-opinto-ohjaus/).

Every topic of a subject works two ways: as a stand-alone lesson a teacher can teach, and as a step in a self-study
path a student follows alone. The site needs no JavaScript to read, keeps a student's progress only in their own
browser, and loads nothing from other hosts.

## Install

```bash
python -m pip install "lukio-runko @ git+https://github.com/sheikkinen/lukio-runko@v0.5.0"
```

A subject site pins a tag in its `requirements.txt`. For work on the engine itself, clone it and install it
editable: `python -m pip install --user -e <path to the clone>[dev]`.

## Use

Run the commands in the subject site's folder (the one that holds `subject.yaml`), or pass `--root`:

```bash
lukio-runko build                  # writes _site/ and runs every check; exits 1 on any error
lukio-runko build --partial        # while writing: coverage and missing facts are warnings
lukio-runko fetch-curriculum       # reads ePerusteet into data/curriculum.yaml
lukio-runko images --dry-run       # plans the pictures in data/images*.yaml
lukio-runko repeats                # reports text that repeats across the built pages (read-only)
lukio-runko compare GOLDEN BUILT   # compares two built sites byte for byte
```

`lukio-runko <command> --help` lists each command's options. `python -m lukio_runko` works the same way.

The build reads the date for its link-age check from `<SHORT>_TODAY` (for example `LOO_TODAY=2026-11-21`), where
`<SHORT>` is the site's `short_name` in capitals, so a build can be repeated exactly.

`lukio-runko images` uses the image modules of a separate game-engine checkout. Set `GAME_ENGINE_DIR` to that folder;
the command stops if it is not set. Paid calls are capped by `--max-dollars`, and the plan is printed first.

## A subject site

```
subject.yaml              everything subject-specific (see below)
content/topics/*.md       the topics, written to the content contract
content/pages/*.md        etusivu, opetussuunnitelma, lahteet, polku, tietosuoja, saavutettavuus
data/curriculum.yaml      written by lukio-runko fetch-curriculum
data/yearly-facts.yaml    facts that change yearly, each with its source and read date
data/images*.yaml         optional: the picture manifest
site-src/                 optional: the site's own pictures (site-src/img/) and any file that replaces an
                          engine asset of the same path (for example site-src/css/site.css)
templates/base.html       optional: replaces the engine's page template
```

The engine's stylesheets and script are copied to `_site/assets/` first and the site's `site-src/` is copied over
them. `@SITE_NAME@` and `@STORAGE_KEY@` in any copied `.js` or `.css` file are filled in from `subject.yaml`.

`subject.yaml` names:

- `site`: the name, the short name (the prefix of the environment variables), the base address, the one
  localStorage key, and the footer licence line;
- `teacher`: how the lesson views name the teacher, and the teacher's column in the lesson plan tables;
- `curriculum`: the ePerusteet ids of the core curriculum, the subject and its modules, the subject code, the module
  routes, and the number of objectives and contents each module must have;
- `topics.max_order` and `assessment`: `sh` (pass or fail, no grade) or `numeric` (a grade 4 to 10);
- `contract`: the topic sections in order and which view shows each. `numeric` adds `## Koetehtävät` (exam tasks,
  each `###` heading stating its points, for example `(6 p)`) and `## Mallivastaukset` (one model answer per task,
  with the same heading, in the same order). The build checks both.

`tests/fixtures/site/subject.yaml` is a complete example (the opinto-ohjaus subject).

Optional in v0.2.0:
- a topic's front matter may list `card_links: [{label, url}]`: extra links shown on the topic's card beside
  "Opiskelijan näkymä" and "Tuntisuunnitelma". Each url must be https and listed in `official_links`;
- a picture entry may carry a `commons` block (`credit`, `work` and its source record) for a public-domain artwork;
  the credit and the work are shown as the figure caption.

New in v0.4.0: `docs/content-guideline.md`, the shared content rules every site's contract extends (every teaching
claim names its basis; value questions as weighing; review against the basis; a watch list of English habits).

New in v0.3.0: the picture manifest is read from `data/images.yaml`, then `data/images-illustrations.yaml`, then any
other `data/images-*.yaml` in name order, so a site adds a file when one reaches the 500-line limit.

## Repeat check

Every build also looks for sentences and paragraphs that repeat across the site's pages: template boilerplate,
warnings and reassurances stamped on every topic. It reads the built HTML (print pages under `tulosta/` left out),
counts a topic's student and lesson page as one topic, and compares normalised text by SHA-256 (exact) and by MinHash
confirmed with exact Jaccard (near-exact). It uses no meaning, no keyword list and no randomness, so the same site
always gives the same result. The build prints one `repeats:` summary line, warns once per repeated text found in 10%
of the topics (at least 3), and writes the full report to `repeats.json` beside the output folder (for the default
build, `<root>/repeats.json`). The method and its numbers are in `docs/repeat-check-plan.md`.

- Intended repeats go in `data/allowed-repeats.yaml`, one entry per exact text: `hash`, `text` (must normalise to the
  hash and have at least `min_words` words), `reason` and `max_groups`. A reworded copy (drift), growth past
  `max_groups` (also below the report threshold) and an entry that matches nothing (stale) are reported.
- `subject.yaml` may set `repeats:` with `min_share`, `min_groups`, `stamped_share`, `near_jaccard`, `min_words`,
  `near_min_words` and `fail_on_new`. With `fail_on_new: true` the warnings become errors and fail the build;
  `--partial` turns them back into warnings.
- `lukio-runko repeats` reads `<root>/_site` (or `--site DIR`), or builds a temporary copy when there is none or with
  `--fresh`; it never changes the site. `--json FILE` writes the report, `--json` alone prints it, and
  `--suggest-allow` prints the new repeats as allow-list entries with an empty reason, for a person to fill in or
  reject.

## Workflow templates

`workflows/` holds the multi-agent workflow scripts used to make the opinto-ohjaus site (research, build, content
fixes, pictures). They take the project folder as an argument and name opinto-ohjaus files and checks, so copy one
into a subject's `.claude/workflows/` and adapt it to that subject's brief. `docs/templates/` has the brief and diary
templates.

## Development

```bash
python -m pip install --user -e .[dev]
python -m pytest
ruff check .
```

The tests are fast and use no network. No file is over 500 lines.

## Licence

CC BY 4.0, see [LICENSE](LICENSE). The curriculum texts the engine fetches belong to the Finnish National Agency for
Education (Opetushallitus, ePerusteet) and are not covered by this licence.
