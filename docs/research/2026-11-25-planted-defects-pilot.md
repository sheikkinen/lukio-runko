# Check 6, first pilot: planted defects measure the checkers

Date 2026-11-25. The first pilot of check 6 in `docs/feedback-loops-plan.md`: plant known defects in copies of the
nine chapters of the 2026-11-24 review pilot, run the deterministic checks and a model reviewer on them, and count what
each catches. The ground truth is the defect we planted, so no human verdict is needed to get a recall figure.
Operator: "Check 6 pilot". Code and data: the private `lukio-data` repository, folder `check6/`.

**Result in one line:** with the page as reference, the explicit-criteria reviewer names about three quarters of the
planted defects: Haiku 77%, Sonnet 82% (strict to lenient: 74–81% and 78–88%). Both catch inserted help lines, 112,
content notes, added rules and repeated reassurance every time; both are weak on calques (Haiku 1 of 9, Sonnet 4 of 9),
a single misspelt letter and a graded open question (about two in three). The deterministic checks catch only what
they were built for: wrong curriculum codes and an unbased graded choice. Planted defects are more conspicuous than
real ones, so these figures are upper bounds.

**Review.** A verification round (two lenses, each finding put to a refuter; 12 findings, none refuted) changed this
pilot before the figures were final. The comment matcher read only the quote, so comments that named a defect in their
text while quoting another line were missed (Sonnet bundles several points per comment, so it lost most); the judges'
agreement was overstated (yes-against-no splits only); four changed-condition plants contradicted nothing on the page
(two were re-planted where the page has the hedge, two dropped for want of such a spot); some controls were not neutral (sentence swaps that moved a pronoun ahead of its referent, "myös → lisäksi",
"heti vaarassa → saman tien vaarassa"). The planting, matcher and analysis were fixed; of 21 changed variants, 15 were
reviewed again under new ids and 6 dropped out; every match was judged again. The figures below are after the fixes.

## What was planted

Defect types copied from failures seen in the lukio novels (the catalogue in
`docs/research/2026-11-24-feedback-loops.md` section 6), each applied alone to a copy of one chapter at a seeded
position (`check6/mutate.py`):

| Defect | How it was planted | Variants |
|---|---|---|
| help line | teacher line with Kriisipuhelin number and Sekasin-chat (not in TE1 ch08, where one help block belongs) | 8 |
| 112 | teacher line "Jos tilanne tuntuu vaaralliselta, soita heti 112." (not in TE1 ch08) | 8 |
| content note | "Sisältövaroitus: …" at the start | 9 |
| praise | "Hyvä kysymys!" in front of the teacher's answer to a student's question | 9 |
| repeated reassurance | "Muista, että et ole tässä yksin." three times | 9 |
| graded value question | "Oikein." in front of one option's feedback in a menu where no option is graded | 9 |
| changed condition | a hedge changed to "aina" (the final plants replaced "usein" or "joskus"; the code also accepts "yleensä", "tavallisesti", "useimmiten"), only where the page has the same hedge next to the same word | 7 |
| added service | a line naming Ohjaamo, Väestöliitto or Seta, whichever the page and chapter do not mention | 9 |
| calque | the line "Isossa kuvassa tämä on aika selvä asia." (Kielikello lists *isossa kuvassa* as a calque) | 9 |
| misspelling | one "ä" typed as "a" in a long word | 9 |
| wrong code | a curriculum code in a `# peruste:` comment replaced by one the trace does not list (not player-visible) | 9 |
| added rule | "Lukiolain mukaan tämä pitää hoitaa ennen toisen jakson loppua." | 9 |
| changed number | a number stated on the page changed (only FI4 has a number with its noun on the page: 1896 → 1899) | 1 |
| dropped own framing | "sivuston oma …" removed (only TE3 carries the mark) | 1 |

Controls: a synonym swap (ehkä → kenties; heti → saman tien only where punctuation follows "heti"; 5), two
sentences of one line swapped where neither opens with, and the moved one does not contain, a word that ties it to
the other (9), a rewording (Sitten → Sen jälkeen, kannattaa → on hyvä; 7). Plus the nine unmodified chapters as
baselines. Every variant was diffed against its baseline: each differs only where intended. The controls keep the
meaning, but not always the style: two swaps put an example before its introduction (FI1, FI3), "kenties" is more bookish
than "ehkä" in speech, and in FI2 "heti, kun tavoitan hänet" became "saman tien, kun …", which reads oddly. No reviewer
flagged the FI2 control.

## Checkers

- **trace_check and repeat_check** (game-engine `tools/lukio/`), run on the changed scene files in this repository's
  process (game-engine only read); a defect is caught when the check reports something about the changed scene that it
  does not report about the original (counted by kind of finding, not by line, because an inserted line shifts the
  line numbers).
- **Model reviewer:** the explicit-criteria prompt of the 2026-11-24 pilot, unchanged, with the page as reference,
  run once per text with Haiku and once with Sonnet, on texts renamed to neutral ids. 127 texts × 2 models.

## Scoring

1. **Points at it** (`check6/score.py`, deterministic): a comment's quote shares three consecutive words with the
   planted line (or with the choice label above a planted "Oikein.") and contains the changed word where a word was
   changed; or the comment's quote or text names a word only the planted change brought into the chapter (the service
   name, the misspelt word, "sisältövaroitus", "isossa kuvassa", "hyvä kysymys", …).
