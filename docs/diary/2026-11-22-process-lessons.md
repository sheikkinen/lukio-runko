# Process lessons from the lukio sites (operator's notes, 2026-11-22)

**Date:** 2026-11-22 **IDs:** content guideline v0.4.0 and its watch list; terveystieto D-012; the safety-block decision

## What the operator observed

The operator [O], after the person-first, help-block and repeated-disclaimer findings:

> Dynamic workflows circle back to US cultural habits and English idioms. Ad hoc generated code repeats the current
> idea and readability is poor / code nearly obfuscated. Generated content would require multiple rounds of
> verification.

## What happened

- **Cultural drift.** Across four sites, the workflows kept producing habits from English-language practice: a
  person-first wording rule taught as a Finnish norm, a help block with 112 and crisis lines on almost every page,
  content notes, privacy reassurances and disclaimers stamped on every page, and English sentence rhythm. Each was
  copied forward by the next workflow because the style guides, written by earlier workflows, said so. Checkers checked
  pages against those style guides, so the drift confirmed itself.
- **Ad hoc code.** The quick scripts written during the work (link adders, a repeat counter, inline regex edits)
  encoded the idea of the moment, were hard to read, and had to be patched or rewritten when the idea changed. One
  repeat-counting script used a hand-made keyword list to label what it found, which is interpretation dressed as a
  measurement.
- **Verification load.** Every module needed two or three judge rounds, and the judge itself was sometimes wrong (the
  "arviosi" correction, a sentence a judge asked for that its own source did not state). A single pass was never
  enough.

## Countermeasures now in place or planned

- The shared guideline (`docs/content-guideline.md`): every teaching claim names its basis; a watch list of English
  habits and US-style safety apparatus; ask the operator early on Finnish norms.
- A deterministic repeat check in the engine instead of ad hoc scripts (`docs/repeat-check-plan.md`, being designed):
  hashing or vectors only, no LLM and no keyword meaning, run in every build, with a reviewed allow-list.
- Code that is kept is written as engine code with tests and plain names; throwaway scripts are deleted when done.
- Verification is planned as several rounds by different agents, each checking against the basis, and a native
  speaker's eye (the operator's) for language and cultural norms.

## Heuristic

What a model writes by default is what the English-speaking web does; for Finnish school material, every default is a
claim that needs a Finnish basis.

**Seed:** Should each site's first brief ask the operator for a short list of Finnish norms (wording, safety
practice, tone) before any style guide is written?

**Seed answered** (operator [O], 2026-11-22): "this is context and grounding". The Finnish norms are not a style
preference to collect later; they are the context every brief starts from and the ground every check tests against.
