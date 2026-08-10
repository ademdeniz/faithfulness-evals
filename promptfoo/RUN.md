# Running the Promptfoo configs

**Always cd into this folder first, or the config/script won't be found and the viewer may show a stale result.**

Promptfoo is a Node tool. Node 22 was too old for recent versions; use Node 24.

`ANTHROPIC_API_KEY` is exported globally in `~/.zshrc`, so it doesn't need to be set here — just make sure it's a fresh terminal tab (older tabs opened before the key was added won't have it).

```bash
nvm use 24
cd ~/faithfulness-evals/promptfoo

# 1) Two-case judge test
npx promptfoo@latest eval -c 01_faithfulness_pass_fail.yaml --no-cache
npx promptfoo@latest view

# 2) 20-case suite (10 grounded PASS, 10 adversarial FAIL -> ~50% by design)
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
