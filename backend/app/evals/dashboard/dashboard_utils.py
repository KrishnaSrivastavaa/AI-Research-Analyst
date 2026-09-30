from typing import Any

from app.evals.retrieval_eval import (
    retrieval_eval,
    retrieval_precision_recall,
)
from app.evals.generation_eval import generation_eval
from app.evals.citation_eval import citation_eval
from app.evals.e2e_eval import e2e_eval


# --------------------------------------------------
# DeepEval result normalization
# --------------------------------------------------

def normalize_deepeval_result(
    evaluation_result,
    eval_name: str,
) -> dict[str, Any]:

    test_results = evaluation_result.test_results

    if not test_results:
        return {
            "eval_name": eval_name,
            "metrics": [],
            "cases": [],
            "total_cases": 0,
        }

    # --------------------------------------------------
    # Collect all metric names
    # --------------------------------------------------

    metric_names = []

    for test_result in test_results:
        for metric in test_result.metrics_data:

            if metric.name not in metric_names:
                metric_names.append(metric.name)

    # --------------------------------------------------
    # Build metric summaries
    # --------------------------------------------------

    metrics = []

    for metric_name in metric_names:

        metric_results = []

        for test_result in test_results:

            for metric in test_result.metrics_data:

                if metric.name == metric_name:
                    metric_results.append(metric)

        scores = [
            metric.score
            for metric in metric_results
            if metric.score is not None
        ]

        passed = sum(
            1
            for metric in metric_results
            if metric.success
        )

        failed = len(metric_results) - passed

        average_score = (
            sum(scores) / len(scores)
            if scores
            else None
        )

        pass_rate = (
            passed / len(metric_results)
            if metric_results
            else None
        )

        # DeepEval metric-level metadata can vary slightly
        # by version, so use getattr safely.

        threshold = getattr(
            metric_results[0],
            "threshold",
            None,
        ) if metric_results else None

        model = getattr(
            metric_results[0],
            "model",
            None,
        ) if metric_results else None

        evaluation_cost = sum(
            getattr(metric, "evaluation_cost", 0) or 0
            for metric in metric_results
        )

        input_tokens = sum(
            getattr(metric, "input_tokens", 0) or 0
            for metric in metric_results
        )

        output_tokens = sum(
            getattr(metric, "output_tokens", 0) or 0
            for metric in metric_results
        )

        metrics.append(
            {
                "name": metric_name,
                "threshold": threshold,
                "model": model,
                "average_score": average_score,
                "pass_rate": pass_rate,
                "passed": passed,
                "failed": failed,
                "evaluation_cost": evaluation_cost,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }
        )

    # --------------------------------------------------
    # Build case-level results
    # --------------------------------------------------

    cases = []

    for index, test_result in enumerate(test_results):

        case = {
            "question_id": f"q{index + 1:03d}",
        }

        for metric in test_result.metrics_data:

            case[metric.name] = metric.score

            case[
                f"{metric.name} - Status"
            ] = (
                "Passed"
                if metric.success
                else "Failed"
            )

            case[
                f"{metric.name} - Reason"
            ] = getattr(
                metric,
                "reason",
                None,
            )

        cases.append(case)

    return {
        "eval_name": eval_name,
        "metrics": metrics,
        "cases": cases,
        "total_cases": len(test_results),
    }


# --------------------------------------------------
# Evaluation runner
# --------------------------------------------------

async def run_evaluation(
    eval_name: str,
    eval_user_id: str,
    access_token: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:

    # --------------------------------------------------
    # EVAL 1
    # --------------------------------------------------

    if eval_name == "EVAL 1 - Contextual Relevancy":

        evaluation = await retrieval_eval(
            eval_user_id=eval_user_id,
            limit=limit,
        )

        return normalize_deepeval_result(
            evaluation["result"],
            eval_name,
        )

    # --------------------------------------------------
    # EVAL 2
    # --------------------------------------------------

    if eval_name == "EVAL 2 - Contextual Precision & Recall":

        evaluation = await retrieval_precision_recall(
            eval_user_id=eval_user_id,
            limit=limit,
        )

        return normalize_deepeval_result(
            evaluation["result"],
            eval_name,
        )

    # --------------------------------------------------
    # EVAL 3
    # --------------------------------------------------

    if eval_name == "EVAL 3 - Faithfulness & Answer Relevancy":

        evaluation = await generation_eval(
            eval_user_id=eval_user_id,
            limit=limit,
        )

        return normalize_deepeval_result(
            evaluation["result"],
            eval_name,
        )

    # --------------------------------------------------
    # EVAL 4
    # --------------------------------------------------

    if eval_name == "EVAL 4 - Citation Correctness & Completeness":

        return await citation_eval(
            eval_user_id=eval_user_id,
            limit=limit,
        )

    # --------------------------------------------------
    # EVAL 5
    # --------------------------------------------------

    if eval_name == "EVAL 5 - End-to-End":

        if not access_token:

            raise ValueError(
                "Access token is required for EVAL 5."
            )

        return await e2e_eval(
            eval_user_id=eval_user_id,
            access_token=access_token,
            limit=limit,
        )

    raise ValueError(
        f"Unknown evaluation: {eval_name}"
    )