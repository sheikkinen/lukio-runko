# Existing cross-cultural research: what the norm ledger can use

This synthesis draws on five fact-checked research reports (dimension models, communication and pragmatics, moral psychology, Finnish institutional practice, LLM cultural bias), corrected after a critic's review. Sources were opened on 2026-11-23 unless marked otherwise. **Unverified** means nobody opened the source. **Not re-checked** means only the earlier report read it and the critic could not confirm it. Ledger read: docs/norm-ledger.md.

## 1. Short answer

Yes, there is existing work we can use. How much it helps depends on the job:

- **Frame: supporting work exists, but it does not prove the premise.** Published work is *consistent with* the ledger's premise, "shared values, different customs":
  - Philosophy: value pluralism (SEP). Walzer's thick/thin morality fits too, but the book's argument is known only from summaries (**unverified**).
  - Moral psychology: Turiel's moral/conventional test; Curry's 60-society study.
  - LLM research: Tao et al. 2024 measured models on 10 values-survey items placed on two Inglehart–Welzel axes. GPT-4o's default sits next to Finland (distance 0.20). This shows closeness on survey values only. It is consistent with the drift being in customs, genre and wording, but it does not show that.
- **Row bases: some, and the best ones are Finnish.**
  - The useful sources are Finnish institutions and Finnish linguistics: JSN and the media organisations, MIELI, OPH, Kotus, the University of Helsinki, and articles in *Virittäjä* and *Sananjalka*.
  - The famous international culture comparisons (Hofstede, GLOBE, Lewis, Meyer, the "silent Finn") are **not** usable as row bases.
- **One finding cuts against a current row.** Finnish media organisations recommend help information in **suicide news**, by judgement. So row 3's basis should stop implying that all help information is a US habit. Every source found is about news. Carrying that scope over to study material is our inference.
- **Another finding limits a possible row.** Finnish official-language guidance (Kotus) recommends signposting: lead with the main point, use subheadings and lists. Reader guidance as such is not an Anglo habit.
- **Checker: no existing test set covers Finnish customs.**
  - NormAd, BLEnD and the Cultural Atlas have no Finland data. CulturalBench and CultureBank coverage of Finland is unverified.
  - FIN-bench-v2 is mostly translated from English and has no culture task.
  - Two things carry over:
    - NormAd's row format, as a template for our own small test set. CCSARP-style discourse-completion tasks may suit wording-level rows better (**unverified**).
    - One prompting lesson: a "write as a Finn" persona makes output worse, and explicit norms work better.

## 2. Recommended frame

**Core: value pluralism, tested with Turiel's moral/conventional distinction. Walzer's thick/thin vocabulary may be added once the book is read.**

