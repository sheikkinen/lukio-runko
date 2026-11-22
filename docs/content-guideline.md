# Content guideline for the lukio sites

The shared rules for every site built by lukio-runko (lukion-opinto-ohjaus, lukion-terveystieto, lukion-filosofia,
lukion-psykologia and later ones) and for the visual novels adapted from them. A site's own `docs/content-contract.md`
extends this file and names the engine version it follows; the site adds only what is specific to its subject.
Changes go here, in a dated section at the end, and reach a site when it raises its engine pin.

Why this exists: in November 2026 a style rule invented in research ("henkilö, jolla on sairaus, ei sairastaja") was
taught to students as a Finnish norm. It came from English-language practice, had no source, and passed every check,
because the checks compared pages with the site's own style guide. The rules below make that kind of error visible.

## 1. Every teaching claim names its basis

A **teaching claim** is anything a page presents to the student as true, correct or required: a fact, a definition, a
rule of language or conduct, a criterion in a model answer, a "sanotaan…", "oikea tapa on…", "kuuluu…".

Each one rests on one of these, and a reader can find which:

| Basis | How it shows |
|---|---|
| a curriculum code from the topic's own list | the code in the front matter, and the claim inside what the code says |
| a matriculation exam requirement | a link to YTL's public page (format, scoring, grading description) |
| a cited source | a dated link to a page whose text states it, or a primary-text box |
| an operator decision | the decision id in the site's `decisions/INDEX.md` |

A claim with none of these is **removed**, or **labelled as the site's own framing** in the text: *sivuston oma
jäsennys* (for a classification or order the site chose), *sivuston esimerkki*, *sivuston lisäys* (content beyond the
curriculum). House style, meaning how the site writes, is never taught to students as a norm.

## 2. Value questions are weighing, not one right answer

Where the curriculum asks for analysis or evaluation (ethics, freedom and responsibility, political ideals, life
choices, contested science policy), tasks ask the student to weigh reasons, and model answers accept any well-argued
view. A model answer scores the quality of the reasoning, never the conclusion. Empirical questions keep their
evidence: weighing does not mean false balance on matters of fact.

## 3. Review checks claims against their basis

Checkers and judges verify each claim against the curriculum text, the exam rule or the cited source, and read the
Finnish for idiom. Matching the style guide, an earlier draft, another site or a previous checker's verdict is **not**
evidence. A style-guide rule is itself a claim: each row names its basis or is marked house style, and only the
operator turns house style into a rule that touches what students are told. Only the independent sources checker
records a source or translation as checked, and only for what it opened.

## 4. Watch list of English habits

These come easily to a model trained mostly on English, and are not Finnish norms. Checkers look for them:

- **Person-first etiquette as a rule** ("henkilö, jolla on…", "henkilö ensin"). Plain neutral Finnish is fine:
  *sairastaja*, *diabeetikko*, *riippuvainen*, *masentunut*. What stays out is demeaning labels and blame (*narkkari*,
  *nisti*, *juoppo*, *hullu*, *skitso*, *oma syy*, *syypää*). For drug use, prefer *huumeita käyttävä ihminen*, as the
  prevention organisation EHYT recommends ([Termit haltuun](https://ehyt.fi/wp-content/uploads/2024/03/ept-verkosto-termit-haltuun-huoneentaulu.pdf),
  read 22.11.2026). Person-first wording is allowed, not required.
- **Praise and filler** ("Hyvä kysymys!", "Mahtavaa!", "Muista, että…" stacked on every paragraph).
- **Graded verdicts on value questions** ("paras vastaus on…" where the curriculum asks for weighing).
- **Calques** of English phrasing (*ottaa paikkaa* for "take place", *tehdä järkeä*, *olla kiinnostunut sisään*), and
  English sentence rhythm in Finnish text.
- **US-style safety apparatus:** help or crisis blocks ("Apua ja tukea" with 112 and helplines) and content notes
  (trigger warnings). In Finnish practice they are rarely needed. No site carries them, except one help block in the
  single terveystieto chapter about mental health, never repeated elsewhere; a single mention of suicide on a page is
  not a reason for a block (operator, 2026-11-22).
- **Imported norms** presented as Finnish practice (US school conventions, US legal or health categories) without a
  Finnish source.

## 5. Ask early on language and norms

A rule about Finnish usage, etiquette or a social norm goes to the operator, a Finnish speaker, before it enters a
style guide. One question is cheaper than a review round.

## 6. Traceability in practice

- A topic's front matter lists its curriculum codes, sources (`official_links` with read dates), primary texts and
  findings; that is the basis index for its claims.
- A norm sentence in student text ("sanotaan…", "kuuluu…", "on oikein…") carries its basis in the same paragraph.
- Model answers name the criterion they score and where it comes from (the task, a code, the exam's grading areas).
- The visual novels adapted from the sites keep the same basis for every line they teach, and do not add rules the
  site does not state.

## Changes

- 2026-11-22: first version (lukio-runko v0.4.0), after the person-first case (lukion-terveystieto D-012). The operator
  approved the four points relayed from the game-engine review ("proceed as proposed") and the audit ("Guideline and
  audit").
- 2026-11-22: the watch list names US-style safety blocks and content notes; one help block only, in the terveystieto
  mental-health chapter ("remove the unrelated safety block - it is US cultural thing"; "remove the content notes
  too… otherwise never repeat").
