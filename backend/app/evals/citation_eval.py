import asyncio
import json
from typing import Any

from app.services.retrieval_service import retrieve_documents
from app.services.chat_service import get_chat_response


# EVAL_USER_ID = "dc115685-7906-4388-917f-fb339d79a456"


def page_ranges_overlap(
    chunk: dict[str, Any],
    evidence: dict[str, Any],
) -> bool:
    """
    Check whether a retrieved chunk overlaps the
    page range of a reference evidence item.

    The documents must also be the same.
    """

    if chunk["document_id"] != evidence["document_id"]:
        return False

    chunk_start = chunk["page_start"]
    chunk_end = chunk["page_end"]

    evidence_start = evidence["page_start"]
    evidence_end = evidence["page_end"]

    return (
        chunk_start <= evidence_end
        and chunk_end >= evidence_start
    )


def resolve_citations(
    citations: list[str],
    retrieved_chunks: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[str],
]:
    """
    Resolve citation IDs using the exact same mapping
    used by the production chat service.

    S1 -> retrieved_chunks[0]
    S2 -> retrieved_chunks[1]
    S3 -> retrieved_chunks[2]
    ...
    """

    source_map = {
        f"S{i + 1}": chunk
        for i, chunk in enumerate(retrieved_chunks)
    }

    resolved_citations = []
    invalid_citations = []

    for source_id in citations:

        chunk = source_map.get(source_id)

        if chunk is None:
            invalid_citations.append(source_id)
            continue

        resolved_citations.append(
            {
                "citation_id": source_id,
                "chunk": chunk,
            }
        )

    return resolved_citations, invalid_citations


def calculate_citation_correctness(
    resolved_citations: list[dict[str, Any]],
    invalid_citations: list[str],
    reference_evidence: list[dict[str, Any]],
) -> float:
    """
    Citation correctness:

    Percentage of model-generated citations that point
    to retrieved chunks whose document and page range
    overlap with at least one reference evidence item.

    Invalid citation IDs are counted as incorrect.
    """

    total_citations = (
        len(resolved_citations)
        + len(invalid_citations)
    )

    if total_citations == 0:
        return 0.0

    correct_citations = 0

    for citation in resolved_citations:

        cited_chunk = citation["chunk"]

        matched = any(
            page_ranges_overlap(
                chunk=cited_chunk,
                evidence=evidence,
            )
            for evidence in reference_evidence
        )

        if matched:
            correct_citations += 1

    return correct_citations / total_citations


def calculate_citation_completeness(
    resolved_citations: list[dict[str, Any]],
    reference_evidence: list[dict[str, Any]],
) -> float:
    """
    Citation completeness:

    Percentage of reference evidence items that are
    covered by at least one model-generated citation.
    """

    if not reference_evidence:
        return 1.0

    if not resolved_citations:
        return 0.0

    cited_chunks = [
        citation["chunk"]
        for citation in resolved_citations
    ]

    covered_evidence = 0

    for evidence in reference_evidence:

        matched = any(
            page_ranges_overlap(
                chunk=chunk,
                evidence=evidence,
            )
            for chunk in cited_chunks
        )

        if matched:
            covered_evidence += 1

    return covered_evidence / len(reference_evidence)


