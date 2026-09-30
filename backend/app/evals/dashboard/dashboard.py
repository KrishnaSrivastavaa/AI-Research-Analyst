import asyncio

import streamlit as st

from app.evals.dashboard.dashboard_utils import run_evaluation


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Research Analyst - Eval Dashboard",
    page_icon="🧪",
    layout="wide",
)


# --------------------------------------------------
# Constants
# --------------------------------------------------

EVAL_OPTIONS = [
    "EVAL 1 - Contextual Relevancy",
    "EVAL 2 - Contextual Precision & Recall",
    "EVAL 3 - Faithfulness & Answer Relevancy",
    "EVAL 4 - Citation Correctness & Completeness",
    "EVAL 5 - End-to-End",
]


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def format_score(score):
    if score is None:
        return "—"

    return f"{score * 100:.1f}%"


def render_deepeval_result(result):
    """
    Render EVAL 1, EVAL 2 and EVAL 3.
    """

    metrics = result.get(
        "metrics",
        [],
    )

    cases = result.get(
        "cases",
        [],
    )

    total_cases = result.get(
        "total_cases",
        len(cases),
    )

    if not metrics:
        st.warning(
            "No metric results were returned."
        )
        return

    # --------------------------------------------------
    # Metric overview
    # --------------------------------------------------

    st.subheader("Evaluation Summary")

    for metric in metrics:

        metric_name = metric.get(
            "name",
            "Unknown Metric",
        )

        threshold = metric.get(
            "threshold"
        )

        model = metric.get(
            "model",
            "Unknown",
        )

        average_score = metric.get(
            "average_score"
        )

        pass_rate = metric.get(
            "pass_rate"
        )

        passed = metric.get(
            "passed",
            0,
        )

        failed = metric.get(
            "failed",
            0,
        )

        evaluation_cost = metric.get(
            "evaluation_cost",
            0,
        )

        input_tokens = metric.get(
            "input_tokens",
            0,
        )

        output_tokens = metric.get(
            "output_tokens",
            0,
        )

        # ----------------------------------------------
        # Metric header
        # ----------------------------------------------

        st.markdown(
            f"### {metric_name}"
        )

        st.caption(
            f"Threshold: **{threshold}**  •  "
            f"Judge: **{model}**"
        )

        # ----------------------------------------------
        # Metric cards
        # ----------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Average Score",
                format_score(
                    average_score
                ),
            )

        with col2:

            st.metric(
                "Pass Rate",
                format_score(
                    pass_rate
                ),
            )

        with col3:

            st.metric(
                "Passed",
                passed,
            )

        with col4:

            st.metric(
                "Failed",
                failed,
            )

        # ----------------------------------------------
        # Evaluation metadata
        # ----------------------------------------------

        with st.expander(
            "Evaluation Details"
        ):

            detail_col1, detail_col2, detail_col3 = (
                st.columns(3)
            )

            with detail_col1:

                st.write(
                    "**Evaluation Cost**"
                )

                st.write(
                    f"${evaluation_cost:.6f}"
                )

            with detail_col2:

                st.write(
                    "**Input Tokens**"
                )

                st.write(
                    f"{input_tokens:,}"
                )

            with detail_col3:

                st.write(
                    "**Output Tokens**"
                )

                st.write(
                    f"{output_tokens:,}"
                )

        st.divider()

    # --------------------------------------------------
    # Case results
    # --------------------------------------------------

    st.subheader(
        f"Case Results · {total_cases} cases"
    )

    if not cases:

        st.info(
            "No case results available."
        )

        return

    # ----------------------------------------------
    # Build a compact table
    #
    # Don't dump the potentially huge LLM reasons
    # directly into the main table.
    # ----------------------------------------------

    table_rows = []

    for case in cases:

        row = {
            "Question": case.get(
                "question_id",
                "—",
            )
        }

        for metric in metrics:

            metric_name = metric["name"]

            score = case.get(
                metric_name
            )

            status = case.get(
                f"{metric_name} - Status"
            )

            row[f"{metric_name} Score"] = (
                format_score(score)
            )

            row[f"{metric_name} Status"] = (
                status or "—"
            )

        table_rows.append(row)

    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # Detailed reasoning
    # --------------------------------------------------

    st.subheader(
        "Evaluation Reasoning"
    )

    for case in cases:

        question_id = case.get(
            "question_id",
            "Unknown",
        )

        with st.expander(
            question_id
        ):

            for metric in metrics:

                metric_name = metric["name"]

                score = case.get(
                    metric_name
                )

                status = case.get(
                    f"{metric_name} - Status"
                )

                reason = case.get(
                    f"{metric_name} - Reason"
                )

                st.markdown(
                    f"**{metric_name}**"
                )

                st.write(
                    f"Score: "
                    f"**{format_score(score)}**"
                )

                st.write(
                    f"Status: "
                    f"**{status or '—'}**"
                )

                if reason:

                    st.write(
                        reason
                    )

                st.divider()