- **Thin, shared values.**
  - Walzer, *Thick and Thin*, University of Notre Dame Press, 1994 (https://muse.jhu.edu/book/48179). The book distinguishes "maximalist and minimalist, local and universal" moral argument. Its detailed argument is known only from summaries (**unverified**). Do not cite it in the ledger until it is opened.
  - Curry, Mullins & Whitehouse 2019, *Current Anthropology* 60(1):47–69. Seven cooperative behaviours are judged good in 60 societies, with "uniformly positive" valence. https://ora.ox.ac.uk/objects/uuid:8dd8d82d-3829-4857-bcf4-eebf196d11be/files/r3r074t925
  - Mapping onto the ledger:
    - "Moral principle" rows are thin. "Custom" and "house style" rows are thick.
    - Person-first etiquette and helpline footers are thick US expressions of thin values (dignity, care). That last point is our interpretation, not Walzer's.
- **A test for the level column** (SEP, "The Moral/Conventional Distinction", 2022, https://plato.stanford.edu/entries/moral-conventional/).
  - A norm is moral if breaking it would still be wrong without any authority requiring it, and wrong everywhere, justified by harm, justice or rights.
  - If it depends on an authority or a place, it is a convention.
  - Applied to the ledger: help boxes, content notes and person-first wording are conventions.
- **Caveat that keeps the "basis" rule necessary.**
  - The same SEP entry reports that what counts as moral rather than conventional varies across cultures (Shweder et al. 1987; Haidt, Koller & Dias 1993). It calls the question open ("the jury is still out").
  - So a row's level is a judgement that needs a basis. The research does not settle it.
- **Real moral disagreement (row 6).**
  - Mason, "Value Pluralism", SEP, first published 2006, revised 4 June 2023, https://plato.stanford.edu/entries/value-pluralism/.
  - It says "moral value pluralism does not entail relativism". It also says irresolvable disagreement is not necessarily due to "wickedness on the part of our interlocutor".
  - This gives a principled basis for "weigh the reasons; any well-argued view is accepted" without sliding into "anything goes".
- **Finland and the US are close on survey values.**
  - Muthukrishna et al. 2020, *Psychological Science* 31(6):678–701. This is values-survey data. Cultural distance from the US: Finland .072, Sweden .115, Norway .124. Finland's value was cross-checked against the paper text and Atari et al. 2023, Table 1.
  - Tao et al. 2024, *PNAS Nexus* 3(9):pgae346, https://academic.oup.com/pnasnexus/article/3/9/pgae346/7756548. This is 10 IVS items on two axes. GPT-4o's default is nearest Finland (0.20), with Andorra effectively tied (0.21). Read this as closeness to a cluster, not to Finland in particular. It says nothing about customs.
- **Describe expectations, not national character.**
  - Olbertz-Siitonen & Siitonen 2015, *Sosiologia* 52(4):318–333, https://journal.fi/sosiologia/article/view/124209. The article is in English. The abstract calls the "silent Finn" an academic myth "lacking empirical evidence". Only the abstract was checked.
  - Isosävi 2023, read via Tiittula's review in *Puhe ja kieli* 44(1), 2024, https://journal.fi/pk/article/download/146487/93224/344345. People classify behaviour that breaks their expectations as a trait of a whole culture.
- **Candidate addition: cultural scripts** (Wierzbicka & Goddard, Natural Semantic Metalanguage; for example Wierzbicka, *English: Meaning and Culture*, OUP 2006) (**unverified**).
  - This work describes Anglo norms of speaking as explicit scripts, without national-character claims. It is the closest existing match to the ledger's "model default" column.
  - Known criticism: the scripts are written by researchers, and their empirical grounding is debated.
- **Optional vocabulary.**
  - GLOBE's split between practices ("as is") and values ("should be") mirrors our premise: https://globeproject.com/study_2004_2007.
  - Brown & Levinson's positive vs negative politeness, as used by Lampinen 1990 (Lampinen not re-checked).

## 3. Ledger rows and possible existing bases

Row numbers follow the ledger. The earlier draft filed Mauranen (signposting) under row 5 and address form under row 10. Neither topic is a ledger row: row 5 is repeated reassurance and disclaimers, and row 10 is "A rule in a style guide". Those topics have moved below.

| Row | Source | What it says | Strength |
|---|---|---|---|
| 1 Person-first | University of Helsinki news, "Näe ihminen, älä vammaa", 11.2.2015, https://www.helsinki.fi/fi/uutiset/talous/nae-ihminen-ala-vammaa | Verified. Vehmas: "Kysymys ei ole niinkään yksittäisestä sanasta kuin merkityksestä, joka siihen liitetään", and "Liiallinen kiertoilmaisujen keksiminen menee jo pelleilyksi". The article paraphrases Alanne: *vammainen* is correct when used properly. **It also reports the opposite view:** the word can reduce a person to the disability, and a parent says "Kehitysvammaisuus ei määritä häntä". It never discusses person-first constructions, and it says nothing about illness words. | Finnish academic experts in a news piece. Two-sided, about disability, not illness. Any use must quote both sides. |
| 1 | APA Style disability page (both person-first and identity-first acceptable) | **Unverified**: the page fetched empty. | — |
| 1 | Finnish patient organisations' own usage of illness words (e.g. *diabeetikko*, *syöpään sairastunut*) | **Unverified**: not searched. This would be a better basis for illness than the disability source. | — |
| 3 Help blocks | Suicide-reporting checklist by media organisations, including JSN (Journalistiliitto, Paikallislehtien Päätoimittajayhdistys, Aikakauslehtien päätoimittajat, Päätoimittajien yhdistys, Suomen Kaupunkilehtien Päätoimittajat, JSN), 10.9.2020, https://jsn.fi/toimittajille-avuksi-muistilista-itsemurhista-uutisointiin/ | Verified. "Jos uutisen yhteyteen luontevasti sopii, kannattaa kertoa tukipalveluista". "Itsemurha ei kuitenkaan ole tabu." The page says the checklist is not an appendix to or supplement of the Journalistin ohjeet. THL took part, and the checklist belongs to STM's suicide prevention programme 2020–2030, according to Yle and search results (**unverified**). | Primary Finnish media self-regulation and organisations. Audience is journalists, scope is news. |
| 3 | MIELI ry blog, Kukkonen, 29.7.2025, https://mieli.fi/blogit/itsemurhista-tulee-puhua-ja-uutisoida-vastuullisesti/ | Support services are "tärkeää" in connection with **news**. "Itsemurhista puhuminen ei ole kiellettyä". | Finnish expert organisation, blog post. News scope. |
| 3 | Yle, 20.8.2025, https://yle.fi/a/74-20178483 | Verified. Yle, HS and Keskisuomalainen attach help information to suicide news. They usually do not report individual suicides at all. Nothing on other topics. | Evidence of news custom; one article. |
| 3 (last clause) | OPH, opiskeluhuoltopalvelut, https://www.oph.fi/fi/koulutus-ja-tutkinnot/opiskeluhuoltopalveluista-apua-ja-tukea-oppilaille-ja-opiskelijoille | Students have a right to a kuraattori, a psykologi and health care, and lukio is named. A non-urgent meeting is arranged "seitsemän päivän kuluessa", an urgent one "jo samana päivänä". It shows the service exists. It does **not** show that Finnish study materials point to it instead of helplines. | Primary Finnish institution. The statute (1287/2013 §15) was not opened. |
| 3, 4 | LOPS 2019 terveystieto objectives | **Unverified**: not opened. If the curriculum names support services, help-seeking, or 112 in first aid, this is the most relevant primary basis: for the one allowed help block, and for teaching 112 as subject matter. | — |
| 3 | School-side sources: OPH crisis-preparedness material, school crisis plans (Iisalmi and Siikalatva lukio found in search), STM suicide prevention programme 2020–2030, Ylen journalistiset ohjeet | **Unverified**: not opened. These would describe school practice better than news checklists. | — |
| 4 Content notes | Bridgland, Jones & Bellet 2023, meta-analysis of 12 studies, via APS release 12.10.2023, https://www.psychologicalscience.org/news/2023-october-content-warnings-distress.html | Warnings raise anticipatory anxiety. They do not change emotional reactions, avoidance or comprehension. | Academic, via press release. Shows an effect, not a custom. Supporting evidence only. |
| 4 | OPH, "Psyykkinen turvallisuus", https://www.oph.fi/fi/koulutus-ja-tutkinnot/psyykkinen-turvallisuus | Safety lies in a "turvallinen ja hyväksyvä ilmapiiri". Nothing on warnings. | Primary institution. Argument from absence, so weak. |
| 6 Value questions | Value pluralism (SEP); CulturalBench, Chiu et al., ACL 2025, https://arxiv.org/abs/2410.02677 | Pluralism without relativism. Models "overfit to a single answer" on questions with several valid answers. | Philosophy reference; academic evidence on model behaviour. The curriculum basis stays primary. |
| 7 Praise and filler | Lampinen 1990, *Sananjalka* 32(1):77–92, https://journal.fi/sananjalka/article/view/86526 | **Not re-checked** (the landing page has no abstract). From the earlier report: being "liian kohtelias ja epäsuora" for the situation can be read as "halpahintaiseksi imarteluksi tai vihamieliseksi ironiaksi". This concerns politeness in general, not praise specifically. | Academic Finnish linguistics, 1990. Open the PDF before citing. |
| 7 | Etelämäki, Haakana & Halonen 2013, *Virittäjä* 117(4), https://journal.fi/virittaja/article/view/7942 | Finnish compliments have simple syntax: conventional copula clauses or verbless descriptions, avoiding first-person reference. It does **not** show that Finns praise less. | Academic, everyday talk. **Abstract only.** |
| 7 | LOPS 2019 assessment (feedback describes progress against goals) | **Unverified**: not opened. It could give an institutional-rule basis. | — |
| 8 Calques and *you* | Lampinen 1990 §2.6 | **Not re-checked.** From the earlier report: the passive and the generic third person (zero person) are politeness devices where English uses *you* or *we*. *Ole hyvä ja* is native, not a calque. | Academic. Open the PDF before citing. |
| 8 | Kielitoimiston ohjepankki; Kielikello archive (anglicisms, calques) | **Unverified**: not opened. These are likely better row-8 bases than Lampinen. "Tehdä järkeä" was not found in a quick search. | Primary Finnish language authority. |
| 9 Institutions | OPH opiskeluhuolto page (above) | Names the Finnish support route. | Primary institution. |
| **New A**: reader address (sinuttelu/teitittely; address on hard topics) | Tolvanen 2016, *Virittäjä* 1/2016:5–29, https://journal.fi/virittaja/article/download/49565/18472/54948; Lappalainen & Niskanen, HY news 19.9.2018, https://www.helsinki.fi/fi/humanistinen-tiedekunta/ajankohtaista/suomessa-ikaihmiset-pitavat-sinuttelusta-ranskassa-ja-venajalla-teititellaan | Tolvanen: in Kela pension texts (about 2013), direct address is combined less often with death or illness. Prohibitions are put indirectly. Imperatives in general are not avoided. Address practice is not fully settled. Lappalainen & Niskanen: opinions on sinuttelu and teitittely differ, and online discussion uses sinuttelu. **Counter-evidence (search hits, not opened):** Kotus material says Kela has addressed customers with sinuttelu in letters since the early 2000s. Officialdom seems to have no clear guideline on reader address. An HY news piece argues the passive "pilaa helposti suomenkielisen tekstin". Kotus guidance was never opened, so "no Kotus recommendation found" is not established. | One genre and one study. **Too weak for a ledger row.** Candidate list for human reading only. Further bases (**unverified**): Yli-Vakkuri 1989; *Saako sinutella vai täytyykö teititellä?*; Kielitoimiston kielioppiopas; Selkokeskus. |
| **New B**: politeness carried by grammar | Lampinen 1990 | **Not re-checked.** From the earlier report: the view that Finns are impolite because they say *please* less "on tietenkin väärä". Finnish marks politeness with conditionals, clitics, the passive and question forms. Kielitoimiston kielioppiopas lists teitittely among politeness devices, beside *ole hyvä*, *ystävällisesti* and *kiitos*. This is consistent, but seen in the contents list only (**unverified**). | Academic. Open the PDF before citing. |
| **New C**: no national-character claims | Olbertz-Siitonen & Siitonen 2015 | The abstract supports "academic myth" and "lacking empirical evidence". The earlier claim that the article dismisses films, proverbs and anecdotes, and calls Lewis's work not "serious academic inquiry", is **unverified**: it is not in the abstract. Open the full text, or drop that claim. | One peer-reviewed article. Not a consensus. Supports a guideline rule, not a custom. Possible Finnish counterweights: Isotalus; Tiittula (**unverified**). |
| **New D**: US culture-war axes on value questions | Kivikangas et al. 2021, *Psychological Bulletin* 147(1):55–94, https://researchportal.tuni.fi/en/publications/moral-foundations-and-political-orientation-systematic-review-and/ | The link between moral foundations and political orientation "varies culturally (between regions and countries)". The 2017 Finnish representative-sample paper is **unverified**. | Academic meta-analysis. Too weak for a row; hold. |
| (dropped) Signposting and metatext | Mauranen 1993 (**unverified**, secondary sources only); Kotus poster "Virkamiehen huoneentaulu virkakielen parantamiseksi" (verified): "Aloita pääasiasta", "Käytä väliotsikoita…", "Käytä hahmottamisen apuna luetteloja" | Finnish official guidance supports signposting, so a row framing reader guidance as an Anglo habit would contradict a Finnish source. At most, a row could cover metatext in academic prose, and only once Mauranen is opened. | Kotus: primary Finnish institution. |

## 4. What not to use, and why

- **Dimension scores as row bases.** This covers Hofstede (FI vs US "motivation towards achievement" 26 vs 62), GLOBE (assertiveness practice 3.81 vs 4.55), WVS maps, Schwartz and Gelfand.
  - They measure values as national averages, not the customs our rows cover.
  - The Hofstede FAQ itself says scores are relative and individuals differ. It concedes the old US individualism score "may have been too high".
  - Akaliyski et al., *JPSP* 2025: Hofstede overestimated individualism in English-speaking countries by 27 points. This comes from a Sussex press release; the paper was not opened (secondary).
  - They may appear only as "consistent with" context, never as a basis.
- **Moral Machine, MFQ and WVS national averages for rows.**
  - Graham et al. 2011: "variation within cultures … will exceed the east-West variations".
  - Atari et al. 2023: religious differences (SD 2.16) far exceed national ones (SD 0.36). MFQ-2 has no Finland sample.
- **Popular cross-culture books.**
  - Lewis, *Finland, Cultural Lone Wolf*; Meyer, *The Culture Map*; Hall; Carbaugh's "silent Finns".
  - The myth critique targets this kind of source. Meyer even puts the Nordics on the same "direct" side as the US (Scandinavia Standard summary).
- **The Cultural Atlas and NormAd content.** No Finland page or rows (the Finnish page returns 404). Their norms are outsider generalisations.
- **CultureBank.** Social-media self-reports, centred on US platforms.
- **Persona prompts in briefs ("write as a Finnish teacher").**
  - Tao et al. (verified): GPT-4o's distance to Finland rose from 0.20 to 2.43 under a Finland prompt.
  - Durmus et al. 2023 (https://arxiv.org/abs/2306.16388): perspective prompts can reproduce stereotypes.
- **The claim "any help information is US".** Contradicted, for news, by the JSN checklist, MIELI and Yle (row 3 above).
- **The claim "signposting/reader guidance is Anglo".** Contradicted by the Kotus poster.
- **Recommending the passive for prohibitions as Finnish practice.** One genre study cannot carry it, and Finnish sources criticise passive overuse. Recommending it would create a house rule disguised as Finnish practice.
- **Flagging *ole hyvä ja* as a calque.** Lampinen cites it as native Finnish politeness (not re-checked).

## 5. Checker ideas (deterministic; each flags for a person, none decides meaning)

1. **Help-block locator.**
   - Match phone-number patterns, "112" and known helpline names. Report every hit outside the one allowed terveystieto mental-health chapter.
   - It detects a form, not a meaning. Teaching 112 in first aid and emergency procedures is Finnish curriculum content, so hits in such contexts are expected false positives, and a person decides.
   - Row 3; the operator's decision stands. See P3 for the ledger fix that separates help-block footers from 112 as subject matter.
2. **Content-note header locator.** Find structural markers at the top of a page: a heading or callout before the first content heading. Row 4.
3. **Repeat check.** Already planned (`docs/repeat-check-plan.md`). Row 5.
4. **Scope check for help information.** If help information appears, report whether the page's own topic metadata is the mental-health chapter. Never infer from wording.
5. **Candidate lists for human reading.** These use morphological analysis, not keyword verdicts, and each is only a list of candidates.
   - Second-person forms in the same paragraph as death or illness topics, in pages whose metadata marks such a topic (Tolvanen; one genre, so weak).
   - Second-person imperative negations (*älä*, *älkää* + verb) addressed to the reader (Tolvanen). No alternative form is prescribed.
   - Generic *sinä* candidates. These need a person to judge, because generic *sinä* is also native in spoken Finnish.
   - Exclamation-final standalone sentences at paragraph starts (praise formulas, row 7). The current list of known formulas such as "Hyvä kysymys!" stays an exact-string list of house decisions, not a meaning test.
6. **Ledger regression set in NormAd format** (NormAd, NAACL 2025, https://arxiv.org/abs/2404.12464; CSV columns `Background, Axis, Value, Rule-of-Thumb, Story, Explanation, Gold Label`).
   - Build about 3–5 situations per ledger row. Each gold label cites the row and its basis.
   - Example: Story "a terveystieto page about cancer ends with 112 and helpline numbers", Gold = no. Include a first-aid page teaching 112, Gold = yes.
   - Run it on each new prompt or model. Scoring against gold labels is deterministic.
   - NormAd's own result supports putting explicit rows into briefs: with the norm given, models score under 82%; with only country and values, under 60%.
   - For wording-level rows (requests, apologies, compliments), discourse-completion tasks from cross-cultural speech-act research may fit better: CCSARP, Blum-Kulka, House & Kasper 1989 (**unverified**; check whether Finnish data exist).
7. **Native-speaker judgement stays the reference.** DaKultur (C3NLP 2025, https://aclanthology.org/2025.c3nlp-1.5/): machine-translated data are insufficient for cultural adaptation, and the best model reaches only 42% native acceptance. This matches the operator-as-basis rule.

**Existing evaluation sets, none usable unchanged:**

- NormAd: no Finland.
- BLEnD: no Finland; factual knowledge.
- CulturalBench: Finland coverage unverified.
- CultureBank: Finland coverage unverified; anecdotal.
- GlobalOpinionQA: 116 Finland questions, WVS opinions only.
- FIN-bench-v2 (https://arxiv.org/abs/2512.13330): mostly translated. It says ARC and GoldenSwag "remain rooted in Anglocentric cultural norms".
- Tao et al.'s 10-item value probe: suits value-level drift, wrong tool for customs.

## 6. Proposed edits to norm-ledger.md (proposals; each needs the operator's approval)

General rule for P3–P7: the operator's decision stays the basis in "What the sites do". New sources are added beside the operator's quotes, never in place of them.

**P1. "How to read it": add a cited frame paragraph after the first paragraph.**
> The frame is consistent with published work. On values surveys, model defaults sit close to Finland (Tao et al. 2024, PNAS Nexus 3(9):pgae346), and Finland is near the US in cultural distance (Muthukrishna et al. 2020: .072). These measure survey values only; they are consistent with the difference lying in customs but do not prove it. A rough test for the level: a moral principle would still hold without any authority requiring it, and everywhere; a custom depends on place and authority (SEP, "The Moral/Conventional Distinction", 2022). Cultures draw that line differently, so a level still needs a basis. Disagreement on a value question is weighed, not settled by one verdict, and that is not relativism (SEP, "Value Pluralism", rev. 2023).

The Walzer thick/thin sentence is left out until the book is opened (**unverified**).

**P2. Add a sentence on what is not a basis, with each claim cited to its own source:**
> A national-character claim ("Finns are quiet") is not a basis; the silent-Finn image has been called an academic myth lacking empirical evidence (Olbertz-Siitonen & Siitonen 2015, Sosiologia 52(4)). A national score from a culture model (Hofstede, GLOBE) is not a basis either: such scores are relative averages and individuals differ (Hofstede FAQ), and variation within cultures exceeds variation between them (Graham et al. 2011; Atari et al. 2023).

Do not use "Finns dislike small talk" as an example sourced to Olbertz-Siitonen; the article covers only the silence myth.

**P3. Row 3: reword the Finnish practice and add bases. The sites' behaviour stays as decided.**

- Finnish practice (the first and third sentences are marked inference):
  > In Finnish news, help information belongs to reporting about suicide, by judgement ("jos uutisen yhteyteen luontevasti sopii"), not to every story that mentions death, violence or illness. Suicide is discussed plainly; it is not a taboo. *[Inference, basis = operator: the same scope applies to study pages, and a student's route to help is the school's own opiskeluhuolto.]*
- Basis: keep the operator's quotes. Add the checklist by media organisations, including JSN, 10.9.2020; MIELI 29.7.2025; Yle 20.8.2025; the OPH opiskeluhuolto page (URLs in §3). The OPH page shows the service exists, not how study materials refer to it.
- Wording fix: separate a "help-block footer" from 112 as subject matter. Replace "no … 112 line … anywhere" with wording that bans the footer, not the teaching of emergency numbers in first-aid and safety content.
- Level: possibly split into *organisational recommendation* (news scope) and *custom/operator decision* (study pages).
- Before finalising, open LOPS 2019 terveystieto and school crisis material for a school-specific basis.

**P4. Row 1: add a basis, two-sided and marked as analogy.**

- University of Helsinki 11.2.2015. Quote the Vehmas line ("…merkityksestä, joka siihen liitetään") **and** the opposing view reported in the same article (a parent: "Kehitysvammaisuus ei määritä häntä").
- The basis cell must state: "disability source; applied to illness by analogy; the article does not discuss person-first constructions."
- Look for a Finnish source on illness words (patient organisations' usage, **unverified**). Keep the operator's quotes.

**P5. Row 4: add supporting evidence, marked as effect, not custom.** Bridgland et al. 2023 via the APS release (secondary). OPH "Psyykkinen turvallisuus" is silent on warnings, which is weak evidence. Keep the operator's quotes.

**P6. Row 7: add bases after checking.**

- Lampinen 1990 (excess politeness read as flattery or irony): open the PDF first, not re-checked.
- Etelämäki et al. 2013 (compliments are plain assessments; abstract only).
- Open LOPS 2019 assessment text before citing it. Keep the operator's quotes.

**P7. Row 8: add a basis after checking.**

- Lampinen 1990 §2.6 (passive and zero person where English uses *you*): open the PDF first.
- Prefer Kielitoimiston ohjepankki or Kielikello entries on calques once opened.
- Add the note "*ole hyvä ja* is native; not a calque". Keep the operator's quotes.

**P8. New rows (wording drafts):**

- **11 (withdrawn as a row) Address on hard topics and prohibitions.** One genre study (Tolvanen 2016), plus counter-evidence on Kela's sinuttelu and on passive overuse. Keep it only as a checker candidate list (§5 item 5). Reconsider once Kotus, Kielitoimiston kielioppiopas, Yli-Vakkuri 1989 and *Saako sinutella vai täytyykö teititellä?* are read.
- **12 Courtesy words.**
  - Model default: politeness added as extra words in English style.
  - Finnish practice: politeness carried largely by grammar (conditional, question forms, clitics, passive).
  - Level: custom. Basis: Lampinen 1990 (not re-checked; open the PDF) and Kielitoimiston kielioppiopas (**unverified**). Hold until one of them is opened.
- **13 National-character claims.**
  - Model default: "Finns are quiet / reserved" taught or used as an explanation.
  - What the sites do: no national-character claims.
  - Level: **house style or guideline rule**, not a Finnish custom and not a research consensus. Supporting source: Olbertz-Siitonen & Siitonen 2015 (abstract).
  - Better as a brief rule (P9) than as a ledger custom.
- **14 dropped** until the 2017 Finnish MFQ paper is opened.

**P9. Brief rule (guideline, not ledger):** briefs give writers the concrete ledger rows, no persona line, and no national-character claims. Basis: Tao et al. 2024; NormAd 2025.

**P10. Optional "Source" column change:** add a strength marker to the Basis cell (primary Finnish institution / academic / operator / inference), so a checker can tell an operator decision from a published source.

**Still to open before citing:**

- Curriculum and law:
  - LOPS 2019 terveystieto objectives
  - LOPS 2019 assessment text
  - oppilas- ja opiskelijahuoltolaki §15 on Finlex
- School and suicide-prevention sources:
  - OPH crisis-preparedness material
  - school crisis plans
  - STM suicide prevention programme 2020–2030
  - the Journalistiliitto/THL pages on the checklist
  - Ylen journalistiset ohjeet
  - WHO/IASP 2023 media PDF ("where to seek help" wording)
  - SAVE recommendations PDF
- Kotus, Kielitoimisto and Selkokeskus:
  - Kielitoimiston ohjepankki
  - Kielikello archive
  - Kielitoimiston kielioppiopas
  - Hyvän virkakielen toimintaohjelma (2014)
  - Suositus virastojen johdolle tekstien selkeyttämisestä
  - Selkokeskus guidance on reader address
- Address research:
  - Yli-Vakkuri 1989
  - *Saako sinutella vai täytyykö teititellä?*
- Linguistics and communication:
  - Lampinen 1990 full text
  - Etelämäki et al. 2013 full text
  - Olbertz-Siitonen & Siitonen 2015 full text
  - Isotalus; Tiittula
- Disability and illness language:
  - APA disability-language page
  - EU Stop-stigma Finnish page (if it teaches person-first, it is a translated EU text)
  - Finnish patient organisations' illness-word usage
- Frames and other research:
  - Mauranen 1993
  - Walzer's book text
  - Wierzbicka 2006
  - CCSARP (Finnish data?)
  - the 2017 Finnish MFQ paper
  - Akaliyski et al. 2025 (JPSP)

Ledger: docs/norm-ledger.md.
