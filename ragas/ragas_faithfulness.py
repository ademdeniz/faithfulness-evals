"""
RAGAS faithfulness demo: grounded vs hallucinated.

Uses single_turn_ascore to score one sample at a time, which sidesteps the
batch-runner hang seen in ragas 0.4.x. Judge is Claude (RAGAS defaults to
OpenAI, so we wrap ChatAnthropic to override it).

Run:  python3 ragas_faithfulness.py
Needs: ANTHROPIC_API_KEY in the environment.
"""
import asyncio
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import Faithfulness
from ragas.llms import LangchainLLMWrapper
from langchain_anthropic import ChatAnthropic

llm = LangchainLLMWrapper(ChatAnthropic(model="claude-sonnet-4-6", temperature=0))
scorer = Faithfulness(llm=llm)

context = [
    "ST elevation in leads II, III, and aVF indicates an inferior wall MI, "
    "most commonly caused by occlusion of the right coronary artery (RCA)."
]

grounded = SingleTurnSample(
    user_input="55-year-old, chest pain, ST elevation in II, III, aVF. Diagnosis and cause?",
    response="Inferior wall myocardial infarction, most commonly caused by "
             "occlusion of the right coronary artery.",
    retrieved_contexts=context,
)

hallucinated = SingleTurnSample(
    user_input="55-year-old, chest pain, ST elevation in II, III, aVF. Diagnosis and cause?",
    response="Inferior wall MI, most commonly caused by occlusion of the left "
             "anterior descending artery, treated with thrombolytics within 90 minutes.",
    retrieved_contexts=context,
)

async def main():
    g = await scorer.single_turn_ascore(grounded)
    h = await scorer.single_turn_ascore(hallucinated)
    print("\n=== RAGAS Faithfulness ===")
    print("GROUNDED     :", round(g, 3))
    print("HALLUCINATED :", round(h, 3))

asyncio.run(main())
