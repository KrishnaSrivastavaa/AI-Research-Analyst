import asyncio
import json

import httpx
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.models import ConversationDoc, Conversation


# EVAL_USER_ID = "dc115685-7906-4388-917f-fb339d79a456"

BASE_URL = "http://127.0.0.1:8000/api/v1/chat"

# ACCESS_TOKEN = "..."

DATASET_PATH = (
    "app/evals/datasets/research_questions.json"
)


async def get_conversation_id(
    document_id: int,
    eval_user_id: str,
) -> int | None:
    """
    Find the conversation associated with a document
    for the evaluation user.

    The ConversationDoc table stores the relationship
    between conversations and documents.
    """

    async with SessionLocal() as db:

        result = await db.scalar(
            select(ConversationDoc.conversation_id)
            .join(
                Conversation,
                Conversation.id == ConversationDoc.conversation_id,
            )
            .where(
                ConversationDoc.document_id == document_id,
                Conversation.user_id == eval_user_id,
            )
        )

        return result


async def e2e_eval(
    eval_user_id: str,
    access_token: str,
    limit: int | None = None,
):

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        dataset = json.load(f)

    dataset = dataset[:limit]

    case_results = []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers=headers,
        timeout=120.0,
    ) as client:

        for case in dataset:

            print("\n" + "=" * 60)
            print(f"Running {case['id']}")
            print(f"Question: {case['question']}")
            print("=" * 60)

            # -----------------------------------------
            # 1. Get document ID from dataset
            # -----------------------------------------

            document_ids = case["document_ids"]

            if len(document_ids) != 1:

                print(
                    "\nSkipping case because this E2E "
                    "evaluation currently expects one "
                    "document per question."
                )

                case_results.append(
                    {
                        "question_id": case["id"],
                        "document_id": None,
                        "conversation_id": None,
                        "http_status": None,
                        "answer_present": False,
                        "grounded": None,
                        "citation_count": 0,
                        "checks": {},
                        "passed": False,
                        "error": (
                            "E2E evaluation currently expects "
                            "one document per question"
                        ),
                    }
                )

                continue

            document_id = document_ids[0]

            print(
                f"\nDocument ID: "
                f"{document_id}"
            )

            # -----------------------------------------
            # 2. Find conversation for document
            # -----------------------------------------

            conversation_id = await get_conversation_id(
                document_id=document_id,
                eval_user_id=eval_user_id,
            )

            if conversation_id is None:

                print(
                    f"\nNo conversation found for "
                    f"document {document_id}."
                )

                case_results.append(
                    {
                        "question_id": case["id"],
                        "document_id": document_id,
                        "conversation_id": None,
                        "http_status": None,
                        "answer_present": False,
                        "grounded": None,
                        "citation_count": 0,
                        "checks": {},
                        "passed": False,
                        "error": (
                            f"No conversation found for "
                            f"document {document_id}"
                        ),
                    }
                )

                continue

            print(
                f"Conversation ID: "
                f"{conversation_id}"
            )

            # -----------------------------------------
            # 3. Send request through actual API
            # -----------------------------------------

            response = await client.post(
                f"/conversations/"
                f"{conversation_id}/messages",
                json={
                    "query": case["question"],
                },
            )

            print(
                f"\nHTTP status: "
                f"{response.status_code}"
            )

            if response.status_code != 200:

                print("\nAPI error:")
                print(response.text)

                case_results.append(
                    {
                        "question_id": case["id"],
                        "document_id": document_id,
                        "conversation_id": conversation_id,
                        "http_status": response.status_code,
                        "answer_present": False,
                        "grounded": None,
                        "citation_count": 0,
                        "checks": {
                            "http_success": False,
                            "answer_present": False,
                            "grounded_present": False,
                        },
                        "passed": False,
                        "error": response.text,
                    }
                )

                continue

            result = response.json()

            # -----------------------------------------
            # 4. Print API response
            # -----------------------------------------

            print("\nAPI response:")

            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            # -----------------------------------------
            # 5. Inspect answer
            # -----------------------------------------

            answer = result.get("answer")

            print("\nGenerated answer:")
            print(answer)

            # -----------------------------------------
            # 6. Inspect grounding
            # -----------------------------------------

            grounded = result.get("grounded")

            print(
                f"\nGrounded: "
                f"{grounded}"
            )

            # -----------------------------------------
            # 7. Inspect citations
            # -----------------------------------------

            citations = result.get(
                "citations",
                [],
            )

            print(
                f"\nCitations returned: "
                f"{len(citations)}"
            )

            for citation in citations:

                print(
                    f"\n[{citation['id']}] "
                    f"document_id="
                    f"{citation['document_id']} "
                    f"document="
                    f"{citation['document_name']} "
                    f"pages="
                    f"{citation['page_start']}-"
                    f"{citation['page_end']}"
                )

            # -----------------------------------------
            # 8. Basic E2E checks
            # -----------------------------------------

            checks = {
                "http_success": (
                    response.status_code == 200
                ),
                "answer_present": bool(answer),
                "grounded_present": (
                    grounded is not None
                ),
            }

            case_results.append(
                {
                    "question_id": case["id"],
                    "document_id": document_id,
                    "conversation_id": conversation_id,
                    "http_status": response.status_code,
                    "answer_present": bool(answer),
                    "grounded": grounded,
                    "citation_count": len(citations),
                    "checks": checks,
                    "passed": all(checks.values()),
                    "error": None,
                }
            )

            print("\nE2E checks:")

            for check_name, passed in checks.items():

                status = (
                    "PASS"
                    if passed
                    else "FAIL"
                )

                print(
                    f"{check_name}: "
                    f"{status}"
                )

    # -----------------------------------------
    # 9. Return evaluation results
    # -----------------------------------------

    return {
        "eval_name": "EVAL 5 - End-to-End",
        "total_cases": len(dataset),
        "executed_cases": len(case_results),
        "passed_cases": sum(
            1
            for case in case_results
            if case["passed"]
        ),
        "cases": case_results,
    }


if __name__ == "__main__":
    asyncio.run(
        e2e_eval(
            eval_user_id="",
            access_token="",
        )
    )