# Running the DeepEval demo

**Always cd into this folder first, or the config/script won't be found and the viewer may show a stale result.**

`ANTHROPIC_API_KEY` is exported globally in `~/.zshrc`, so it doesn't need to be set here — just make sure it's a fresh terminal tab (older tabs opened before the key was added won't have it).

```bash
cd ~/Desktop/faithfulness-evals/deepeval
python3 -m venv .venv-deepeval
source .venv-deepeval/bin/activate
pip install deepeval anthropic

python3 faithfulness_demo.py
```

If a different venv (e.g. `.venv-ragas`) is already active in this shell, run `deactivate` first, or you'll get `ModuleNotFoundError: No module named 'deepeval'`.

Expected: GROUNDED scores 1.0 and passes; HALLUCINATED scores ~0.5 and fails
(one of two claims grounded). The metric is an LLM call — DeepEval defaults to
OpenAI, so we pass `model=AnthropicModel(...)` to use Claude as the judge.

Uses `.measure()` directly (not `assert_test`) so both cases run and print
instead of pytest aborting on the first failure.