def render_citation_result(result):
    """Render EVAL 4."""

    average_correctness = result.get(
        "average_correctness"
    )

    average_completeness = result.get(
        "average_completeness"
    )

    cases = result.get(
        "cases",
        [],
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Citation Correctness",
            format_score(
                average_correctness
            ),
        )

    with col2:

        st.metric(
            "Citation Completeness",
            format_score(
                average_completeness
            ),
        )

    with col3:

        st.metric(
            "Cases Evaluated",
            len(cases),
        )

    st.divider()

    st.subheader("Case Results")

    if not cases:

        st.info(
            "No case results available."
        )

        return

    st.dataframe(
        cases,
        use_container_width=True,
        hide_index=True,
    )


def render_e2e_result(result):
    """Render EVAL 5."""

    total_cases = result.get(
        "total_cases",
        0,
    )

    executed_cases = result.get(
        "executed_cases",
        0,
    )

    passed_cases = result.get(
        "passed_cases",
        0,
    )

    failed_cases = (
        executed_cases - passed_cases
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Cases",
            total_cases,
        )

    with col2:

        st.metric(
            "Executed",
            executed_cases,
        )

    with col3:

        st.metric(
            "Passed",
            passed_cases,
        )

    with col4:

        st.metric(
            "Failed",
            failed_cases,
        )

    st.divider()

    st.subheader("Case Results")

    cases = result.get(
        "cases",
        [],
    )

    if not cases:

        st.info(
            "No case results available."
        )

        return

    st.dataframe(
        cases,
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title(
    "AI Research Analyst"
)

st.caption(
    "Evaluation & Observability Dashboard"
)

st.divider()


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header(
    "Evaluation Configuration"
)

selected_eval = st.sidebar.selectbox(
    "Select evaluation",
    EVAL_OPTIONS,
)


eval_user_id = st.sidebar.text_input(
    "Evaluation User ID",
    type="password",
)


# --------------------------------------------------
# Access token
# --------------------------------------------------

access_token = None

if selected_eval == "EVAL 5 - End-to-End":

    access_token = st.sidebar.text_input(
        "Access Token",
        type="password",
    )

    st.sidebar.caption(
        "Required only for EVAL 5."
    )


# --------------------------------------------------
# Execution mode
# --------------------------------------------------

st.sidebar.subheader(
    "Execution"
)

execution_mode = st.sidebar.radio(
    "Run mode",
    [
        "Smoke Test",
        "Full Dataset",
    ],
)

limit = (
    1
    if execution_mode == "Smoke Test"
    else None
)

if execution_mode == "Smoke Test":

    st.sidebar.caption(
        "Runs 1 evaluation case."
    )

else:

    st.sidebar.caption(
        "Runs the complete evaluation dataset."
    )


st.sidebar.divider()


# --------------------------------------------------
# Run evaluation
# --------------------------------------------------

run_button = st.sidebar.button(
    "Run Evaluation",
    type="primary",
    use_container_width=True,
)


# --------------------------------------------------
# Execute evaluation
# --------------------------------------------------

if run_button:

    if not eval_user_id:

        st.error(
            "Evaluation User ID is required."
        )

        st.stop()

    if (
        selected_eval == "EVAL 5 - End-to-End"
        and not access_token
    ):

        st.error(
            "Access Token is required for EVAL 5."
        )

        st.stop()

    with st.spinner(
        f"Running {selected_eval}..."
    ):

        try:

            result = asyncio.run(
                run_evaluation(
                    eval_name=selected_eval,
                    eval_user_id=eval_user_id,
                    access_token=access_token,
                    limit=limit,
                )
            )

            # ------------------------------------------
            # Store both result and the evaluation that
            # produced it.
            # ------------------------------------------

            st.session_state[
                "eval_result"
            ] = result

            st.session_state[
                "eval_result_name"
            ] = selected_eval

        except Exception as e:

            st.error(
                "Evaluation failed."
            )

            st.exception(e)

            st.stop()


# --------------------------------------------------
# No result
# --------------------------------------------------

if "eval_result" not in st.session_state:

    st.info(
        "Configure an evaluation from the sidebar "
        "and click 'Run Evaluation'."
    )

    st.stop()


# --------------------------------------------------
# Get stored result
# --------------------------------------------------

result = st.session_state[
    "eval_result"
]

result_eval_name = st.session_state.get(
    "eval_result_name"
)


# --------------------------------------------------
# Result guard
# --------------------------------------------------

if result_eval_name != selected_eval:

    st.info(
        f"The latest result is from "
        f"**{result_eval_name}**. "
        f"Click **Run Evaluation** to run "
        f"{selected_eval}."
    )

    st.stop()


# --------------------------------------------------
# Result header
# --------------------------------------------------

st.header(
    result_eval_name
)


# --------------------------------------------------
# EVAL 1
# EVAL 2
# EVAL 3
# --------------------------------------------------

if selected_eval in [
    "EVAL 1 - Contextual Relevancy",
    "EVAL 2 - Contextual Precision & Recall",
    "EVAL 3 - Faithfulness & Answer Relevancy",
]:

    render_deepeval_result(
        result
    )


# --------------------------------------------------
# EVAL 4
# --------------------------------------------------

elif selected_eval == (
    "EVAL 4 - Citation Correctness & Completeness"
):

    render_citation_result(
        result
    )


# --------------------------------------------------
# EVAL 5
# --------------------------------------------------

elif selected_eval == "EVAL 5 - End-to-End":

    render_e2e_result(
        result
    )