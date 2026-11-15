
import asyncio

from shared_memory import shared_memory
from tools import read_shared_applicant_record
from agents.underwriting_manager import create_underwriting_manager


async def main():

    applicant_id = "APP001"

    # Create applicant record
    shared_memory.create_applicant(applicant_id)

    # Create the complete multi-agent system
    manager = create_underwriting_manager()

    application_text = """
    Applicant Name: Rahul Sharma
    Monthly Income: 65000
    Existing EMI: 5000
    Requested Loan: 800000
    Annual Interest Rate: 10
    Tenure Months: 60
    """

    task = f"""
    Complete the loan underwriting process for applicant {applicant_id}.

    Application details:
    {application_text}

    Follow your complete underwriting workflow.
    Delegate work to all four specialist agents.
    Use their Python tools and shared applicant memory.

    Do not invent any information.
    Save the final decision using write_final_decision.
    """

    print("\nSTARTING REAL MULTI-AGENT UNDERWRITING...\n")

    # Execute the actual OpenAI-powered manager
    result = await manager.run(task)

    print("\nMANAGER RESPONSE")
    print(result.text)

    # Read the actual shared applicant record
    record_result = read_shared_applicant_record(applicant_id)

    print("\nFINAL SHARED APPLICANT RECORD")
    print(record_result)

    record = record_result["record"]

    print("\nFINAL DECISION")
    print(record["final_decision"])

    # Verify specialist agent results
    assert record["document_analysis"], "Document Agent did not save results."
    assert record["emi_analysis"], "EMI Agent did not save results."
    assert record["affordability_analysis"], "Affordability Agent did not save results."
    assert record["credit_analysis"], "Credit Agent did not save results."
    assert record["final_decision"], "Manager did not save final decision."

    print("\nALL FOUR SPECIALIST RESULTS VERIFIED")
    print("FINAL DECISION SAVED SUCCESSFULLY")

    print("\nEND-TO-END WORKFLOW TEST PASSED")


if __name__ == "__main__":
    asyncio.run(main())
