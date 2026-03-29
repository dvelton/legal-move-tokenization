# Legal Move Tokenization

## What We Found

Legal briefs contain a strategic layer that operates beneath the words on the page. When a lawyer writes a paragraph of argument, they aren't just stating the law. They're narrowing a precedent's scope, burying an unfavorable fact in a dependent clause, delivering the most damaging point in calm language, and conceding a weak point to pivot to a stronger one. These are strategic *moves*, and they're identifiable, consistent, and catalogable.

We built a taxonomy of ~47 distinct moves organized across four layers: doctrinal (what legal reasoning operation is being performed), narrative (what structural strategy is being deployed), fact-framing (what's being emphasized, buried, or recharacterized), and stylistic (how the point is delivered for rhetorical effect). We annotated 22 SCOTUS adversarial brief pairs and found that the same moves appear regardless of legal domain. A copyright case, a retirement plan dispute, a state sovereignty question, and a DNA testing case all use the same strategic operations in different combinations.

In a full pipeline test tracing moves from briefs through oral argument to the Court's opinion, move-level annotations predicted which arguments the Court adopted with high accuracy. Moves that drew favorable questions at oral argument were adopted in the majority opinion. Moves that drew skeptical questions were rejected. Moves that were ignored at argument were ignored in the opinion.

One finding we didn't expect: fact-framing moves (which facts you foreground, which you bury, what language you use to describe the same event) may have disproportionate impact relative to their apparent analytical weight. In the pipeline case, the choice of which clock to run for a timeliness argument (10 days from a triggering event vs. years of prior litigation) was arguably the single most effective move in the entire case. It didn't cite new authority or propose new doctrine. It just made one side's story feel obvious.

## Why This Matters

Current legal AI operates at the text level. It predicts words, classifies paragraphs, and summarizes holdings. It misses the strategic layer entirely.

Existing annotation schemes like IRAC (Issue, Rule, Application, Conclusion) tell you *what a paragraph is*. Move annotation tells you *what a paragraph is doing*. Consider the difference: IRAC labels a paragraph as "analysis." Move annotation tells you that paragraph is narrowing a precedent's scope while conceding a weak point and delivering the conclusion in understated language for maximum impact. The paragraph is executing three strategic operations simultaneously across three different layers.

This is analogous to the difference between part-of-speech tagging (this word is a noun) and semantic role labeling (this noun is the agent performing the action). Both are useful. The latter captures far more about meaning and intent.

The taxonomy could enable:

- Strategic brief analysis tools that go beyond text classification
- Move-conditioned text generation (produce a paragraph that narrows a holding while anchoring it in a concrete fact)
- Empirical study of advocacy effectiveness (which move combinations predict Court adoption?)
- Judicial behavior research (which justices respond to which move types?)
- Cross-domain persuasion analysis (do the same moves appear in legislative debate, regulatory comments, or competitive debate?)

## The Taxonomy

The full taxonomy is in [`taxonomy.json`](taxonomy.json). Here's what each layer covers, with examples drawn from the SCOTUS annotations.

### Doctrinal Layer (19 moves)

Legal reasoning operations. What doctrinal work is the paragraph doing?

- NARROW_HOLDING: Confine what a precedent stands for. In *Hughes v. Northwestern* (19-1401), the respondent narrowed *Tibble v. Edison* to argue it only required monitoring, not the specific monitoring the petitioner demanded.
- DISTINGUISH: Show why a cited case doesn't apply. In *Cameron v. EMW* (20-601), the petitioner distinguished the respondent's reliance on *Torres v. Madrid* by arguing the AG was a non-party intervenor, not a party who failed to appeal.
- SLIPPERY_SLOPE: Argue the opponent's rule would produce unacceptable downstream consequences. In 20-601, the respondent warned that allowing late intervention would let state officers "spring to action" whenever a court of appeals issued unfavorable decisions. The majority ignored this argument entirely.
- JURISDICTIONAL_REFRAME: Swap the entire governing legal framework rather than adjusting one rule's scope. The respondent in 20-601 tried to recategorize a discretionary timeliness question as a mandatory jurisdictional bar. It received zero votes.

### Narrative Layer (11 moves)

Story structure and argumentative strategy.

- CONCEDE_AND_REDIRECT: Acknowledge a weak point, then pivot to why it doesn't matter. Both sides in 20-601 used this as their transition to alternative arguments ("even if sovereignty doesn't apply, we still win on timeliness").
- AGREEMENT_TRAP: Use the opponent's own procedural concession to foreclose a substantive position.
- DILEMMA_CONSTRUCTION: Frame the opponent's position as a lose-lose regardless of which path they take.
- STRATEGIC_SHIFT_EXPOSURE: Document the opponent's change in theory between stages of litigation. In 22-96, petitioner used "That is disingenuous" (two words, maximum force) after documenting the respondent's reversal on arm-of-state status between the lower court and certiorari.

### Fact-Framing Layer (11 moves)

How facts are selected, ordered, and characterized.

- FOREGROUND / BACKGROUND: Lead with favorable facts; bury unfavorable ones in dependent clauses or footnotes. In 20-601, petitioner foregrounded the 10-day response time while respondent foregrounded years of prior litigation. Same timeline, opposite stories.
- RECHARACTERIZE: Describe the same event using different framing language. Petitioner said the AG wanted to "fight on" and "pick up the mantle." Respondent said the AG was attempting an "end-run" and trying to "circumvent" the rules. The majority adopted petitioner's characterization.
- SILENCE_AS_CONCESSION: Convert the opponent's failure to contest a point into a tacit admission.
- ACCUMULATION_OVERWHELM: Stack multiple supporting facts in rapid succession to create cumulative weight.

### Stylistic Layer (10 moves)

How the move is delivered for rhetorical effect.

- UNDERSTATED_DEVASTATION: Deliver the most damaging point in calm, clinical language. In 22-96, "That is disingenuous" did more work as a two-word sentence than a paragraph of argument would have.
- COMPRESSION: Say in one sentence what the opponent took a paragraph to say. Signals confidence.
- CADENCE_SHIFT: Follow a complex, heavily cited passage with a short declarative sentence for emphasis.
- AUTHORITY_INVERSION: Capture an opponent's cited authority and deploy it for the opposite proposition.

### Validation

The taxonomy was validated across 22 cases. New moves were discovered during annotation (the initial vocabulary had 30 moves; 17 more emerged through the annotation process). Discovery effectively stopped after ~10 cases. 77% of cases needed zero new moves. Only 2 singleton moves (appearing in just 1 case) exist in the final taxonomy, which suggests it generalizes well across legal domains.

## How We Built It

### Data source

The [BriefMe dataset](https://huggingface.co/datasets/jw4202/BriefMe) on HuggingFace, which contains preprocessed SCOTUS briefs (CC-BY-4.0 license).

### Annotation method

AI-assisted annotation with human expert validation. For each adversarial brief pair, argument sections were extracted and annotated at the paragraph level across all four layers. The AI generated initial annotations, and a legal expert reviewed and corrected them. Corrections fed back into taxonomy refinement.

### Scale

- 22 adversarial brief pairs annotated
- 374 argument units across those pairs
- 2,073 move annotations (multiple moves per argument unit across layers)
- Cases spanning copyright, ERISA, state sovereignty, securities law, patent enablement, Fourth Amendment, Takings Clause, Puerto Rico sovereign immunity, anti-terrorism liability, and more

### Taxonomy convergence

The taxonomy started at 30 moves. The first few cases generated significant new discoveries (7 moves from the first 2 cases alone). Discovery slowed sharply: the last 6 cases averaged fewer than 1 new move per case. 77% of all cases needed zero new moves after the initial discovery phase.

### Pipeline trace

A full pipeline trace on *Cameron v. EMW Women's Surgical Center* (20-601) connected briefing moves to oral argument engagement to opinion adoption. The case was an 8-1 reversal (Alito, J., majority), and the trace tracked each major move from both briefs through 238 turns of oral argument and into the final opinion, concurrences, and dissent. See [`analysis/deep_pipeline_20-601.txt`](analysis/deep_pipeline_20-601.txt) for the full analysis.

## Key Findings

### Layer coverage

All four layers proved productive across the dataset:

- Doctrinal: 97% of argument units had an identifiable doctrinal move
- Stylistic: 94%
- Narrative: 93%
- Fact-framing: 87%

The relatively lower coverage for fact-framing makes sense. Not every paragraph of legal argument involves a fact-selection choice. Some are pure doctrinal operations.

### Move distribution

The move frequency distribution follows a power law, which matches how natural language vocabularies distribute:

- Top 5 moves account for ~30% of all applications
- Top 10 moves account for ~50%
- A long tail of less common but real moves fills out the rest

11 "universal" moves appeared in 86% or more of all cases regardless of legal domain. Only 2 moves were singletons (appearing in just 1 case).

### Pipeline findings from 20-601

The deep pipeline trace produced several results worth testing at scale:

- Oral argument engagement predicted opinion adoption. Every petitioner move that received favorable engagement from multiple justices was adopted in the majority. Every respondent move that received primarily skeptical engagement was rejected. The respondent's most ignored argument (slippery slope) was completely absent from the majority opinion.
- Kagan's concurrence showed that fact-framing and doctrinal moves can travel independently through the pipeline. She rejected the petitioner's constitutional sovereignty framing (the doctrinal move) but adopted the petitioner's factual narrative (the 10-day timeline, the "changed circumstances" story). A justice can decline your legal theory while accepting the facts the way you presented them.
- The respondent's most analytically ambitious move (JURISDICTIONAL_REFRAME, a novel attempt to recategorize the dispute as jurisdictional rather than discretionary) received zero votes. It was the creative high-risk move, and it failed completely. The respondent's more conventional argument (abuse of discretion) at least got Sotomayor's dissent.
- Fact-framing operated as a force multiplier. The competing clocks (10 days vs. 30 days) and competing characterizations ("fight on" vs. "end-run") didn't involve new authority or doctrine. They selected which facts to foreground. These choices appear to have had outsized influence relative to their doctrinal content.

## Game-Theoretic Model

Legal briefing is a three-player persuasion game, not a two-player contest. Two informed adversaries perform for a third party (the court) whose preferences are only partially known. Both sides know the facts and law. Neither side knows exactly how the court will weigh competing considerations.

This structure shapes everything about move selection:

- Briefs are multi-targeted. Different sections aim at different justices: holding friendly votes, persuading swing votes, preempting hostile reasoning.
- Chess (deterministic) and poker (probabilistic) elements coexist throughout. The law on a multi-factor test may be clear, but whether the court will actually apply it your way depends on preferences you can't fully observe.
- The adversarial dimension becomes progressively more chess-like over the briefing sequence (opening brief, response, reply), as each stage reveals more about the opponent's strategy. But the audience dimension stays poker-like throughout. You never get full information about how the court will process what it's heard.

See [`docs/GAME_THEORY.txt`](docs/GAME_THEORY.txt) for the full framework, including discussion of amicus briefs as coalition signals and oral argument as mid-game information revelation.

## Repo Structure

```
legal-move-tokenization/
├── taxonomy.json              # Full move taxonomy (47 moves, 4 layers, v0.3)
├── analysis/
│   ├── analyze.py             # Analysis script: convergence, distribution, coverage tests
│   └── deep_pipeline_20-601.txt  # Full pipeline trace: briefs → oral argument → opinion
├── data/
│   ├── annotations/           # Move annotations for 22 cases (374 argument units)
│   ├── briefs/                # Extracted argument sections from petitioner/respondent briefs
│   ├── metadata/              # Case metadata and brief pairing information
│   ├── opinions/              # Opinion text for pipeline cases
│   └── oral-arguments/        # Oral argument transcripts for pipeline cases
├── docs/
│   ├── FRAMEWORK.txt          # Research framework and methodology
│   ├── GAME_THEORY.txt        # Game-theoretic model of legal briefing
│   └── VALIDATION_PLAN.txt    # Validation tests and failure conditions
└── LICENSE                    # MIT (code) + CC-BY-4.0 (data/annotations)
```

## Data Sources

- [BriefMe dataset](https://huggingface.co/datasets/jw4202/BriefMe) (SCOTUS briefs, CC-BY-4.0)
- [Oyez Project](https://www.oyez.org) (oral argument transcripts)
- [Cornell LII](https://www.law.cornell.edu) (opinion text)
- Supreme Court Database (SCDB) for case metadata

## Limitations and Open Questions

- Single annotator (AI) with limited human expert validation. Inter-annotator agreement has not been formally measured. The annotations need independent human coding on a subset to establish reliability.
- 22 cases is enough to validate the taxonomy (convergence test shows stabilization), but it's marginal for predictive claims. The power-law distribution finding is plausible but should be confirmed with more data.
- Only one full pipeline trace (20-601). That case was an 8-1 decision, which limits what it can tell us about marginal effectiveness. Cases with closer margins (5-4, 6-3) would be more informative. 20-30 pipeline traces are needed for statistical power.
- The taxonomy was built on SCOTUS appellate briefing. It may not fully generalize to trial court motions, state appellate practice, or international jurisdictions. The four-layer structure should transfer, but specific moves may be SCOTUS-specific.
- Some moves discovered during annotation (particularly in the later cases) may be subtypes of existing moves rather than genuinely distinct operations. A hierarchical taxonomy (move families with subtypes) might be more accurate than the current flat list.

## Building on This

The annotated dataset, taxonomy, and methodology are all available in this repo.

Researchers could extend this in several directions: apply the taxonomy to additional cases or lower courts, build move-aware classifiers, train sequence models on move tokens, or test whether move-level representations predict outcomes better than text-level baselines.

The four-layer framework (doctrinal, narrative, fact-framing, stylistic) and the annotation approach could transfer to any domain with adversarial persuasion. Legislative floor debates, regulatory notice-and-comment proceedings, competitive debate, and diplomatic negotiations all involve strategic actors making identifiable moves aimed at specific audiences. The vocabulary would change. The structure probably wouldn't.

## License

MIT for code. CC-BY-4.0 for annotations and data, matching the BriefMe source dataset license.
