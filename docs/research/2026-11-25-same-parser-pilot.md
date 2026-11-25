# Check 4, second pilot: a same-parser native reference from Projekti Lönnrot

Date 2026-11-25. Follows `2026-11-24-calque-pilot.md`, whose main noise source was the mismatch between our parser
(Stanza) and SemFi's (lemmas, compounds, relations, no case). Here the reference is native Finnish parsed with the
same Stanza pipeline, so both sides match by construction, and the dependent's case is kept. Operator: "Yes, pilot
it". Code and data: the private `lukio-data` repository, folders `lonnrot/` and `pilot2/`.

**Result in one line:** a same-parser reference removes the parser artefacts but is too small and too old to work as
a calque check. It flags none of the documented calques and at most one of the own planted ones, and its case check
flags native text as often as ours. What it does show, in four of five author splits (and at the edge in the fifth),
is that the novels, the sites and the LLM translation have more rare word pairs than any native sample of the same
size, while the 1904/1923 human translations do not. With a reference from 1900–1950 that excess cannot be told apart from modern Finnish
simply being newer. The strongest signal is again repetition: "Ei aivan." occurs 977 times in the novels.

**Review.** Three verification rounds changed this pilot. The first (four lenses, each finding put to a refuter; 18
findings, none refuted) found 23 translations in the "native" reference, compound counts merged into plain words, a
wrong threshold in the planted count, and a biased comparison. The second (numbers and claims, 9 findings) found an
anthology carrying a translation and a held-out author, overstated author checks, and one wrong number. Removing books
then changed which authors were held out, and the result moved, so the comparison is now run over all five author
splits. A third round (the five-fold numbers) found per-fold values listed out of order and two ranges taken from
one fold only. All numbers below are after the fixes.

## Reference

- **Source:** Projekti Lönnrot (lonnrot.net), public-domain Finnish e-books, plain text in zip files. The site gives
  no explicit licence; it says the works are public domain in the EU and free to distribute. Used locally only.
