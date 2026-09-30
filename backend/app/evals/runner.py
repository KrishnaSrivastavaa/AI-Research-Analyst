import asyncio
import json

from deepeval import evaluate
from deepeval.metrics import ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase

from app.services.retrieval_service import retrieve_documents

from app.evals.retrieval_eval import retrieval_eval, retrieval_precision_recall


EVAL_USER_ID = "dc115685-7906-4388-917f-fb339d79a456"


async def main():
    # await retrieval_eval()
    await retrieval_precision_recall()

    


if __name__ == "__main__":
    asyncio.run(main())