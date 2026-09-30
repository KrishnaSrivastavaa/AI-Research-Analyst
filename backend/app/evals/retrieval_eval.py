import asyncio
import json

from deepeval import evaluate
from deepeval.evaluate import AsyncConfig
from deepeval.metrics import (
    ContextualRelevancyMetric,
    ContextualRecallMetric,
    ContextualPrecisionMetric,
)
from deepeval.test_case import LLMTestCase

from app.services.retrieval_service import retrieve_documents


# EVAL_USER_ID = "dc115685-7906-4388-917f-fb339d79a456"


async def retrieval_eval(eval_user_id: str, limit: int | None = None):

    with open(
        "app/evals/datasets/research_questions.json",
        "r",
        encoding="utf-8",
    ) as f:
        dataset = json.load(f)

    test_cases = []

    dataset = dataset[:limit]

    for case in dataset:

        print(f"\nRunning {case['id']}")
        print(f"Question: {case['question']}")

        retrieved_chunks = await retrieve_documents(
            query=case["question"],
            owner_id=eval_user_id,
            document_ids=case["document_ids"],
        )

        retrieval_context = [
            chunk["text"]
            for chunk in retrieved_chunks
        ]

        print(f"Retrieved chunks: {len(retrieval_context)}")

        for index, chunk in enumerate(retrieved_chunks, start=1):
            print(
                f"\n[S{index}] "
                f"chunk_id={chunk['chunk_id']} "
                f"score={chunk['score']}"
            )
            print(chunk["text"][:500])

        test_case = LLMTestCase(
            input=case["question"],
            actual_output="",
            retrieval_context=retrieval_context,
        )

        test_cases.append(test_case)

    metric = ContextualRelevancyMetric(
        threshold=0.7,
        include_reason=True,
        model="gpt-4o-mini",
        async_mode=False,
    )

    result = evaluate(
        test_cases=test_cases,
        metrics=[metric],
        async_config=AsyncConfig(
            run_async=False,
        ),
    )

    return {
        "eval_name": "EVAL 1 - Contextual Relevancy",
        "result": result,
    }


async def retrieval_precision_recall(eval_user_id: str, limit: int | None = None):

    with open(
        "app/evals/datasets/research_questions.json",
        "r",
        encoding="utf-8",
    ) as f:
        dataset = json.load(f)

    test_cases = []

    # TEMPORARY: smoke test with one case only
    dataset = dataset[:limit]

    for case in dataset:

        print(f"\nRunning {case['id']}")
        print(f"Question: {case['question']}")

        retrieved_chunks = await retrieve_documents(
            query=case["question"],
            owner_id=eval_user_id,
            document_ids=case["document_ids"],
        )

        retrieval_context = [
            chunk["text"]
            for chunk in retrieved_chunks
        ]

        reference_evidence = [
            evidence["text"]
            for evidence in case["reference_evidence"]
        ]

        print(f"Retrieved chunks: {len(retrieval_context)}")
        print(f"Reference evidence: {len(reference_evidence)}")

        test_case = LLMTestCase(
            input=case["question"],
            actual_output="",
            expected_output=case["reference_answer"],
            retrieval_context=retrieval_context,
        )

        test_cases.append(test_case)

    precision_metric = ContextualPrecisionMetric(
        threshold=0.7,
        include_reason=True,
        model="gpt-4o-mini",
        async_mode=False,
    )

    recall_metric = ContextualRecallMetric(
        threshold=0.7,
        include_reason=True,
        model="gpt-4o-mini",
        async_mode=False,
    )

    result = evaluate(
        test_cases=test_cases,
        metrics=[
            precision_metric,
            recall_metric,
        ],
        async_config=AsyncConfig(
            run_async=False,
        ),
    )

    return {
        "eval_name": "EVAL 2 - Contextual Precision & Recall",
        "result": result,
    }


if __name__ == "__main__":
    asyncio.run(retrieval_precision_recall(eval_user_id = ""))