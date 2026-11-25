# Calque and LLM-Finnish pilot with corpus frequencies (check 4)

Date 2026-11-24. Operator: "go ahead with the pilot" (item 4 of `docs/feedback-loops-plan.md`, chosen because "it would
catch llm errors in general and might have wider applicability"). The ground truth is Finnish corpus frequency, not a
person's verdict. Pilot code and data are in the private `lukio-data` repository, folder `pilot/` (the 3.8 GB reference database stays
local); nothing here
runs in a build.

## Setup

- **Reference:** SemFi 2.1 (Zenodo record 1463685, CC BY-SA 4.0, checksum verified): lemma pairs with dependency
  relations, frequencies and z-scores from the Finnish Internet Parsebank, plus lemma frequencies (135 M tokens).
  Used only as a local lookup table, never published.
- **Parser:** Stanza 1.15 with its Finnish model (UD Finnish TDT): tokens, lemmas, parts of speech, dependencies.
- **Corpora:** the nine lukio novels (141 k words), the four lukio sites (279 k), curriculum text quoted on the sites
  (1.8 k, native control), and three library books in Finnish split by translator: one translated with an LLM in 2026
  (15 k) and two human translations from 1904 and 1923 (66 k).
- **Planted test:** 15 known calques ("Tämä ratkaisu tekee järkeä", "Juhla ottaa paikkaa", "Tunne itsesi vapaaksi
  kysymään"…) and 10 native controls ("tekee päätöksen", "vie aikaa", "pitää huolta"…), parsed the same way.

## Results

### 1. Under-attested word pairs

**Planted test.** On SemFi's own association score, the calques and the native controls separate well where both
can be scored: AUC 0.96 (9 calques, 9 controls). Every native control scores 14 or more; "tehdä + järki" scores 1.4,
"tehdä + pointti" 0.4, "tuntea + vapaa" 0.2.

**Limits found in the planted test.**
- 6 of the 15 calques could not be scored: the parser attached them in a relation SemFi does not record reliably
  ("olla samalla sivulla", "ottaa henkilökohtaisesti", "katsoa eteenpäin").
- 3 scored as native, because the lemma pair is native and only the case or the sense is not: "ottaa paikkaa"
  (partitive; native "ottaa paikkansa"), "ottaa aikaa", and "omata taito" (common in web text, though language advice
  discourages it). A lemma-level reference cannot see case.

**Real text.** The raw lists were dominated by artefacts, not errors, until three filters were added:
- SemFi records adjective–noun pairs sparsely (19% of the novels' adjective–noun pairs found, "iso pöytä" among the
  missing), and copula subjects and adverbials unreliably. Only verb–object, verb–subject, verb–adverbial and
  verb–verb pairs are usable.
- The parser and SemFi lemmatise differently: participles ("raskaana olevalle" → olla), compounds, pronouns.
  Compounds were backed off to their last part; pronouns and participles dropped.
- A pair unseen in SemFi means nothing when its words are rare; pairs are scored against the count SemFi would show if
  the two lemmas combined at random, and only pairs expected five or more times are scored.

After the filters, the top of the list shows one real pattern: **inanimate subjects doing what in Finnish a person
or a passive does**, a known English influence. From the sites and novels: "Mitä sivu sanoo?", "palvelut huomaavat
ympäristön ja oireiden yhteyden", "vastaus käyttää aineiston kohtia", "yhteinen käytäntö antaa mittapuun", "mitkä
valinnat pitävät vaihtoehdot auki" (keep options open), "kokouksen tapa voi antaa toisen sanalle enemmän painoa"
(give weight), "Mitä alue voisi tehdä?", and in a translated quotation "mieli ottaa haltuunsa".

Share of scored pairs far below expectation (ratio under 0.25):

| Corpus | Pairs scored | Flagged | Share |
|---|---|---|---|
| Curriculum (native) | 39 | 0 | — (too small) |
| Human translations, 1904 and 1923 | 1,440 | 5 | 0.35% |
| LLM translation (Alice), 2026 | 365 | 0 | 0% |
| Lukio novels | 2,942 | 29 | 0.99% |
| Lukio sites | 3,990 | 51 | 1.28% |

The sites and novels flag about three times as often as the old human translations, but genre differs (expository
and dialogue against narrative), so this is not yet evidence that the difference is the model.

### 2. Over-represented lemmas (keyness)

Log-likelihood keyness against SemFi's lemma frequencies, read by part of speech. Two kinds of signal, mixed:

- **Formula repetition**, found without any list: in the novels "aivan" appears 8,254 times per million against 470 in
  SemFi (the "Ei aivan." and "Aivan." feedback lines), "oikein" 3,135 against 375 (the "Oikein." feedback), "entä"
  1,260 against 90, and "kuvitteellinen" 2,167 against 16 on both sites and novels (the stamped "kuvitteellinen
  henkilö").
- **Translationese in the LLM translation:** manner adverbs in -sti, the shape of English -ly dialogue tags, are
  strongly over-represented in the 2026 Alice ("kiireesti" 1,216 per million against 4.5, "arasti", "vihaisesti",
  "levottomasti", "kärsimättömästi") and absent from the top of the 1904 and 1923 human translations, which favour
  "äkkiä", "pian", "hitaasti".
- **Topic**, which drowns the rest unless separated: "empiirinen", "normatiivinen", "perustella" on the sites; "huutaa"
  and "mestata" in Alice.
- Lemma mismatches again ("toinen" and "lainkaan" barely exist in SemFi's lemma list).

## What the pilot shows

- **Corpus frequency does carry the signal.** It ranks the planted calques below native phrases, surfaces the
  inanimate-subject pattern and the -sti adverbs, and finds the repeated feedback formulas, all without a list and
  without a human verdict.
- **Not usable as a gate, and not yet as a ranked list.** Most of the noise comes from the reference, not the text:
  a different parser and lemma convention, missing relations, no case. And keyness mixes style with topic.
- **The LLM translation did not stand out on word pairs** (0 of 365), while its adverbs did. The LLM-written study
  text stands out on both. Small samples; one run.

## Next steps, by what they fix

1. **Build the reference with the same parser.** Parse a native Finnish corpus with the same Stanza pipeline, so
   lemmas, relations and compounds match by construction, and keep case. This removes most artefacts at once.
   Candidate sources need licence checks: Finnish originals in Project Gutenberg (public domain, dated language),
   Finnish Wikipedia (CC BY-SA, partly translated), Kielipankki corpora (PUB ones only).
2. **Surface n-grams** (FNC1 newspaper n-grams, CC BY) for case-level calques ("ottaa paikkaa") and multiword formulas
   ("Ei aivan", "Juuri niin", "Se on…, että").
3. **Separate style from topic** in keyness: compare against a native reference of the same genre (expository
   school text, dialogue, narrative), or count only function words, adverbs and constructions.
4. **Measure with more planted cases**, including the inanimate-subject pattern and -sti adverbs, and report recall per
   pattern (check 6), before anything is used to steer writing.
