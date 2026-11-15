
from shared_memory import shared_memory

from agents.credit_agent import (
    lookup_and_store_credit_history,
    evaluate_and_store_credit_risk,
    create_credit_agent
)


def test_credit_applicant(applicant_id):

    print(f"\nTesting applicant: {applicant_id}")

    # Create applicant in shared memory
    shared_memory.create_applicant(applicant_id)

    # Tool 1: Retrieve credit history
    history = lookup_and_store_credit_history(
        applicant_id
    )

    print("\nCREDIT HISTORY")
    print(history)

    # Tool 2: Evaluate credit risk
    risk = evaluate_and_store_credit_risk(
        applicant_id
    )

    print("\nCREDIT RISK EVALUATION")
    print(risk)

    # Verify shared memory
    stored_data = shared_memory.get_section(
        applicant_id,
        "credit_analysis"
    )

    assert stored_data is not None
    assert "credit_history" in stored_data
    assert "risk_evaluation" in stored_data

    print("\nShared memory verification: PASSED")

    return risk


# Test 1: Applicant with clean credit history
risk_1 = test_credit_applicant("APP001")

assert risk_1["status"] == "NO_RECORDED_FLAGS"
assert risk_1["manual_review_required"] is False


# Test 2: Applicant with adverse credit history
risk_2 = test_credit_applicant("APP002")

print("\nADVERSE CREDIT TEST")
print(risk_2)

# Verify agent construction
agent = create_credit_agent()

print("\nCredit Agent construction: PASSED")
print("\nALL CREDIT AGENT TESTS PASSED")
