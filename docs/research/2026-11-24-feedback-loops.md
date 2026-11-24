# Feedback loops for lukio generation that do not rely on the operator: research

Date 2026-11-24. Seven checks, each with a ground truth other than a person's verdict. The operator remains the
basis only for values, norms and taste where no outside source exists (operator: "you rely too much on me as the
ground truth"). Feasibility facts come from a research run with a skeptic pass over the key claims; anything not
confirmed is marked. Nothing here has been installed, downloaded or run.

The parallel is yamlgraph's chain: failure → recorded → rule → **code check with an exceptions registry**
(`docs/confessions.md`), and its `two_strike_split`: when the same failure returns after a prompt fix, the check
belongs in code. The lukio help lines did exactly that (brief 530, then the pilot found variants).

| # | Check | Ground truth | Kind | Runs in |
|---|---|---|---|---|
| 2 | Novel ⊆ page: names, numbers, services | the site page and its sources | deterministic | game-engine ship step |
| 3 | Finnish morphology | Voikko and omorfi lexicons | deterministic | both builds |
| 4 | Calque candidates | Finnish corpus frequencies | statistical, advisory | both, periodic |
| 5 | Material vs released exams | YTL tasks and "hyvän vastauksen piirteet" | model-assisted, external standard | periodic evaluation |
| 6 | Planted defects | defects we insert ourselves | deterministic ground truth for any checker | tests |
| 7 | Agreement across runs and models | repetition (noise filter, not truth) | model, measured by 6 | review step |
| 9 | Stale copies and changed sources | content hashes | deterministic | both builds |

The plan (how each check is built, first pilots, order) is in `docs/feedback-loops-plan.md`.

---

## 2. Novel ⊆ page: every name, number and service in a chapter is on its page

**What it checks.** A chapter may shorten its page but not add facts. Extract from the chapter's player-visible text
(the extractor in `tools/lukio/outsider.py` already does this): proper nouns that are not sentence-initial,
organisation and service names, numbers with what they count (weeks, %, €, years, §), law references, phone numbers,
URLs. Lemmatise them (check 3) and require each to appear in the page's main text, its `official_links` titles or
publishers, or the chapter's `trace.yaml` code texts. Exceptions registry: the book's character and place names
(from `book.yaml`), generic words, and confessed exceptions with a reason (like yamlgraph's CONF entries).

**Ground truth.** The page. No judgement is involved: either "Seta" is on the page or it is not.

**What it would have caught in the pilot.** Sekasin and Kriisipuhelin in OP1 ch04, Nettiturvakoti in TE2 ch07,
Väestöliitto and Seta in TE3 ch08, Ohjaamo in OP2 and FI4, 112 repeated in TE1 ch08 (a number that is on the page
once; count occurrences too). Page-only entities are reported as information, not failures: leaving out is allowed.

**What it cannot catch.** Claims built from words that are all on the page: "suostumuksen voi peruuttaa milloin
tahansa" (TE3), a value question graded "Oikein.", a rule like "HOPSiin ei kirjata terveystietoja". Those need a
claim-level comparison, which is a model step (see 6 and 7 for how to measure one).

**Extension.** The same comparison one level up: page ⊆ cited source, for numbers and law references, against a cached
copy of each source (check 9 keeps the cache honest).

## 3. Finnish morphology: non-words and broken forms

**What it checks.** Every token of site and novel text against a Finnish morphological lexicon; tokens no analyser
accepts are errors ("velvollisuusetiikot", "Ryhmanohjaaja" from the pilot). Voikko's `grammarErrors()` adds some
agreement checks.

**Ground truth.** The lexicon and morphology of two independent finite-state analysers.

**Feasibility (researched, not tested).**
- **Voikko**: `pip install libvoikko` (pure-Python wheel, works with 3.13) plus the native 64-bit
  `libvoikko-1.dll` 4.3 (2019 build, published by the project) and a dictionary from the 2024-06-18 snapshot; load
  with `Voikko('fi', path=...)` so it stays portable. Dictionary variants exist for education (`dict-kasvatus`) and
  medicine (`dict-laaketiede`), which suit terveystieto and opinto-ohjaus. Lemma (`BASEFORM`) may need the
  `dict-morpho` variant: unconfirmed.
- **omorfi**: `pip install omorfi` (pulls `pyhfst`, which has a Windows cp313 wheel) plus the 0.9.12 model archive
  (about 26 MB, one download).
- **Licences**: Voikko dictionary GPL v2 (or later: not re-checked), omorfi GPLv3. Run as build tools only; their
  output is not GPL-covered (GNU GPL FAQ); never bundle them into the CC BY sites. Not legal advice.
- spaCy, Stanza and Trankit lemmatise with 83–86% accuracy (spaCy's own figures) and always output a lemma, even for
  a misspelt word: too noisy for a gate.

**Rule.** Fail when both Voikko and omorfi reject a token that is not in the project registry; warn when only one
does. Two independent lexicons cut the false alarms from lexicon gaps without anyone deciding each case.

**What it cannot catch.** Real words used wrongly, calques made of valid words, misspelt compounds whose parts are
valid words.

## 4. Calque candidates from corpus frequency

**What it checks.** Phrases rare in native Finnish but common in English-influenced Finnish: a verb–object or
adjective–noun pair whose lemmas are each common but whose combination is rare in native text, and relatively more
common in translated text.

**Ground truth.** Frequencies in large Finnish corpora. Rarity alone is not a calque, so a contrast corpus is the
second signal.

**Data (researched; licences as stated on primary pages).**
- **SemFi** (CC BY-SA 4.0 on Zenodo; other catalogues disagree): lemma+POS dependency pairs with frequencies from
  the Finnish Internet Parsebank, 3.8 GB. Catches "tehdä + dobj järki" even when not adjacent. Schema unconfirmed.
- **FNC1** n-grams from the National Library newspaper corpus 1820–2000 (CC BY, version unstated; word forms, OCR
  noise, 6.5 GB + 18 GB): a native baseline from before English influence.
- **OpenSubtitles fi 2017** (Kielipankki, CC BY 4.0): largely translated from English, so its frequency relative to
  newspapers is a translationese signal. Lemma column unconfirmed.
- Not usable: Suomi24 (academic login, no redistribution), the Kotus Parole list (licence unclear), the newspaper
  frequency lexicon (NC-ND). The Korp API is online only; at most a one-time cache.

**What it cannot catch, and the honest limit.** It produces candidates, not verdicts: rare can be fine, and web
text contains calques too. Its precision is unknown until check 6 measures it with planted calques. Advisory, never
a gate. Data is several gigabytes; downloads need the operator's yes.


## 5. Released matriculation exams as an external standard of sufficiency

**What it checks.** Whether the material is enough to answer real exam tasks: a model answers each released task
with only our material in context, and the answer is scored against YTL's own description of a good answer.
Points the material cannot support show gaps, task by task.

**Ground truth.** YTL's tasks and "hyvän vastauksen piirteet" (HVP): an external, official standard.

**Feasibility (researched).**
- HVP pages for terveystieto, filosofia and psykologia exist per session from spring 2013 to autumn 2026: PDF up to
  2021, HTML from autumn 2021 on tiedostot.ylioppilastutkinto.fi, with task wording, points per subtask and scoring
  descriptions. Use LOPS 2019 exams only (from 2022; the new reaaliaine rules apply from autumn 2025: 9 tasks, at
  most 5 answered, 120 points). Opinto-ohjaus has no exam, so this does not cover it.
- **Rights.** YTL's publishing page, citing Copyright Council statement 2020:4: YTL is an authority under Copyright
  Act section 9(1)(4) and its exam tasks are statements without copyright; under section 25 d(4) exams may be
  reproduced. Third-party attachment material is not covered (rights holders' permission needed), so keep
  attachments out and keep everything in a local evaluation folder, never republished. The statement is advisory,
  not a ruling. Exam attachments returned HTTP 403 to automated fetches.
- No per-task score statistics are public.

**Method, keeping the model's opinion out of the score.**
1. For each task, give the answering model only the topics whose curriculum codes match the task (or the whole
   course), and require every point in its answer to cite a material line.
2. Score each HVP point as present or absent: present only if the answer states it **and** cites a material line
   that supports it. A point stated without a citation counts as model knowledge, not our material.
3. Report per task: HVP points supported by our material, points missing, and which topic should carry them.

The grading step is still a model, but each decision is binary and comes with a quote, so it can be checked
mechanically (the quote exists, the cited line exists) and measured with check 6.

**What it cannot show.** Whether the material teaches well; points the HVP does not list; the difficulty of tasks.

## 6. Planted defects: measure every checker's recall

**What it checks.** Not the content but the checks. Insert known defects into copies of pages and chapters by
script, run every check, and count what each catches; insert meaning-preserving edits too and count false alarms.

**Ground truth.** The defects we inserted. This is what makes model reviewers measurable without a human verdict.

**Defect catalogue, copied from failures actually seen** (synthetic defects that do not resemble real ones are the
method's known weakness): a help or crisis line; 112 outside its allowed places; a content note; a praise formula;
a repeated reassurance; "Oikein." on a value question; a changed number (week 12 → 14); a changed law condition
("ennen keräämistä" → "milloin tahansa"); an added service name; a calque; a misspelling; a wrong curriculum code;
a dropped "sivuston oma jäsennys"; an added rule ("HOPSiin ei kirjata…"). Controls: synonym swaps, reordered
sentences, a reworded line that keeps its meaning.

**Evidence.** FBI (EMNLP 2024): five LLM evaluators missed over half of 2,400 planted quality drops; giving the
checker a reference gave the largest gain. FLAWS (2026): the best model found 39% of inserted errors at k=10.
Benchmarking Agentic Review Systems (2026): best configuration 71.6% of injected errors, the union of six models
83.3%. All on English, non-curriculum tasks.

## 7. Agreement across runs and models: a noise filter, measured by 6

**What it checks.** Whether a model finding is stable: the same reviewer run 3–5 times, and a second model family;
findings matched by scene line and defect category.

**Ground truth.** None by itself, and the research is clear on that: models share blind spots (Kim et al., ICML
2025: correlated errors across over 350 models; Kohli 2026: a panel of nine judges carried about two independent
votes, and the best single judge matched the panel). Agreement is not correctness.

**How to use it anyway.**
- For coverage, take the union across runs and models (the 83.3% vs 71.6% result).
- For ranking, use the recurrence count: a finding in five of five runs comes first, a one-run finding last.
- Never treat "all runs found nothing" as a pass.
- Decide the thresholds with check 6, not by taste: plant defects, run k times, and see what union and
  recurrence do to recall and false alarms.


## 9. Stale copies and changed sources

**What it checks.** (a) A novel chapter written from a page that has since changed. (b) A site page whose cited
source has changed since its read date (a law amendment, a renamed service).

**Ground truth.** SHA-256 hashes of normalised text: equality, not inference (yamlgraph's seed
`artifact_carries_code_identity`).

**What it cannot catch.** Whether a change matters; that still needs reading, but now someone knows where to look.
