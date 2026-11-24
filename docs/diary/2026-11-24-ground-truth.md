# 2026-11-24: who is the ground truth

A pilot had Haiku review nine visual-novel chapters against their site pages, once as a Finnish student persona and
once with an explicit criteria list (`docs/research/2026-11-24-vn-review-pilot/`). A Sonnet check called 80–85% of
the 201 comments valid; a strict judge and a skeptic left 28 must-change points. The operator's reading: the list is
an actionable size, but the points are "close to opinions - can be decided either way", and need manual checking.

Then, on the proposed feedback loops: "you rely too much on me as the ground truth." Three of the ten proposals
measured the process against the operator's own verdicts.

What changed: every check now names its ground truth before it is proposed, and the ones that need no human verdict
come first (`docs/feedback-loops-plan.md`). About half of the 28 points were help lines and added services that a set
comparison between chapter and page finds without any model; the rest are claims, where planted defects can at least
measure how often a model reviewer catches them.

**Trap:** treating a model's "valid" or "must" as a finding, and the operator as the only check on it. Both make the
operator the bottleneck and the process unable to learn by itself.

**Heuristic:** ask "measured against what?" before "reviewed by whom?". A page, a lexicon, an exam description, a
planted defect or a hash answers without anyone's opinion.

**Seed:** if planted defects show a model reviewer's recall per defect type, which defect types could stop going to
the operator at all, and which can never leave a human (norms with no outside source)?
