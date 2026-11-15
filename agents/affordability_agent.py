
from agent_framework import Agent

from config import create_openai_client
from shared_memory import shared_memory

from tools import (
    calculate_obligation_ratio,
    check_affordability
)


def calculate_and_store_affordability(applicant_id: str) -> dict:
    """
    Calculate the applicant's monthly obligation ratio
    and store the result in shared memory.
    """

    application = shared_memory.get_section(
        applicant_id, "application"
    )

    emi_data = shared_memory.get_section(
        applicant_id, "emi_analysis"
    )

    if not application:
        raise ValueError("Application data not found.")

    if not emi_data or emi_data.get("monthly_emi") is None:
        raise ValueError("Proposed EMI is not available.")

    monthly_income = application.get("monthly_income")
    existing_emi = application.get("existing_emi")

    if monthly_income is None:
        raise ValueError("Monthly income is missing.")

    if existing_emi is None:
        raise ValueError("Existing EMI information is missing.")

    proposed_emi = emi_data["monthly_emi"]

    result = calculate_obligation_ratio(
        monthly_income,
        existing_emi,
        proposed_emi
    )

    shared_memory.update_section(
        applicant_id,
        "affordability_analysis",
        {
            "obligation_details": result,
            "status": "CALCULATED"
        }
    )

    return result


def evaluate_and_store_affordability(applicant_id: str) -> dict:
    """
    Evaluate the calculated obligation ratio against
    the affordability threshold.
    """

    affordability_data = shared_memory.get_section(
        applicant_id,
        "affordability_analysis"
    )

    if not affordability_data:
        raise ValueError(
            "Calculate the obligation ratio first."
        )

    obligation_details = affordability_data.get(
        "obligation_details"
    )

    if not obligation_details:
        raise ValueError("Obligation details are missing.")

    ratio = obligation_details["obligation_ratio"]

    result = check_affordability(ratio)

    shared_memory.update_section(
        applicant_id,
        "affordability_analysis",
        {
            **affordability_data,
            "evaluation": result,
            "evaluation_status": "COMPLETED"
        }
    )

    return result


def create_affordability_agent(client=None):
    """
    Create the Affordability Agent with two Python tools.
    """

    if client is None:
        client = create_openai_client()

    return Agent(
        client=client,
        name="AffordabilityAgent",
        instructions="""
        You are the Affordability Agent in a multi-agent
        loan underwriting system.

        Your responsibilities are:

        1. Read applicant income and existing EMI from shared memory.
        2. Read the proposed EMI calculated by the EMI Agent.
        3. Calculate the total monthly obligation ratio.
        4. Evaluate affordability using the registered Python tools.
        5. Store all results in shared applicant memory.
        6. Never assume or invent missing financial information.
        7. Report missing information instead of making assumptions.

        Use your registered Python tools for all calculations.
        Report the obligation ratio and affordability result.
        """,
        tools=[
            calculate_and_store_affordability,
            evaluate_and_store_affordability
        ]
    )
