# Faithfulness Evals: Promptfoo, DeepEval, RAGAS

A hands-on project for evaluating the faithfulness of LLM-generated medical content, built to understand LLM evaluation from the inside rather than from documentation. The same faithfulness check is implemented three ways (Promptfoo, DeepEval, RAGAS), then extended into a live multi-model comparison and a controlled experiment that isolates why answers fail.

Every judge in this repo is Claude (Anthropic). All three frameworks default to OpenAI, so pointing them at Claude is a deliberate configuration step in each one, documented below.

## What "faithfulness" means (and what it does not)

**Faithfulness** = does every claim in an answer trace back to the provided source material?

The critical distinction, and the throughline of this whole project: faithfulness is not the same as being true in general.

- An answer can be medically correct but unfaithful if it adds facts the source never stated.
- An answer can be faithful but useless if the source itself was wrong.

Faithfulness measures grounding in the source, nothing more. In a retrieval-augmented (RAG) medical product, this is exactly the property you want to test, because the danger isn't only "the model made something up," it's "the model stated something that isn't backed by the reviewed source material a clinician approved."

This is why faithfulness is a retrieval-plus-generation metric: it only has meaning relative to the source you give it. Change the source, and the same answer can flip from unfaithful to faithful. `04` in this repo proves that directly.

## How faithfulness is actually scored

None of these frameworks do a string match. Each one runs an LLM judge that:

1. Decomposes the answer into individual atomic claims.
2. Verifies each claim against the source material.
3. Scores the ratio: supported claims / total claims.

That ratio is why the same wrong answer can score differently across tools: each framework's judge splits the answer into a different number of claims. In this project the identical hallucinated answer scored 0.5 in DeepEval and 0.333 in RAGAS, not because one is wrong, but because claim decomposition is itself a judgment call and the two judges chunked the sentence differently.

Practical consequence, and the rule this project operates by: don't chase the exact decimal. Set a high threshold for medical content, and act on which claim the judge flags as unsupported, not on whether the score was 0.33 or 0.50.

## The three actors, and the two things being tested

Every eval has three actors:

| Actor | Role |
|---|---|
| Generator | the model that writes the answer |
| Output | the answer itself (faithful or not) |
| Judge / scorer | reads the output and rules PASS / FAIL |

This repo tests two different things, and keeping them straight is the whole skill:

### 1. Testing the JUDGE (`01`, `02`, and both `.py` demos)

We supply answers whose correct verdict we already know, and check the judge sorts them correctly.

- Grounded answers stay inside the source and should PASS (positive test cases).
- Adversarial answers deliberately break grounding and should FAIL (negative test cases).

Promptfoo's `echo` provider passes our handwritten answers straight through, so no model generates anything. The generator is removed from the loop entirely. The only question is: does the judge's verdict match the label I defined?

You're testing the test. This is the step most people skip, and it's the one that earns trust in every score that comes after.

### 2. Testing the GENERATOR (`03`, `04`)

Now the judge is fixed and trusted, real models generate answers live, and we measure the models. The roles flip: same metric, opposite thing under test.

In Promptfoo terms: the `providers:` list is the lineup of contestants, and the single `llm-rubric` provider is the one referee grading all of them. One judge, many generators, held constant so the comparison is fair.

## Repository layout

```
faithfulness-evals/
├── promptfoo/
│   ├── 01_faithfulness_pass_fail.yaml   # 2-case judge test (echo provider)
│   ├── 02_faithfulness_suite_20.yaml    # 20-case suite: 10 grounded, 10 adversarial
│   ├── 03_generator_test.yaml           # 3 live models graded by 1 judge (sparse source)
│   ├── 04_generator_enriched.yaml       # same as 03 but enriched source (controlled experiment)
│   └── RUN.md
├── deepeval/
│   ├── faithfulness_demo.py             # grounded vs hallucinated, claim-decomposition scores
│   └── RUN.md
├── ragas/
│   ├── ragas_faithfulness.py            # grounded vs hallucinated, single_turn_ascore
│   └── RUN.md
├── requirements.txt
└── README.md
```

## The 20-case suite (`02`) explained

The suite is deliberately 10 grounded + 10 adversarial, so a ~50% pass rate is by design. Rows 1-10 should be green; rows 11-20 should be red. Any row that disagrees with its label is a finding about the judge, not a bad result.

The 10 adversarial cases each encode a different hallucination type, so the suite tests breadth of detection, not just one failure:

| # | Hallucination type | Example |
|---|---|---|
| 11 | Direct contradiction | artery swap RCA to LAD |
| 12 | Fabricated addition | invented dose "10 units, dialysis in 30 min" |
| 13 | Overgeneralization | "always cures heart failure in every patient" |
| 14 | Wrong drug | epinephrine to diphenhydramine |
| 15 | Invented dose/target | "target INR of exactly 5.0 for all patients" |
| 16 | Invented mechanism | "directly rupturing hepatocyte cell membranes" |
| 17 | Swapped lab values | microcytic/low to macrocytic/high |
| 18 | Unsupported absolute | "completely safe, no side effects in any patient" |
| 19 | Conflated conditions | atrial fibrillation described as flutter |
| 20 | Out-of-scope fabrication | "coronary artery bypass surgery" for DKA |

