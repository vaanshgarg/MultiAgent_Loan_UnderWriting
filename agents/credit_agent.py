
from agent_framework import Agent

from config import create_openai_client
from shared_memory import shared_memory

from tools import (
    lookup_credit_history,
    evaluate_credit_risk
)


def lookup_and_store_credit_history(applicant_id: str) -> dict:
    """
    Retrieve credit history and store it in shared memory.
    """

    # Retrieve credit records
    history_result = lookup_credit_history(applicant_id)

    # Store retrieved information
    shared_memory.update_section(
        applicant_id,
        "credit_analysis",
        {
            "credit_history": history_result,
            "lookup_status": history_result.get("status")
        }
    )

    return history_result


def evaluate_and_store_credit_risk(applicant_id: str) -> dict:
    """
    Evaluate credit risk using retrieved credit history.
    """

    credit_data = shared_memory.get_section(
        applicant_id,
        "credit_analysis"
    )

    if not credit_data:
        raise ValueError(
            "Credit history must be retrieved first."
        )

    history_result = credit_data.get("credit_history")

    if not history_result:
        raise ValueError("Credit history data is missing.")

    # Evaluate credit risk
    risk_result = evaluate_credit_risk(history_result)

    # Store evaluation
    shared_memory.update_section(
        applicant_id,
        "credit_analysis",
        {
            **credit_data,
            "risk_evaluation": risk_result,
            "evaluation_status": "COMPLETED"
        }
    )

    return risk_result


def create_credit_agent(client=None):
    """
    Create the Credit-History Agent with two Python tools.
    """

    if client is None:
        client = create_openai_client()

    return Agent(
        client=client,
        name="CreditHistoryAgent",
        instructions="""
        You are the Credit-History Agent in a multi-agent
        loan underwriting system.

        Your responsibilities are:

        1. Retrieve the applicant's credit history.
        2. Check previous defaults, late payments and overdue accounts.
        3. Evaluate credit risk using the registered Python tools.
        4. Store credit history and risk evaluation in shared memory.
        5. Report red flags and whether manual review is required.
        6. Never invent credit records or assume missing information.
        7. If records are unavailable, follow the manual-review
           result returned by the Python tools.

        Always use your registered Python tools for credit evaluation.
        """,
        tools=[
            lookup_and_store_credit_history,
            evaluate_and_store_credit_risk
        ]
    )