- **Sample:** 500 books, at most 3 per catalogue author (fixed seed), downloaded at one request per second.
- **Filter** (deterministic, from each file's own title page and an outside record, not from author names):
  - **original, not translation:** no translator line on the title page, which runs up to the imprint year
    ("suom.", "suomensi", "suomentanut", "suomennos", "kielestä", "mukaili"...)
  - **year:** published 1900 or later; the year is the first standalone year on the title page, so a range in a title
    ("1914–1918") or a life span ("1854–1930") is not read as the publication year
  - **language:** Finnish, not Swedish (function-word ratio)
  - **not a play:** a genre word on the title page ("huvinäytelmä", "yksinäytöksinen") or a cast list ("HENKILÖT")
  - **not an edited collection** ("Toim.", "Toimittanut"): an anthology can hold translations, verse and other
    authors that its title page does not show
  - **prose, not verse:** median line length
  - **author language:** Wikidata (P1412 languages written, P103 native language), first matching person born
    before 1930. Books by authors recorded with languages that do not include Finnish are dropped, because some
    translations name no translator: 9 authors (Andrejev, Blicher-Clausen, Fielding, Furuhjelm, Geijerstam, Glyn,
    Nansen, Rolland, Söderhjelm). Among the kept authors, 52 are recorded as writing Finnish; 31 are kept unchecked:
    26 matched a person with no language recorded, and 5 were not matched at all. The lookup takes the first match,
    which can be the wrong person (Geijerstam matched his son, also a Swedish writer).
- **Kept:** 97 books under 83 catalogue author names (81 people: two authors appear under two spellings), published
  1900–1950s (one 1994 reprint of a 1930s book), each capped at 300,000 characters: 20.9 million characters. Mostly
  fiction, but also memoirs, history, biography, an ethnography and dialect texts.
- **Split:** authors are divided into five folds by sorted name; each fold in turn is held out as a native control the
  reference has never seen. A reference is 75–79 books by 66–67 author names, 2.0–2.2 million words and about 0.9
  million content-word pairs; a control is 18–22 books by 16–17 names.

Rejections among the 500 (a book can have several reasons): 248 translated, 152 published before 1900 or with no
year found, 61 verse, 55 plays, 24 Swedish, 8 edited collections, 2 by authors with a translated book in the sample,
9 by the Wikidata rule.

## Method

- **Parse:** Stanza 1.15.1, Finnish TDT, the same pipeline as the first pilot, now keeping morphological features.
  Books are joined into paragraphs at blank lines before parsing (they are hard-wrapped); the pilot corpora are
  parsed line by line, as before.
- **Pairs:** content words (noun, verb, adjective, adverb, auxiliary) in the relations obj, nsubj, obl, xcomp, amod,
  advmod, nmod, nmod:poss, nsubj:cop, ccomp, advcl.
- **Rarity:** `ratio = (observed + 0.5) / expected`, where expected = (head's count as head of the relation) ×
  (dependent's count as dependent) / (relation total), in the reference. A pair is scorable only if expected ≥ 5;
  flagged if ratio < 0.25. Pairs are scored on exact lemmas; only when that is not scorable and one word is a
  compound, on a separate view of the reference where every compound is reduced to its last part.
- **Case:** for a pair seen at least N times in the reference, the share of its occurrences with the text's case on
  the dependent; flagged below 5%.

## Results

### Planted test sets

| Set | Calques | Natives | Scorable (calque / native) | Flagged (calque / native) |
|---|---|---|---|---|
| Own (first pilot) | 15 | 10 | 3 / 5 | 0 / 0 in four folds, 1 / 0 in one |
| Documented (new) | 53 | 53 | 2 / 1 | 0 / 0 |

The documented set is new: a workflow collected English-model phrases that Finnish language sources name, with the
native wording each source gives, and a second agent opened every page to confirm it. After the review removed two
duplicates and two items whose source gives only a gloss, 53 remain: Kielikello (27, four articles), the Oulu
university language centre's guide (16), jkorpela.fi kielenopas (6), Kielitoimiston ohjepankki (4). Carrier sentences
were written by a model; one was corrected in review (*paras ikinä* now in the bare predicative form the source
quotes).

- **Coverage is the limit.** Only 2 of the 53 documented calques and 3 of the 15 own ones are scorable. The rest have
  no matching pair in the parse (constructions such as "hän joka" or "sekä – ja", forms such as "viikon sisällä"), or
  a pair the reference has too little data on (word-order calques like "Vene löytyi rannalta" are parsed, but their
  lemmas and relation are the same as in the native order, so no pair method can see them).
- **No reliable catch.** The first draft reported *ottaa paikkaa* as caught by the case check. That depended on
  compound objects (koti#paikka, kauppa#paikka...) being counted as *paikka*. On plain lemmas the reference has
  *ottaa + paikka* 4–8 times, below the case check's minimum, so it is not tested. The one flag, *antaa ajatus* in
  one fold, rests on a single reference occurrence (ratio 0.19); in the other folds its ratio is 0.34–0.45.
- AUC by ratio (`pilot2/score_fold*.log`): 0.93–1.0 on the own set (3 calques, 5 natives), 0.0 on the documented set
  (2, 1). At these sizes the values mean nothing.

### Rates: flagged pairs per corpus

By occurrence (every pair token counts), fold 0; the other folds are within a point except where ranges are given:

| Corpus | Pairs | Scorable | Rare (ratio < 0.25) | Without pairs repeated ≥ 50 times |
|---|---|---|---|---|
| Held-out native (20 books) | 244,089 | 24,656 | 2.9% (folds 2.5–3.0%) | 3.2% |
| Novels | 50,031 | 4,081 | 26.9% | 4.2% |
| Sites | 99,850 | 3,786 | 4.4% (folds 4.4–7.0%) | 6.0% (folds 5.7–7.1%) |
| Human translations 1904, 1923 | 28,136 | 2,462 | 3.4% (folds 2.7–3.4%) | 3.4% |
| Alice, LLM translation 2026 | 5,644 | 684 | 4.2% (folds 4.2–4.8%) | 4.2% |

The novels' 27% is one formula: "Ei aivan." (*ei + aivan*, advmod) occurs 977 times; the next rare pair, "ei hyvin",
24.

Counted once per distinct pair, against native samples with the same number of distinct scorable pairs (200 samples
per fold, each reading the held-out books in a random order from a random start; exact lemmas only;
`pilot2/compare.py fold=k`), over the five author folds:

| Corpus | Rare share of distinct pairs | Native median per fold | Native samples as high, per fold |
|---|---|---|---|
| Novels | 5.5–6.0% | 3.4–4.0% | 6, 0, 0, 0, 0% |
| Sites | 5.5–6.2% | 3.4–3.8% | 5, 0, 1, 0, 0% |
| Alice, LLM translation | 5.2–5.5% | 2.9–3.5% | 4, 1, 1, 0, 1% |
| Human translations 1904, 1923 | 4.0–4.9% | 3.7–4.2% | 10, 19, 72, 28, 57% |

The novels, sites and Alice sit above the native range in four of five folds, about 2 points above the native
median; in fold 0 all three fall just inside it (4–6% of native samples as high). The old human translations sit
inside it in every fold. Single held-out books, each measured on all its distinct
pairs, mostly fall between 2% and 6.6% (one reaches 7.5%; one very short book has none), so the gap is real but not
large.

**What the excess can and cannot mean.** The reference and the control are 1900–1950s text; the sites and novels are
2026 educational Finnish, Alice 2026 fiction. Modern native phrasing reads as rare against old text, so the excess in
modern text cannot be told apart from the reference's age (or from register: educational prose against mostly
fiction). The old translations show no excess, so translation as such does not produce it in this measure; but they
share the reference's era, so they do not separate era from English influence either. Separating those needs a
modern native reference.

### Case check

Limited to verb objects and obliques, with the reference pair seen at least N times (fold 0; across folds the
held-out native rate at N = 40 runs from 3.1% to 5.7%):

| N | Held-out native | Novels | Sites | Human 1904/1923 | Alice |
|---|---|---|---|---|---|
| 10 | 5.6% | 6.8% | 4.0% | 6.5% | 8.0% |
| 20 | 5.0% | 5.8% | 3.0% | 6.1% | 6.9% |
| 40 | 3.8% | 6.3% | 2.7% | 5.8% | 4.5% |

Native text is flagged at about the same rate as ours; the sites are flagged least or nearly least. The flags are case alternations
with a different meaning or construction ("puhua asioissa", "tehdä vuoden", "tehdä mielelläsi") and attachment
differences. On all relations, verb–noun obliques are the largest or tied-largest group of case flags (about 42–60% across
folds), except on the sites, where adjective–noun pairs lead (53–60%); those mean nothing, because an adjective
agrees in case with its noun.

### What the lists show

Without repetition, the rare-pair lists are mostly native phrasing the reference does not cover (*alkaa maksaa*,
*löytää asiat*, *ottaa huomioon terveysvaikutukset*) and attachment differences. A few items are recognisable
English-model phrasing: in the LLM translation "korkea aika" ("high time") and "tiedätkö tien pois" ("know the way
out"). "Hyvä kysymys" also appears, but on the sites it is inside a media-literacy task as a deliberate example of a
flattering AI answer, which is correct use. These are candidates, not findings; a reader decides them.

## Conclusions

1. **The parser mismatch was real but not the whole problem.** A same-parser reference removes the lemma and
   relation artefacts; what remains is sparsity and era. With about 2 million words, 10% of the held-out native pairs
   are scorable, 8% of the novels' and 4% of the sites'.
2. **No calque detection at this size.** No documented calque and at most one own planted calque (on a single
   reference occurrence) is flagged, and the case check flags native text about as often as ours.
3. **Modern text has more rare pairs than old native text; the cause is open.** About 2 points more for the novels,
   the sites and the LLM translation, above every native sample in four of five author splits and at the edge in
   the fifth, and none for old human translations. Era, register and
   English influence all predict this; only a modern native reference can separate them.
4. **Repetition is the strong, cheap signal.** "Ei aivan." ×977 in the novels was found by both pilots, by keyness
   in the first and by pair counts here. A repetition check (keyness against a native reference, check 6's planted
   formulas) needs no parser and no large corpus.
5. **Documented calques are mostly invisible to word pairs.** Constructions, forms and word order make up most of
   the 53. A check for them is either a pattern list with sources (which section 7 of the content guideline rules
   out as a decision-maker) or a model reviewer measured with planted defects (check 6).
6. **One split is not enough.** Removing four books changed the held-out authors and moved the result from "above
   every native sample" to "just inside the range" in that fold. Any rate comparison here needs all folds.

## What would change the conclusion

- A **modern** native reference parsed the same way, tens of millions of words: removes the era confound and the
  sparsity at once. Candidates need a licence check (Finnish Wikipedia, CC BY-SA; government text; the Yle news
  archive is research-only).
- Scoring against SemFi for coverage and the same-parser reference only to **confirm** a candidate (the hybrid in the
  first pilot's next steps).

Recommendation: stop developing check 4 as a calque detector; keep its keyness part as a repetition and formula
check, and put the effort into check 6 (planted defects), which the documented set here seeds with 53 sourced cases.