## Key findings from the runs

- **Faithfulness is claim-decomposition, not a vibe check.** Scores are supported-claims / total-claims. The same hallucinated answer scored 0.5 (DeepEval) and 0.333 (RAGAS) because the judges decomposed it into different numbers of claims. The takeaway is to act on the flagged claim, not the decimal.

- **A more capable model can score worse on grounding.** In `03`, given a sparse source and a strict "use only the source" prompt, the larger models failed cases the terse model passed, because they added true but unsourced detail (e.g. "the RCA supplies the inferior wall of the left ventricle"). That's medically correct and not in the source, so a grounding metric correctly marks it unfaithful. Helpful elaboration is punished by a strict faithfulness check. This is counterintuitive and worth internalizing: "best model" is not a fixed property, it depends on what you're measuring.

- **The failures were unsourced-elaboration, proven by controlled experiment.** `04` is identical to `03` except the sources are enriched to contain exactly the detail the models were adding. One variable changed. The previously-failing cases flip to PASS, confirming the earlier failures were elaboration beyond the source, not fabrication. Same model, same prompt, same judge, different source, opposite verdict.

- **ERROR is not FAIL.** During development an all-ERROR run (a provider serialization bug, and separately a stale viewer showing a cached result) looked at a glance like passing/failing tests. It wasn't; the harness hadn't run. An all-error run means fix your setup; an all-fail run means interrogate the model. Conflating the two sends you debugging the wrong layer. The habit this built: never trust a result you didn't watch execute fresh (`--no-cache`).

- **Whether elaboration passes or fails is a POLICY decision, not a technical one.** If the rule is "explanations may only state what's in the reviewed source," failing the elaborations is correct. If the rule is "explanations should be accurate and may add helpful context," the rubric is too strict. That line has to be set by product and clinical reviewers, not QA alone. The eval encodes a policy; it doesn't invent it.

- **The tooling is OpenAI-first.** All three frameworks defaulted to OpenAI and had to be explicitly pointed at Claude (DeepEval via `AnthropicModel`, Promptfoo via `provider: anthropic:...`, RAGAS via a `LangchainLLMWrapper` around `ChatAnthropic`). Provisioning the judge is a real setup decision, not an afterthought, and it's the same friction in every framework.

## Framework comparison

| | Promptfoo | DeepEval | RAGAS |
|---|---|---|---|
| Language | Node (YAML config) | Python (pytest-style) | Python |
| Faithfulness output | binary PASS/FAIL (rubric) | graded score + claim reasons | graded score |
| Source handling | inject `{{source}}` into rubric | `retrieval_context` first-class | `retrieved_contexts` first-class |
| Best for | fast CI, config-driven suites | detailed per-claim scoring | RAG-specific metric suite |
| Judge default | OpenAI (override to Claude) | OpenAI (override to Claude) | OpenAI (override to Claude) |

A note on why hand-rolled rubrics are risky: an early Promptfoo faithfulness rubric failed to grade correctly because the judge couldn't see the source — the `{{source}}` variable wasn't injected into the rubric text, so the judge refused to certify groundedness it couldn't check. That's the exact problem `retrieval_context` (DeepEval) and `retrieved_contexts` (RAGAS) solve by design: they pass the source to the judge as structured input. Lesson: a faithfulness scorer must be given the source, or it isn't measuring faithfulness.

## Setup

Per-framework run steps are in `promptfoo/RUN.md`, `deepeval/RUN.md`, and `ragas/RUN.md`. Highlights:

- Node 24+ is required for Promptfoo (Node 22 is rejected).
- DeepEval and RAGAS conflict on the `click` version if installed in the same virtualenv. Use a separate venv per framework.
- All scripts require `ANTHROPIC_API_KEY` in the environment:

  ```bash
  export ANTHROPIC_API_KEY=sk-ant-...
  ```

- Always `cd` into the relevant subfolder before running, and use `--no-cache` with Promptfoo to guarantee a fresh run rather than a cached result.

## What this project demonstrates

- Building faithfulness evals across three frameworks and reconciling their differences.
- Validating the judge on known-label cases before trusting it to grade live model output.
- Designing an adversarial suite that covers distinct hallucination types.
- Comparing models on a grounding metric and interpreting a counterintuitive result.
- Running a controlled experiment to isolate the cause of failures.
- Distinguishing harness errors from genuine eval failures.
- Recognizing where a technical metric ends and a content-policy decision begins.

## Author

Adem Garic — Senior SDET / QA Engineer

## License

All rights reserved. See [LICENSE](LICENSE).
