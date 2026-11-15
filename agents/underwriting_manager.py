
from agent_framework import Agent

from config import create_openai_client
from shared_memory import shared_memory

from tools import (
    read_shared_applicant_record,
    write_final_decision
)

from agents.document_agent import create_document_agent
from agents.emi_agent import create_emi_agent
from agents.affordability_agent import create_affordability_agent
from agents.credit_agent import create_credit_agent


def create_underwriting_manager(client=None):
    """
    Create the Underwriting Manager.

    The manager delegates tasks to four specialist agents
    using Microsoft Agent Framework's agent-as-tool feature.
    """

    if client is None:
        client = create_openai_client()

    # Create all four specialist agents
    document_agent = create_document_agent(client)
    emi_agent = create_emi_agent(client)
    affordability_agent = create_affordability_agent(client)
    credit_agent = create_credit_agent(client)

    # Convert specialist agents into callable tools
    document_tool = document_agent.as_tool(
        name="delegate_to_document_agent",
        description=(
            "Delegate application extraction and document "
            "validation to the Document Agent."
        ),
        arg_name="task",
        arg_description=(
            "Applicant ID and application text. Include all "
            "available application details."
        )
    )

    emi_tool = emi_agent.as_tool(
        name="delegate_to_emi_agent",
        description=(
            "Delegate EMI calculation and repayment summary "
            "generation to the EMI Computation Agent."
        ),
        arg_name="task",
        arg_description="Applicant ID and EMI calculation task."
    )

    affordability_tool = affordability_agent.as_tool(
        name="delegate_to_affordability_agent",
        description=(
            "Delegate obligation ratio calculation and "
            "affordability evaluation."
        ),
        arg_name="task",
        arg_description="Applicant ID and affordability task."
    )

    credit_tool = credit_agent.as_tool(
        name="delegate_to_credit_agent",
        description=(
            "Delegate credit-history lookup and risk evaluation."
        ),
        arg_name="task",
        arg_description="Applicant ID and credit evaluation task."
    )

    # Create the manager agent
    manager = Agent(
        client=client,
        name="UnderwritingManager",

        instructions="""
        You are the Underwriting Manager of a multi-agent
        loan underwriting system.

        You coordinate four specialist agents and produce
        the final loan underwriting decision.

        SHARED MEMORY:
        All agents use the same shared applicant memory.
        Always use the supplied applicant ID.

        REQUIRED WORKFLOW:

        STEP 1: READ APPLICANT RECORD
        - Call read_shared_applicant_record.
        - Confirm that the applicant exists.
        - If the record cannot be found, stop and report the error.

        STEP 2: DOCUMENT VERIFICATION
        - Delegate application extraction to the Document Agent.
        - Delegate document validation to the Document Agent.
        - Verify that required application information is present.
        - Monthly income is mandatory.
        - If monthly income is missing, STOP immediately.
        - Do not calculate EMI or continue underwriting
          when monthly income is missing.
        - Save a REFER decision with a clear explanation.

        STEP 3: EMI COMPUTATION
        - Delegate EMI calculation to the EMI Agent.
        - Ask it to calculate the repayment summary.
        - Use the results stored in shared memory.
        - Never invent loan amounts, interest rates or tenure.

        STEP 4: AFFORDABILITY EVALUATION
        - Delegate obligation ratio calculation to the
          Affordability Agent.
        - Ask it to evaluate affordability.
        - Read the actual evaluation result from shared memory.
        - Never assume the affordability result.

        STEP 5: CREDIT EVALUATION
        - Delegate credit-history lookup and risk evaluation
          to the Credit-History Agent.
        - Read its actual result from shared memory.
        - If credit history is unavailable or manual review
          is required, do not sanction the loan.

        STEP 6: FINAL DECISION
        - Read the complete shared applicant record again.
        - Use the actual EMI, affordability and credit results.
        - SANCTION only when:
            a. Required application information is complete.
            b. EMI has been calculated.
            c. Affordability status is exactly PASS.
            d. Credit status is exactly NO_RECORDED_FLAGS.
            e. No manual review is required.

        - Use DECLINE when a verified underwriting criterion
          fails and the application should not proceed.
        - Use REFER when information is missing, a record
          is unavailable, or manual review is required.

        STEP 7: SAVE FINAL DECISION
        - Always call write_final_decision.
        - Pass the actual monthly EMI or None.
        - Pass the actual affordability and credit statuses.
        - Provide a meaningful justification.
        - Never claim that a decision was saved unless
          the tool confirms success.

        IMPORTANT:
        - Never assume missing monthly income.
        - Never invent financial or credit information.
        - Never bypass specialist agents.
        - Never sanction a loan based on incomplete checks.
        - Do not fabricate results from shared memory.

        FINAL REPORT:
        Provide:
        1. Applicant ID.
        2. Final decision: SANCTION, DECLINE or REFER.
        3. Monthly EMI.
        4. Affordability verdict.
        5. Credit-history verdict.
        6. One-paragraph justification.
        """,

        tools=[
            read_shared_applicant_record,
            document_tool,
            emi_tool,
            affordability_tool,
            credit_tool,
            write_final_decision
        ]
    )

    return manager
