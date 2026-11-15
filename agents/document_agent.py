
"""
Document Agent
Multi-Agent Loan Underwriting System.

Responsibilities:
- Extract loan application information.
- Store extracted information in shared memory.
- Validate required application fields.
"""

import json

from agent_framework import Agent

from config import create_openai_client
from shared_memory import shared_memory

from tools import (
    parse_application_fields,
    validate_required_fields,
)


# --------------------------------------------------
# TOOL 1: EXTRACT AND STORE APPLICATION
# --------------------------------------------------

def extract_and_store_application(
    applicant_id: str,
    application_text: str,
) -> str:
    """
    Extract application information and save it in shared memory.

    Parameters:
        applicant_id: Unique applicant identifier.
        application_text: Text containing loan application details.

    Returns:
        JSON string containing extracted information.
    """

    try:
        shared_memory.get_record(applicant_id)

        result = parse_application_fields(application_text)

        if not result["success"]:
            return json.dumps(result)

        extracted_data = result["extracted_data"]

        shared_memory.update_section(
            applicant_id,
            "application",
            extracted_data,
            "Document Agent",
        )

        shared_memory.update_section(
            applicant_id,
            "document_analysis",
            {
                "extraction_status": "COMPLETED",
                "extracted_fields": list(extracted_data.keys()),
            },
            "Document Agent",
        )

        return json.dumps({
            "success": True,
            "applicant_id": applicant_id,
            "extracted_data": extracted_data,
        })

    except Exception as exc:
        return json.dumps({
            "success": False,
            "error": str(exc),
        })


# --------------------------------------------------
# TOOL 2: VALIDATE STORED APPLICATION
# --------------------------------------------------

def validate_stored_application(applicant_id: str) -> str:
    """
    Read applicant information from shared memory,
    validate required fields and save validation results.
    """

    try:
        application = shared_memory.get_section(
            applicant_id,
            "application",
        )

        validation = validate_required_fields(application)

        shared_memory.update_section(
            applicant_id,
            "document_analysis",
            {
                "validation_status": (
                    "VALID" if validation["valid"] else "INVALID"
                ),
                "missing_fields": validation["missing_fields"],
                "validation_errors": validation["errors"],
                "income_missing": validation["income_missing"],
            },
            "Document Agent",
        )

        return json.dumps({
            "applicant_id": applicant_id,
            "validation": validation,
        })

    except Exception as exc:
        return json.dumps({
            "success": False,
            "error": str(exc),
        })


# --------------------------------------------------
# CREATE MICROSOFT AGENT FRAMEWORK AGENT
# --------------------------------------------------

def create_document_agent(client=None):
    """
    Create and return the Document Agent.

    A client can be injected for testing or shared
    with other agents.
    """

    if client is None:
        client = create_openai_client()

    document_agent = Agent(
        client=client,
        name="DocumentAgent",
        instructions="""
You are the Document Agent in a multi-agent loan
underwriting system.

Your responsibilities:

1. Extract applicant information from the supplied
   loan application text.
2. Always call extract_and_store_application first.
3. Always call validate_stored_application after extraction.
4. Never invent missing applicant information.
5. Never assume monthly income.
6. Clearly report missing or invalid fields.
7. Report whether the application is valid.
8. Do not make loan approval or rejection decisions.

You must use your registered Python tools to perform
extraction and validation.

Return a concise structured summary containing:
- Applicant ID
- Extracted applicant information
- Validation status
- Missing fields
- Validation errors
""",
        tools=[
            extract_and_store_application,
            validate_stored_application,
        ],
    )

    return document_agent


# --------------------------------------------------
# STANDALONE EXECUTION
# --------------------------------------------------

if __name__ == "__main__":
    import asyncio

    async def main():
        agent = create_document_agent()

        applicant_id = "DEMO001"

        shared_memory.create_applicant(applicant_id)

        application_text = """
        Applicant Name: Rahul Sharma
        Monthly Income: 65000
        Existing EMI: 5000
        Requested Loan: 800000
        Interest Rate: 10
        Tenure: 60
        """

        result = await agent.run(
            f"""
            Process this loan application.

            Applicant ID: {applicant_id}

            Application:
            {application_text}

            Use both your registered tools.
            """
        )

        print("\nDOCUMENT AGENT RESPONSE")
        print(result.text)

        print("\nSHARED MEMORY")
        print(shared_memory.get_record(applicant_id))

    asyncio.run(main())