async def citation_eval(eval_user_id: str, limit: int | None = None):

    with open(
        "app/evals/datasets/research_questions.json",
        "r",
        encoding="utf-8",
    ) as f:
        dataset = json.load(f)

    # TEMPORARY: smoke test with one case only
    dataset = dataset[:limit]

    total_correctness = 0.0
    total_completeness = 0.0

    case_results = []

    for case in dataset:

        print("\n" + "=" * 60)
        print(f"Running {case['id']}")
        print(f"Question: {case['question']}")
        print("=" * 60)

        # -----------------------------------------
        # 1. Retrieve context
        # -----------------------------------------

        retrieved_chunks = await retrieve_documents(
            query=case["question"],
            owner_id=eval_user_id,
            document_ids=case["document_ids"],
        )

        print(
            f"\nRetrieved chunks: "
            f"{len(retrieved_chunks)}"
        )

        # -----------------------------------------
        # 2. Generate answer + citations
        # -----------------------------------------

        response = await get_chat_response(
            query=case["question"],
            history=[],
            context=retrieved_chunks,
        )

        print("\nGenerated answer:")
        print(response.answer)

        # -----------------------------------------
        # 3. Resolve S1/S2/S3 citations
        # -----------------------------------------

        citations = response.citations

        print(
            f"\nModel citation IDs: "
            f"{citations}"
        )

        (
            resolved_citations,
            invalid_citations,
        ) = resolve_citations(
            citations=citations,
            retrieved_chunks=retrieved_chunks,
        )

        print(
            f"Resolved citations: "
            f"{len(resolved_citations)}"
        )

        print(
            f"Invalid citations: "
            f"{len(invalid_citations)}"
        )

        if invalid_citations:
            print(
                f"Invalid citation IDs: "
                f"{invalid_citations}"
            )

        # -----------------------------------------
        # 4. Print resolved citations
        # -----------------------------------------

        for citation in resolved_citations:

            citation_id = citation["citation_id"]
            chunk = citation["chunk"]

            print(
                f"\n[{citation_id}] "
                f"chunk_id={chunk['chunk_id']} "
                f"document_id={chunk['document_id']} "
                f"pages="
                f"{chunk['page_start']}-"
                f"{chunk['page_end']}"
            )

        # -----------------------------------------
        # 5. Reference evidence
        # -----------------------------------------

        reference_evidence = case[
            "reference_evidence"
        ]

        print(
            f"\nReference evidence: "
            f"{len(reference_evidence)}"
        )

        for index, evidence in enumerate(
            reference_evidence,
            start=1,
        ):
            print(
                f"\n[Gold {index}] "
                f"document_id={evidence['document_id']} "
                f"pages="
                f"{evidence['page_start']}-"
                f"{evidence['page_end']}"
            )

        # -----------------------------------------
        # 6. Calculate citation correctness
        # -----------------------------------------

        correctness = calculate_citation_correctness(
            resolved_citations=resolved_citations,
            invalid_citations=invalid_citations,
            reference_evidence=reference_evidence,
        )

        # -----------------------------------------
        # 7. Calculate citation completeness
        # -----------------------------------------

        completeness = calculate_citation_completeness(
            resolved_citations=resolved_citations,
            reference_evidence=reference_evidence,
        )

        case_results.append(
            {
                "question_id": case["id"],
                "correctness": correctness,
                "completeness": completeness,
                "total_citations": len(citations),
                "resolved_citations": len(resolved_citations),
                "invalid_citations": len(invalid_citations),
            }
        )

        total_correctness += correctness
        total_completeness += completeness

        # -----------------------------------------
        # 8. Print case results
        # -----------------------------------------

        print(
            f"\nCitation Correctness: "
            f"{correctness:.2f}"
        )

        print(
            f"Citation Completeness: "
            f"{completeness:.2f}"
        )

    # -----------------------------------------
    # 9. Dataset averages
    # -----------------------------------------

    if dataset:

        average_correctness = (
            total_correctness / len(dataset)
        )

        average_completeness = (
            total_completeness / len(dataset)
        )

        print("\n" + "=" * 60)
        print("CITATION EVALUATION SUMMARY")
        print("=" * 60)

        print(
            f"Average Citation Correctness: "
            f"{average_correctness:.2f}"
        )

        print(
            f"Average Citation Completeness: "
            f"{average_completeness:.2f}"
        )
    return {
        "eval_name": "EVAL 4 - Citation Correctness & Completeness",
        "average_correctness": average_correctness if dataset else 0.0,
        "average_completeness": average_completeness if dataset else 0.0,
        "cases": case_results,
    }


if __name__ == "__main__":
    asyncio.run(citation_eval(eval_user_id=""))