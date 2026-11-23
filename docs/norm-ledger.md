# Norm ledger: Finnish practice versus a model's defaults

Part of the shared content guideline (`docs/content-guideline.md`). It is the **context** every brief starts from and
the **ground** every checker tests against (operator, 2026-11-22: "this is context and grounding").

## How to read it

The shared values are the same in Finland and elsewhere: dignity, no harm, privacy, honesty, care for the student.
What differs is the **custom** that expresses them. A model trained mostly on English writes US and English customs
by default and takes them for neutral; this ledger names each default so it can be seen as a choice.

Each row is **descriptive**: what Finnish practice is, with its basis. It is not a list of commands, so that a writer
can reason about cases the ledger does not cover. The **level** says what kind of norm it is and how fixed it is:

- **law** — set by a statute; fixed.
- **moral principle** — the shared value; fixed.
- **institutional rule** — set by an authority such as OPH, YTL or a professional body; fixed for that domain.
- **organisational recommendation** — advice from an expert organisation; followed unless there is a reason.
- **custom** — how things are usually done in Finland; followed, and open to the operator's judgement.
- **house style** — the sites' own choice; never taught to students as a norm.

A row is added or changed only with a basis: a source a person opened, or an operator decision. A model's opinion is
not a basis. When a writer meets a norm question the ledger does not cover, they ask the operator (guideline §5).

## The ledger

| # | Situation | A model's default | Finnish practice | Level | Basis | What the sites do |
|---|---|---|---|---|---|---|
| 1 | Naming a person with an illness | Person-first etiquette as a rule: *henkilö, jolla on sairaus*, never *sairastaja* | Plain words are neutral: *sairastaja*, *diabeetikko*, *sairastunut*. Dignity shows in avoiding labels that reduce a person to the condition and in not blaming | custom | Operator, 2026-11-22: "sairastaja is not used in finnish language as a stigma" (terveystieto D-012) | Write plain Finnish; no rule about word order. *Väärin:* "Sanotaan henkilö, jolla on sairaus, ei sairastaja." *Oikein:* "Riskitekijä ei ole syy, eikä sairastunutta syyllistetä." |
| 2 | Naming people who use drugs | *Addict*, *drug user*, or the English *person who uses drugs* translated word for word | *Huumeita käyttävä ihminen*; avoid *narkkari*, *nisti*, *huumeidenkäyttäjä*, *huumeriippuvainen* | organisational recommendation | EHYT / ept-verkosto, [Termit haltuun](https://ehyt.fi/wp-content/uploads/2024/03/ept-verkosto-termit-haltuun-huoneentaulu.pdf), read 22.11.2026 | Use *huumeita käyttävä ihminen* about drugs; *riippuvuus* and *riippuvainen* are fine about dependence in general |
| 3 | A page that mentions death, suicide, violence or illness | A help block with 112, crisis lines and youth helplines on every such page | Rarely needed; a single mention of suicide is not a reason for a block. Support for students is the school's own service, not a footer | custom | Operator, 2026-11-22: "remove the unrelated safety block - it is US cultural thing … in finnish culture the block is needed rarely" and "only single instance … otherwise never repeat" | No help block, 112 line or helpline anywhere, except one block in the single terveystieto chapter about mental health |
| 4 | A page with a hard subject | A content note (trigger warning) at the top | Not used | custom | Operator, 2026-11-22: "remove the content notes too" | No content notes |
| 5 | Reassurance and disclaimers | The same reassurance on every page: *you don't have to share*, *this is not advice*, *the scoring is unofficial* | Said once, plainly, where it matters | house style (operator 2026-11-23: "Remove repeats") | Operator's notes, 2026-11-22: repeated warnings and disclaimers; the deterministic repeat check (`docs/repeat-check-plan.md`); operator 2026-11-23: "Remove repeats" | A site-wide fact is stated once on a site page; topic pages do not repeat it |
| 6 | A value question in a task or model answer | One right answer, a graded verdict (*paras vastaus on…*) | Weighing reasons; any well-argued view is accepted | institutional rule | The curriculum asks for analysis and evaluation in such content (for example FI2, TE3.s8); guideline §2, approved by the operator ("proceed as proposed") | Tasks ask to weigh; model answers score reasoning, not the conclusion; empirical questions keep their evidence |
| 7 | Feedback to the student | Praise and filler: *Hyvä kysymys!*, *Mahtavaa!*, *Muista, että…* on every paragraph | Plain, matter-of-fact tone | custom | Guideline §4, approved by the operator ("proceed as proposed") | No praise formulas; a reminder only where it carries information |
| 8 | Sentence-level phrasing | Calques of English (*ottaa paikkaa*, *tehdä järkeä*) and English sentence rhythm | Idiomatic Finnish | custom | Guideline §4; the operator reads for idiom | Checkers read the Finnish for idiom, not only for errors |
| 9 | Legal, health and school categories | US categories and institutions presented as general (US school roles, US legal or diagnostic terms) | Finnish institutions and terms (opiskeluhuolto, opiskeluterveydenhuolto, kuraattori, ylioppilastutkinto) with Finnish sources | institutional rule | Guideline §4 and §1 (every claim names its basis) | Name the Finnish institution and cite a Finnish source |
| 10 | A rule in a style guide | A rule a model proposed becomes a rule because an earlier workflow wrote it | A rule needs a basis; otherwise it is house style and is not taught | house style | Guideline §1 and §3; the person-first case (terveystieto D-012) | Every style-guide row names its basis or is marked house style |

## Changes

- 2026-11-22: first version, rows 1–10, from the person-first case, the help-block and content-note decisions, the
  repeated-disclaimer finding and the guideline's watch list (operator: "Yes, add the ledger").
- 2026-11-23: row 5 decided (operator: "Remove repeats"); lukio-runko v0.5.1 drops the two per-topic notes the
  engine stamped (yearly facts and the self-study mark) and the *(esimerkki, koulu päättää)* stamp after
  each topic's timing, and the sites remove their repeated notes.
