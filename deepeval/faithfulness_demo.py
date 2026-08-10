"""
DeepEval faithfulness demo: grounded vs hallucinated.

Tests the JUDGE, not a generator. We supply a known-good answer and a
known-bad answer, and check that the faithfulness metric scores them correctly.

Run:  python3 faithfulness_demo.py
Needs: ANTHROPIC_API_KEY in the environment.
"""
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric
from deepeval.models import AnthropicModel

judge = AnthropicModel(model="claude-sonnet-4-6", temperature=0)

context = [
    "ST elevation in leads II, III, and aVF indicates an inferior wall MI, "
    "most commonly caused by occlusion of the right coronary artery (RCA)."
]

grounded = LLMTestCase(
    input="55-year-old, chest pain, ST elevation in II, III, aVF. Diagnosis and cause?",
    actual_output="Inferior wall myocardial infarction, most commonly caused by "
                  "occlusion of the right coronary artery.",
    retrieval_context=context,
)

hallucinated = LLMTestCase(
    input="55-year-old, chest pain, ST elevation in II, III, aVF. Diagnosis and cause?",
    actual_output="Inferior wall MI, most commonly caused by occlusion of the left "
                  "anterior descending (LAD) artery, and it should be treated with "
                  "thrombolytics within 90 minutes.",
    retrieval_context=context,
)

metric = FaithfulnessMetric(threshold=0.9, model=judge, include_reason=True)

for name, tc in [("GROUNDED", grounded), ("HALLUCINATED", hallucinated)]:
    metric.measure(tc)
    print(f"\n=== {name} ===")
    print("score :", metric.score)
    print("passed:", metric.is_successful())
    print("reason:", metric.reason)