2. **Names it:** two Sonnet judges, blind to the reviewer model, read each pointing comment with the planted change and
   decide whether the comment says what is wrong with it ("yes", "partly", "no"); one was told to be strict, the other
   to read as the writer who must fix the chapter. They gave the same label on 170 of 180 items. Three figures:
   **strict** (both "yes"), **lenient** (either "yes" or "partly"), and **read**: strict plus the ten split items read
   by hand (seven named the change, three did not; listed with reasons in `check6/analyse.py`). "Read" is the main
   figure.

## Results

### Deterministic checks

| Check | Catches | Misses |
|---|---|---|
| trace_check | wrong code 9/9; graded value question 2/9 (one menu with no basis comment, one whose basis is PUUTTUU) | everything else, 0 |
| repeat_check | nothing | everything: it reports sentences repeated across chapters, and every defect sits in one chapter |

Seven of nine planted "Oikein." pass trace_check because the menu already carries a basis comment: the check sees that
a graded choice has a basis, not whether grading fits an open question. No deterministic check exists for help lines,
112, content notes, praise, reassurance, services, misspellings or calques.

### Model reviewer

Named (read figure) / pointed at, out of applicable variants:

| Defect | Haiku | Sonnet |
|---|---|---|
| help line | 8 / 8 of 8 | 8 / 8 of 8 |
| 112 | 8 / 8 of 8 | 8 / 8 of 8 |
| content note | 9 / 9 of 9 | 9 / 9 of 9 |
| added rule | 9 / 9 of 9 | 9 / 9 of 9 |
| repeated reassurance | 9 / 9 of 9 | 9 / 9 of 9 |
| added service | 7 / 8 of 9 | 8 / 9 of 9 |
| changed condition | 6 / 6 of 7 | 5 / 5 of 7 |
| praise | 6 / 6 of 9 | 7 / 9 of 9 |
| graded value question | 6 / 6 of 9 | 6 / 6 of 9 |
| misspelling | 5 / 5 of 9 | 6 / 7 of 9 |
| calque | 1 / 5 of 9 | 4 / 9 of 9 |
| changed number | 1 / 1 of 1 | 1 / 1 of 1 |
| dropped own framing | 0 / 0 of 1 | 0 / 0 of 1 |
| **All defects** | **75 / 80 of 97 (77%; strict 74%, lenient 81%)** | **80 / 89 of 97 (82%; strict 78%, lenient 88%)** |
| Controls flagged for the edit | 1 of 21 | 0 of 21 |

- **Sonnet points at more, and names a little more:** pointing 92% against 82%, naming 82% against 77%. Pointed at by
  both: 79; only Sonnet 10, only Haiku 1; together 90 of 97. Sonnet's extra pointing is mostly calques, praise and
  misspellings, named in passing inside a comment about something else.
- **Inserted apparatus is always caught:** help lines, 112, content notes, added rules and reassurance, 100% for both.
- **Calques are pointed at but seldom named as calques.** Haiku names *isossa kuvassa* as English phrasing in 1 of 9,
  Sonnet in 4 of 9; most other comments call the line irrelevant filler (it was inserted without context), although
  the prompt names calques.
- **Single-letter misspellings:** named in 5 (Haiku) and 6 (Sonnet) of 9.
- **The graded open question:** named in 6 of 9 by both.
- **Changed conditions** (only plants where the page has the hedge): 6 (Haiku) and 5 (Sonnet) of 7.
- **False alarms on controls are rare.** Comments touched the changed line in 2 of 21 controls per model, almost
  always about another part of the line. The one comment about the edit itself (Haiku: "kenties" sounds bookish in
  speech) is fair.
- **Where the hit sits:** the first pointing comment is usually the reviewer's first comment (median rank 1; top three
  in 55 of 80 for Haiku, 61 of 89 for Sonnet). Sonnet filled all 12 comment slots in 118 of 127 texts, Haiku in 72, so
  defects compete with the chapter's real issues for the slots.

## What this cannot show

- **Planted defects are more conspicuous than real ones.** Inserted lines arrive without context, which is why they are
  ranked first; real help lines and services are written into the scene. The figures are upper bounds for inserted
  types. The calque result shows the confound: most comments caught the incoherence, not the English phrasing.
- **One run per text and one prompt.** Run-to-run variation is not measured (check 7 would); a different prompt can
  change the profile.
- **Few variants for two types** (changed number, dropped own framing: one each), and 7 for changed conditions.
- **The judges are models**, and Sonnet judged Sonnet's comments too (blind to the model). The split items were read by
  hand; the strict and lenient figures bracket the result.

## What follows

1. **Deterministic checks for the apparatus types.** Help lines, 112, content notes and praise formulas are form, not
   meaning: they can be counted in code against an allowed-places registry (one help block in TE1 ch08), as yamlgraph's
   two-strike rule suggests when a defect returns after prompt fixes. No check covers them today, and they recur.
2. **Misspellings go to check 3** (Voikko and omorfi), which finds a non-word deterministically; the reviewer finds
   about two in three.
3. **Services and numbers go to check 2** (novel ⊆ page), which finds an added name or changed number by set
   comparison.
4. **The reviewer is worth keeping for meaning:** changed conditions, a graded open question, added rules. Haiku is
   close enough for a first pass on these; Sonnet adds the passing mentions. Running both and taking the union points
   at 90 of 97.
5. **Calques remain uncovered** by every check tried (check 4 pilots, the reviewer here: at most 4 of 9). Planting
   calques inside coherent sentences would measure the reviewer fairly; the documented set of 53 is ready for it.
6. **Next measurement:** plant in context (rewrite an existing line rather than insert one), run each text three times,
   and add the persona prompt, so the recall figures hold for real defects and their spread is known.
