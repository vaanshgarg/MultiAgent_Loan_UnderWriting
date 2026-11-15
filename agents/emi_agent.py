
from agent_framework import Agent

from config import create_openai_client
from shared_memory import shared_memory

from tools import (
    calculate_emi,
    generate_repayment_summary
)


def compute_and_store_emi(applicant_id: str) -> dict:
    """
    Calculate the applicant's monthly EMI and store it
    in shared applicant memory.
    """

    application = shared_memory.get_section(
        applicant_id, "application"
    )

    if not application:
        raise ValueError("Application data not found.")

    required_fields = [
        "loan_amount",
        "annual_interest_rate",
        "tenure_months"
    ]

    missing = [
        field for field in required_fields
        if application.get(field) is None
    ]

    if missing:
        raise ValueError(
            f"Missing loan details: {', '.join(missing)}"
        )

    result = calculate_emi(
        application["loan_amount"],
        application["annual_interest_rate"],
        application["tenure_months"]
    )

    shared_memory.update_section(
        applicant_id,
        "emi_analysis",
        {
            **result,
            "status": "COMPLETED"
        }
    )

    return result


def create_repayment_summary(applicant_id: str) -> dict:
    """
    Generate total repayment and total interest summary
    using the EMI calculation stored in shared memory.
    """

    emi_data = shared_memory.get_section(
        applicant_id, "emi_analysis"
    )

    if not emi_data or emi_data.get("monthly_emi") is None:
        raise ValueError(
            "EMI calculation must be completed first."
        )

    summary = generate_repayment_summary(
        emi_data["principal"],
        emi_data["monthly_emi"],
        emi_data["tenure_months"]
    )

    shared_memory.update_section(
        applicant_id,
        "emi_analysis",
        {
            **emi_data,
            "repayment_summary": summary,
            "summary_status": "COMPLETED"
        }
    )

    return summary


def create_emi_agent(client=None):
    """
    Create the EMI Computation Agent with two Python tools.
    """

    if client is None:
        client = create_openai_client()

    return Agent(
        client=client,
        name="EMIComputationAgent",
        instructions="""
        You are the EMI Computation Agent in a multi-agent
        loan underwriting system.

        Your responsibilities are:

        1. Read loan details from shared applicant memory.
        2. Calculate the monthly EMI using compute_and_store_emi.
        3. Generate total repayment and total interest using
           create_repayment_summary.
        4. Ensure both results are stored in shared memory.
        5. Never invent missing loan details.
        6. Report missing information instead of assuming values.

        Always use your registered Python tools for calculations.
        """,
        tools=[
            compute_and_store_emi,
            create_repayment_summary
        ]
    )
