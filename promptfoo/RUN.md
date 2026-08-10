# Running the Promptfoo configs

Promptfoo is a Node tool. Use Node 24 and set `ANTHROPIC_API_KEY` only in the
shell where live generator evaluations will run.

```bash
nvm use 24
cd /path/to/faithfulness-evals/promptfoo

# 1) Two-case judge test
npx promptfoo@latest eval -c 01_faithfulness_pass_fail.yaml --no-cache
npx promptfoo@latest view

# 2) 30-case suite (15 grounded PASS, 15 adversarial FAIL -> ~50% by design)
npx promptfoo@latest eval -c 02_faithfulness_suite_20.yaml --no-cache
npx promptfoo@latest view

# 3) Live generator test (3 models, 1 judge; sparse source)
npx promptfoo@latest eval -c 03_generator_test.yaml --no-cache
npx promptfoo@latest view

# 4) Enriched-source controlled experiment (failures should flip to PASS)
npx promptfoo@latest eval -c 04_generator_enriched.yaml --no-cache
npx promptfoo@latest view
```

Notes:
- `echo` provider (01, 02) returns the answer text verbatim so only the judge
  makes model calls. This isolates the scorer.
- Generator providers use the full `anthropic:messages:<model>` id with a
  `config:` block. The bare-string form triggered a "Converting circular
  structure to JSON" serialization bug when the provider had to GENERATE.
- `temperature` is deprecated on Sonnet 5 / Opus 4.x and is silently omitted.
  Harmless.
- The two judge-validation configs use the `echo` provider and do not require
  an API key. The generator configs make live provider calls and do require
  `ANTHROPIC_API_KEY`.
- Promptfoo can return exit code `100` when expected adversarial assertions
  fail. Treat that as an evaluation result, not automatically as an
  infrastructure error.

From the repository root, normalize a Promptfoo JSON result for comparison:

```bash
python3 tools/promptfoo_results.py \
  path/to/promptfoo-output.json \
  results/promptfoo-results.json
```
