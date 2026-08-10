# Running the RAGAS demo

**Always cd into this folder first, or the config/script won't be found and the viewer may show a stale result.**

`ANTHROPIC_API_KEY` is exported globally in `~/.zshrc`, so it doesn't need to be set here — just make sure it's a fresh terminal tab (older tabs opened before the key was added won't have it).

```bash
cd ~/faithfulness-evals/ragas
python3 -m venv ../.venv-ragas
source ../.venv-ragas/bin/activate
pip install ragas langchain-anthropic "langchain-community==0.3.31"

python3 ragas_faithfulness.py
```

If a different venv (e.g. `.venv-deepeval`) is already active in this shell, run `deactivate` first, or you'll get a `ModuleNotFoundError`.

`langchain-community` must stay pinned to `0.3.31` (not the latest 0.4.x) — ragas 0.4.3 imports `langchain_community.chat_models.vertexai` directly, and that module was removed in the 0.4.x line as part of the package's "sunset"/deprecation, causing `ModuleNotFoundError: No module named 'langchain_community.chat_models.vertexai'`. If `pip install ragas` or `langchain-anthropic` silently upgrades it back to 0.4.x, re-run `pip install "langchain-community==0.3.31"` to re-pin it.

Expected: GROUNDED ~1.0; HALLUCINATED ~0.333 (one of three claims grounded).

Notes:
- Uses `single_turn_ascore` per sample to avoid the `evaluate()` batch-runner
  hang seen in ragas 0.4.x.
- RAGAS defaults to OpenAI; we wrap `ChatAnthropic` in `LangchainLLMWrapper` to
  use Claude. Deprecation warnings about `LangchainLLMWrapper` and the metric
  import are harmless on 0.4.x.
- Keep RAGAS in its OWN venv — its `langchain-anthropic` dep upgrades `click`
  past what deepeval allows.
