import asyncio 
import json 

from deepeval import evaluate
from deepeval.evaluate import AsyncConfig
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
)
from deepeval.test_case import LLMTestCase

from app.services.retrieval_service import retrieve_documents
from app.services.chat_service import get_chat_response

# EVAL_USER_ID = "dc115685-7906-4388-917f-fb339d79a456"


async def generation_eval(eval_user_id : str, limit: int | None = None):
    with open(
        "app/evals/datasets/research_questions.json",
        "r",
        encoding="utf-8",
    ) as f:
        dataset = json.load(f)

    test_cases = []

    dataset = dataset[:limit]

    for case in dataset:
        print(f"\nRunning{case['id']}")
        print(f"Question: {case['question']}")

        # 1. Retrieve context
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

        # 2. Generate answer
        response = await get_chat_response(
            query=case["question"],
            history=[],
            context=retrieved_chunks,
        )

        actual_output = response.answer

        print("\nGenerated answer:")
        print(actual_output)

        # 3. Create DeepEval test case
        test_case = LLMTestCase(
            input=case["question"],
            actual_output=actual_output,
            retrieval_context=retrieval_context,
        )

        test_cases.append(test_case)

    # 4. Evaluation metrics
    faithfulness_metric = FaithfulnessMetric(
        threshold=0.7,
        include_reason=True,
        model="gpt-4o-mini",
        async_mode=False,
    )

    answer_relevancy_metric = AnswerRelevancyMetric(
        threshold=0.7,
        include_reason=True,
        model="gpt-4o-mini",
        async_mode=False,
    )

    # 5. Run evaluation
    result = evaluate(
        test_cases=test_cases,
        metrics=[
            faithfulness_metric,
            answer_relevancy_metric,
        ],
        async_config=AsyncConfig(
            run_async=False,
        ),
    )

    return {
        "eval_name": "EVAL 3 - Faithfulness & Answer Relevancy",
        "result": result
    }


if __name__ == "__main__":
    asyncio.run(generation_eval())


